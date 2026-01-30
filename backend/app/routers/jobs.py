import uuid
import logging
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

from app.config import UPLOADS_DIR, OUTPUTS_DIR
from app.models.schemas import JobCreatedResponse, JobStatusResponse, JobStatus, JobListItem
from app.workers.task_queue import create_job, get_job, update_job, run_in_thread
from app.services.image_processor import remove_background
from app.services.hunyuan import generate_3d

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["jobs"])


@router.post("/upload", response_model=JobCreatedResponse)
async def upload_image(
    file: UploadFile = File(...),
    remove_bg: bool = Form(True),
    enhanced_detail: bool = Form(False),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Only image files are accepted")

    job_id = str(uuid.uuid4())
    job_dir = UPLOADS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "image.png").suffix or ".png"
    raw_path = str(job_dir / f"original{ext}")

    with open(raw_path, "wb") as f:
        content = await file.read()
        f.write(content)

    image_path = raw_path

    # Background removal if requested
    if remove_bg:
        try:
            nobg_path = str(job_dir / "nobg.png")
            result_path = await run_in_thread(remove_background, raw_path, nobg_path)
            image_path = result_path
        except Exception as e:
            logger.warning(f"Background removal failed, using original: {e}")

    create_job(job_id, image_path, {
        "remove_bg": remove_bg,
        "enhanced_detail": enhanced_detail,
    })

    return JobCreatedResponse(job_id=job_id)


@router.post("/jobs/{job_id}/generate-3d", response_model=JobStatusResponse)
async def trigger_3d(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    update_job(job_id, status="processing", stage="3d_generation", progress=0)

    async def _run():
        try:
            await run_in_thread(generate_3d, job_id, job["image_path"])
            update_job(job_id, status="completed", stage="3d_generation")
        except Exception as e:
            logger.error(f"3D generation failed for {job_id}: {e}")
            update_job(job_id, status="failed", error=str(e))

    import asyncio
    asyncio.create_task(_run())

    return _job_status(job_id)


@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return _job_status(job_id)


@router.get("/jobs/{job_id}/result/{asset}")
async def job_result(job_id: str, asset: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")

    if asset == "model.glb":
        model_path = job.get("model_path")
        if not model_path or not Path(model_path).exists():
            raise HTTPException(404, "Model not ready")
        return FileResponse(model_path, media_type="model/gltf-binary", filename="model.glb")

    raise HTTPException(400, f"Unknown asset: {asset}")


@router.get("/jobs", response_model=list[JobListItem])
async def list_jobs():
    items = []
    if OUTPUTS_DIR.exists():
        for d in OUTPUTS_DIR.iterdir():
            if not d.is_dir():
                continue
            glb = d / "model.glb"
            has_model = glb.exists()
            if not has_model:
                continue
            created_at = datetime.fromtimestamp(glb.stat().st_mtime).isoformat()
            items.append(JobListItem(job_id=d.name, has_model=True, created_at=created_at))
    items.sort(key=lambda x: x.created_at, reverse=True)
    return items


@router.get("/jobs/{job_id}/thumbnail")
async def job_thumbnail(job_id: str):
    upload_dir = UPLOADS_DIR / job_id
    if not upload_dir.exists():
        raise HTTPException(404, "Job not found")
    nobg = upload_dir / "nobg.png"
    if nobg.exists():
        return FileResponse(nobg, media_type="image/png")
    for f in upload_dir.iterdir():
        if f.name.startswith("original"):
            media = "image/png" if f.suffix == ".png" else "image/jpeg"
            return FileResponse(f, media_type=media)
    raise HTTPException(404, "No thumbnail found")


def _job_status(job_id: str) -> JobStatusResponse:
    job = get_job(job_id)
    return JobStatusResponse(
        job_id=job["job_id"],
        status=JobStatus(job["status"]),
        progress=job.get("progress", 0),
        stage=job.get("stage"),
        error=job.get("error"),
    )
