"""Mesh repair task."""
from app.tasks import celery_app
from app.services.job_service import get_job_service, JobStatus
from app.storage.local import get_job_storage
from app.utils import get_logger

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.mesh_repair.repair_mesh", bind=True)
def repair_mesh(self, mesh_path: str, job_id: str):
    """Repair mesh for FDM 3D printing.

    Performs validation and repair operations:
    - Check/fix watertight
    - Check/fix manifold
    - Fix normals
    - Remove degenerate faces
    - Fill holes

    Args:
        mesh_path: Path to raw mesh file
        job_id: Job identifier

    Returns:
        Path to repaired mesh file
    """
    job_service = get_job_service()
    job_storage = get_job_storage()

    try:
        # Update status
        job_service.update_status(job_id, JobStatus.MESH_REPAIRING, 75)

        # Load mesh
        input_path = job_storage.get_path(f"{job_id}/{mesh_path}")

        if not input_path.exists():
            raise FileNotFoundError(f"Mesh not found: {input_path}")

        logger.info(f"Repairing mesh for job {job_id}")

        # Import mesh processing modules
        from app.mesh.validator import MeshValidator
        from app.mesh.repair import MeshRepairer
        import trimesh

        # Load mesh
        mesh = trimesh.load(input_path)
        job_service.update_progress(job_id, 78)

        # Validate mesh
        validator = MeshValidator()
        validation_result = validator.validate(mesh)
        logger.info(f"Initial validation: {validation_result}")

        job_service.update_progress(job_id, 80)

        # Repair mesh if needed
        repairer = MeshRepairer()
        repaired_mesh = repairer.repair(mesh)

        job_service.update_progress(job_id, 85)

        # Validate repaired mesh
        final_validation = validator.validate(repaired_mesh)
        logger.info(f"Final validation: {final_validation}")

        # Save repaired mesh
        repaired_filename = "repaired_mesh.ply"
        save_path = job_storage.get_path(f"{job_id}/{repaired_filename}")
        repaired_mesh.export(save_path)

        job_service.update_progress(job_id, 88)

        logger.info(f"Repaired mesh saved to {save_path}")

        return {
            "mesh_path": repaired_filename,
            "validation": final_validation,
        }

    except Exception as e:
        logger.error(f"Mesh repair failed for job {job_id}: {str(e)}")
        job_service.set_error(job_id, str(e), "mesh_repair")
        raise
