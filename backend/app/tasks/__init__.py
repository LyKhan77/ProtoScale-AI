"""Celery task configuration."""
from celery import Celery

from app.config import get_config

config = get_config()

celery_app = Celery(
    "3d_miniature",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.pipeline",
        "app.tasks.multi_angle",
        "app.tasks.preprocessing",
        "app.tasks.reconstruction",
        "app.tasks.mesh_repair",
        "app.tasks.export",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing - GPU tasks to gpu queue, CPU tasks to cpu queue
    task_routes={
        "app.tasks.multi_angle.*": {"queue": "gpu"},
        "app.tasks.reconstruction.*": {"queue": "gpu"},
        "app.tasks.preprocessing.*": {"queue": "cpu"},
        "app.tasks.mesh_repair.*": {"queue": "cpu"},
        "app.tasks.export.*": {"queue": "cpu"},
        "app.tasks.pipeline.*": {"queue": "cpu"},
    },

    # Prevent GPU tasks from being prefetched
    worker_prefetch_multiplier=1,

    # Task serialization
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task result expiration
    result_expires=86400,  # 24 hours

    # Task acknowledgement
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Retry policy
    task_default_retry_delay=30,
    task_max_retries=3,
)
