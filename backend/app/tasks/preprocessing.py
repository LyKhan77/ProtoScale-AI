"""Image preprocessing task."""
from app.tasks import celery_app
from app.services.job_service import get_job_service, JobStatus
from app.storage.local import get_upload_storage, get_job_storage
from app.utils import get_logger

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.preprocessing.preprocess_image", bind=True)
def preprocess_image(self, job_id: str):
    """Preprocess images by removing background.

    Uses rembg to remove background from the uploaded image
    for 3D reconstruction.

    Args:
        job_id: Job identifier

    Returns:
        Path to preprocessed image
    """
    job_service = get_job_service()
    upload_storage = get_upload_storage()
    job_storage = get_job_storage()

    try:
        # Update status
        job_service.update_status(job_id, JobStatus.PREPROCESSING, 0)

        job = job_service.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Read uploaded image directly
        image_path = upload_storage.get_path(job["image_path"])

        if not image_path.exists():
            raise FileNotFoundError(f"Uploaded image not found: {image_path}")

        logger.info(f"Preprocessing image for job {job_id}")

        # Import background removal module
        from app.ai.background_removal import remove_background
        from PIL import Image

        # Load and process image
        input_image = Image.open(image_path)
        job_service.update_progress(job_id, 10)

        # Remove background
        processed_image = remove_background(input_image)
        job_service.update_progress(job_id, 15)

        # Save preprocessed image
        preprocessed_filename = "preprocessed.png"
        save_path = job_storage.get_path(f"{job_id}/{preprocessed_filename}")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        processed_image.save(save_path)

        # Update job
        job_service.set_preprocessed_image(job_id, preprocessed_filename)
        job_service.update_progress(job_id, 20)

        logger.info(f"Preprocessed image saved to {save_path}")

        return preprocessed_filename

    except Exception as e:
        logger.error(f"Preprocessing failed for job {job_id}: {str(e)}")
        job_service.set_error(job_id, str(e), "preprocessing")
        raise
