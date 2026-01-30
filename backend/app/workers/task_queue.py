import asyncio
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=2)

# In-memory job store: job_id -> dict
jobs: dict[str, dict] = {}


def create_job(job_id: str, image_path: str, settings: dict) -> dict:
    job = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "stage": None,
        "error": None,
        "image_path": image_path,
        "settings": settings,
        "multi_angle_paths": [],
        "model_path": None,
    }
    jobs[job_id] = job
    return job


def get_job(job_id: str) -> dict | None:
    return jobs.get(job_id)


def update_job(job_id: str, **kwargs):
    if job_id in jobs:
        jobs[job_id].update(kwargs)


async def run_in_thread(fn: Callable, *args) -> Any:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, fn, *args)
