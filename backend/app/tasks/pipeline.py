"""Pipeline orchestration task."""
from celery import chain

from app.tasks import celery_app
from app.services.job_service import get_job_service, JobStatus
from app.utils import get_logger

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.pipeline.start_pipeline", bind=True)
def start_pipeline(self, job_id: str):
    """Start the complete processing pipeline for a job.

    Pipeline stages:
    1. Preprocessing / Background removal (CPU)
    2. 3D Reconstruction (GPU)
    3. Render Multi-Angle Previews (CPU)
    4. Mesh repair (CPU)
    5. Export to STL/OBJ (CPU)

    Args:
        job_id: Job identifier
    """
    from app.tasks.preprocessing import preprocess_image
    from app.tasks.reconstruction import reconstruct_3d
    from app.tasks.triposr_pipeline import render_previews
    from app.tasks.mesh_repair import repair_mesh
    from app.tasks.export import export_mesh

    job_service = get_job_service()
    job = job_service.get_job(job_id)

    if not job:
        logger.error(f"Job {job_id} not found")
        return {"error": "Job not found"}

    logger.info(f"Starting TripoSR-only pipeline for job {job_id}")

    # Create task chain
    # First task uses si() (immutable) since it has no previous result
    # Subsequent tasks use s(job_id) and receive previous result as first arg
    pipeline = chain(
        preprocess_image.si(job_id),
        reconstruct_3d.s(job_id),
        render_previews.s(job_id),
        repair_mesh.s(job_id),
        export_mesh.s(job_id),
    )

    # Execute the chain
    try:
        pipeline.apply_async()
        return {"job_id": job_id, "status": "pipeline_started"}
    except Exception as e:
        logger.error(f"Failed to start pipeline for job {job_id}: {str(e)}")
        job_service.set_error(job_id, str(e), "pipeline_start")
        return {"error": str(e)}
