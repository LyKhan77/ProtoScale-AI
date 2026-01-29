"""Multi-angle image generation task."""
from app.tasks import celery_app
from app.services.job_service import get_job_service, JobStatus
from app.storage.local import get_upload_storage, get_job_storage
from app.utils import get_logger

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.multi_angle.generate_multi_angles", bind=True)
def generate_multi_angles(self, job_id: str):
    """Generate multi-angle views of the uploaded image.

    Uses Qwen Image Edit with Multiple Angles LoRA to generate
    front, right, back, and left views.

    Args:
        previous_result: Result from previous task (or None if first)
        job_id: Job identifier

    Returns:
        List of generated image paths
    """
    job_service = get_job_service()
    upload_storage = get_upload_storage()
    job_storage = get_job_storage()

    try:
        # Update status
        job_service.update_status(job_id, JobStatus.GENERATING_MULTI_ANGLES, 5)

        job = job_service.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Load the uploaded image
        image_path = upload_storage.get_path(job["image_path"])
        logger.info(f"Generating multi-angles for job {job_id} from {image_path}")

        # Import AI module
        from app.ai.qwen_multi_angle import generate_multi_angle_views
        import torch

        # Generate views at different azimuths
        job_service.update_progress(job_id, 10)

        from PIL import Image
        input_image = Image.open(image_path)

        # Generate multi-angle images
        azimuths = [0, 90, 180, 270]  # front, right, back, left
        generated_images = generate_multi_angle_views(input_image, azimuths)

        # Free GPU memory after generation
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("GPU memory cleared after multi-angle generation")

        job_service.update_progress(job_id, 20)

        # Save generated images
        image_paths = []
        for i, (azimuth, img) in enumerate(zip(azimuths, generated_images)):
            filename = f"angle_{azimuth}.png"
            save_path = job_storage.get_path(f"{job_id}/{filename}")
            save_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(save_path)
            image_paths.append(filename)
            logger.info(f"Saved angle {azimuth} to {save_path}")

        # Update job with image paths
        job_service.set_multi_angle_images(job_id, image_paths)
        job_service.update_progress(job_id, 25)

        logger.info(f"Generated {len(image_paths)} multi-angle images for job {job_id}")

        return image_paths

    except Exception as e:
        logger.error(f"Multi-angle generation failed for job {job_id}: {str(e)}")
        job_service.set_error(job_id, str(e), "multi_angle_generation")
        raise
