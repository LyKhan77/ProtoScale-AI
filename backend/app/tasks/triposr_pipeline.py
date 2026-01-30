"""
TripoSR-Only Pipeline Tasks for ProtoScale.

Fast 3D reconstruction pipeline using TripoSR only.
Optimized for speed and loose tolerances.
"""
from app.tasks import celery_app
from app.services.job_service import get_job_service, JobStatus
from app.storage.local import get_job_storage
from app.utils import get_logger

logger = get_logger(__name__)


@celery_app.task(
    name="app.tasks.triposr_pipeline.render_previews",
    bind=True,
    max_retries=2
)
def render_previews(self, mesh_path: str, job_id: str):
    """Render 2D multi-angle previews from 3D mesh.

    Args:
        mesh_path: Path to generated GLB/PLY mesh file
        job_id: Job identifier

    Returns:
        list: List of preview image filenames
    """
    job_service = get_job_service()
    job_storage = get_job_storage()

    try:
        # Update status
        job_service.update_status(job_id, JobStatus.RENDERING_PREVIEWS, 60)

        # Load mesh
        mesh_file = job_storage.get_path(f"{job_id}/{mesh_path}")

        if not mesh_file.exists():
            raise FileNotFoundError(f"Mesh file not found: {mesh_file}")

        import trimesh
        mesh = trimesh.load(mesh_file)

        job_service.update_progress(job_id, 65)

        # Render previews
        from app.ai.triposr_renderer import render_multi_angle_previews

        logger.info(f"Rendering preview angles for job {job_id}")
        preview_images = render_multi_angle_previews(
            mesh,
            angles=[0, 90, 180, 270],
            image_size=(512, 512)
        )

        job_service.update_progress(job_id, 70)

        # Save preview images
        image_paths = []
        for i, (angle, img) in enumerate(zip([0, 90, 180, 270], preview_images)):
            filename = f"angle_{angle}.png"
            save_path = job_storage.get_path(f"{job_id}/{filename}")
            save_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(save_path)
            image_paths.append(filename)
            logger.info(f"Saved preview angle {angle} to {save_path}")

        # Update job with image paths
        job_service.set_multi_angle_images(job_id, image_paths)
        job_service.update_progress(job_id, 75)

        logger.info(f"Generated {len(image_paths)} preview images for job {job_id}")

        return image_paths

    except Exception as e:
        logger.error(f"Preview rendering failed for job {job_id}: {str(e)}")
        job_service.set_error(job_id, str(e), "preview_rendering")
        raise
