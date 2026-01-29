#!/usr/bin/env python3
"""
Test script to run 3D reconstruction pipeline stages directly without Celery.

This allows rapid testing and debugging without waiting for the full pipeline.

Usage:
    # Test reconstruction only
    python test_reconstruction.py --job-id <job_id>

    # Test from specific stage
    python test_reconstruction.py --job-id <job_id> --stage reconstruction

    # Test all stages from preprocessing onwards
    python test_reconstruction.py --job-id <job_id> --stage preprocessing
"""
import argparse
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_config
from app.storage.local import get_job_storage
from app.utils import get_logger

logger = get_logger(__name__)


def test_preprocessing(job_id: str):
    """Test preprocessing stage."""
    from app.ai.background_removal import remove_background
    from app.storage.local import get_upload_storage
    from PIL import Image

    logger.info(f"=== Testing PREPROCESSING for job {job_id} ===")

    upload_storage = get_upload_storage()
    job_storage = get_job_storage()

    # Find uploaded image
    upload_files = list(upload_storage.base_dir.glob("*.png")) + \
                   list(upload_storage.base_dir.glob("*.jpg"))

    if not upload_files:
        logger.error("No uploaded images found")
        return None

    image_path = upload_files[-1]  # Use latest
    logger.info(f"Using image: {image_path}")

    # Load and process
    image = Image.open(image_path)
    processed = remove_background(image)

    # Save
    output_path = job_storage.get_path(f"{job_id}/preprocessed.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    processed.save(output_path)

    logger.info(f"Preprocessed image saved to: {output_path}")
    return str(output_path)


def test_reconstruction(job_id: str):
    """Test 3D reconstruction stage."""
    from app.ai.triposr import reconstruct_mesh
    from PIL import Image

    logger.info(f"=== Testing 3D RECONSTRUCTION for job {job_id} ===")

    job_storage = get_job_storage()

    # Load preprocessed image
    preprocessed_path = job_storage.get_path(f"{job_id}/preprocessed.png")

    if not preprocessed_path.exists():
        logger.error(f"Preprocessed image not found: {preprocessed_path}")
        logger.info("Run with --stage preprocessing first")
        return None

    logger.info(f"Loading image from: {preprocessed_path}")
    image = Image.open(preprocessed_path)

    # Reconstruct
    logger.info("Starting reconstruction (this may take a few minutes)...")
    mesh = reconstruct_mesh(image)

    # Save
    output_path = job_storage.get_path(f"{job_id}/raw_mesh.ply")
    mesh.export(output_path)

    logger.info(f"Raw mesh saved to: {output_path}")
    logger.info(f"Mesh stats: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
    return str(output_path)


def test_mesh_repair(job_id: str):
    """Test mesh repair stage."""
    from app.mesh.validator import MeshValidator
    from app.mesh.repair import MeshRepairer
    import trimesh

    logger.info(f"=== Testing MESH REPAIR for job {job_id} ===")

    job_storage = get_job_storage()

    # Load raw mesh
    raw_mesh_path = job_storage.get_path(f"{job_id}/raw_mesh.ply")

    if not raw_mesh_path.exists():
        logger.error(f"Raw mesh not found: {raw_mesh_path}")
        logger.info("Run with --stage reconstruction first")
        return None

    logger.info(f"Loading mesh from: {raw_mesh_path}")
    mesh = trimesh.load(raw_mesh_path)

    # Validate
    validator = MeshValidator()
    logger.info("Running initial validation...")
    initial_validation = validator.validate(mesh)
    logger.info(f"Initial validation: {initial_validation}")

    # Repair
    logger.info("Repairing mesh...")
    repairer = MeshRepairer()
    repaired_mesh = repairer.repair(mesh)

    # Validate again
    logger.info("Running final validation...")
    final_validation = validator.validate(repaired_mesh)
    logger.info(f"Final validation: {final_validation}")

    # Save
    output_path = job_storage.get_path(f"{job_id}/repaired_mesh.ply")
    repaired_mesh.export(output_path)

    logger.info(f"Repaired mesh saved to: {output_path}")
    logger.info(f"Mesh stats: {len(repaired_mesh.vertices)} vertices, {len(repaired_mesh.faces)} faces")
    return str(output_path)


def test_export(job_id: str):
    """Test export stage."""
    from app.mesh.converter import MeshConverter
    import trimesh

    logger.info(f"=== Testing EXPORT for job {job_id} ===")

    job_storage = get_job_storage()

    # Load repaired mesh
    repaired_mesh_path = job_storage.get_path(f"{job_id}/repaired_mesh.ply")

    if not repaired_mesh_path.exists():
        logger.error(f"Repaired mesh not found: {repaired_mesh_path}")
        logger.info("Run with --stage mesh_repair first")
        return None

    logger.info(f"Loading mesh from: {repaired_mesh_path}")
    mesh = trimesh.load(repaired_mesh_path)

    # Export
    converter = MeshConverter()
    export_storage = job_storage.get_path(f"{job_id}")

    logger.info("Exporting to STL...")
    stl_path = converter.to_stl(mesh, export_storage / "model.stl")
    logger.info(f"STL saved to: {stl_path}")

    logger.info("Exporting to OBJ...")
    obj_path = converter.to_obj(mesh, export_storage / "model.obj")
    logger.info(f"OBJ saved to: {obj_path}")

    return {"stl": str(stl_path), "obj": str(obj_path)}


def main():
    parser = argparse.ArgumentParser(description="Test pipeline stages directly")
    parser.add_argument("--job-id", required=True, help="Job ID to process")
    parser.add_argument(
        "--stage",
        choices=["preprocessing", "reconstruction", "mesh_repair", "export", "all"],
        default="reconstruction",
        help="Stage to test (default: reconstruction)"
    )

    args = parser.parse_args()

    logger.info(f"Starting test for job {args.job_id}, stage: {args.stage}")

    try:
        if args.stage == "preprocessing" or args.stage == "all":
            test_preprocessing(args.job_id)

        if args.stage == "reconstruction" or args.stage == "all":
            test_reconstruction(args.job_id)

        if args.stage == "mesh_repair" or args.stage == "all":
            test_mesh_repair(args.job_id)

        if args.stage == "export" or args.stage == "all":
            test_export(args.job_id)

        logger.info("=== TEST COMPLETED ===")

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
