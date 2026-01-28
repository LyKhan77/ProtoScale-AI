"""Image preprocessing task."""
from app.tasks import celery_app
from app.services.job_service import get_job_service, JobStatus
from app.storage.local import get_job_storage
from app.utils import get_logger

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.preprocessing.preprocess_image", bind=True)
def preprocess_image(self, multi_angle_paths: list, job_id: str):
    """Preprocess images by removing background.

    Uses rembg to remove background from the front view image
    for 3D reconstruction.

    Args:
        multi_angle_paths: List of generated multi-angle image paths
        job_id: Job identifier

    Returns:
        Path to preprocessed image
    """
    job_service = get_job_service()
    job_storage = get_job_storage()

    try:
        # Update status
        job_service.update_status(job_id, JobStatus.PREPROCESSING, 30)

        # Use the front view (azimuth=0) for 3D reconstruction
        front_view_path = job_storage.get_path(f"{job_id}/angle_0.png")

        if not front_view_path.exists():
            raise FileNotFoundError(f"Front view not found: {front_view_path}")

        logger.info(f"Preprocessing image for job {job_id}")

        # Import background removal module
        from app.ai.background_removal import remove_background
        from PIL import Image

        # Load and process image
        input_image = Image.open(front_view_path)
        job_service.update_progress(job_id, 35)

        # Remove background
        processed_image = remove_background(input_image)
        job_service.update_progress(job_id, 40)

        # Save preprocessed image
        preprocessed_filename = "preprocessed.png"
        save_path = job_storage.get_path(f"{job_id}/{preprocessed_filename}")
        processed_image.save(save_path)

        # Update job
        job_service.set_preprocessed_image(job_id, preprocessed_filename)
        job_service.update_progress(job_id, 45)

        logger.info(f"Preprocessed image saved to {save_path}")

        return preprocessed_filename

    except Exception as e:
        logger.error(f"Preprocessing failed for job {job_id}: {str(e)}")
        job_service.set_error(job_id, str(e), "preprocessing")
        raise
