"""3D reconstruction task."""
from app.tasks import celery_app
from app.services.job_service import get_job_service, JobStatus
from app.storage.local import get_job_storage
from app.utils import get_logger

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.reconstruction.reconstruct_3d", bind=True)
def reconstruct_3d(self, preprocessed_path: str, job_id: str):
    """Reconstruct 3D mesh from preprocessed image.

    Uses TripoSR to generate 3D mesh from a single image.

    Args:
        preprocessed_path: Path to preprocessed image
        job_id: Job identifier

    Returns:
        Path to generated mesh file
    """
    job_service = get_job_service()
    job_storage = get_job_storage()

    try:
        # Update status
        job_service.update_status(job_id, JobStatus.RECONSTRUCTING_3D, 50)

        # Load preprocessed image
        image_path = job_storage.get_path(f"{job_id}/{preprocessed_path}")

        if not image_path.exists():
            raise FileNotFoundError(f"Preprocessed image not found: {image_path}")

        logger.info(f"Reconstructing 3D mesh for job {job_id}")

        # Import 3D reconstruction module
        from app.ai.triposr import reconstruct_mesh
        from PIL import Image

        # Load image
        input_image = Image.open(image_path)
        job_service.update_progress(job_id, 55)

        # Reconstruct 3D mesh
        mesh = reconstruct_mesh(input_image)
        job_service.update_progress(job_id, 65)

        # Save mesh as PLY (intermediate format)
        mesh_filename = "raw_mesh.ply"
        save_path = job_storage.get_path(f"{job_id}/{mesh_filename}")
        mesh.export(save_path)

        # Update job
        job_service.set_mesh_path(job_id, mesh_filename)
        job_service.update_progress(job_id, 70)

        logger.info(f"3D mesh saved to {save_path}")

        return mesh_filename

    except Exception as e:
        logger.error(f"3D reconstruction failed for job {job_id}: {str(e)}")
        job_service.set_error(job_id, str(e), "reconstruction")
        raise
