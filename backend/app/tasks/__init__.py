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
        "app.tasks.preprocessing",
        "app.tasks.reconstruction",
        "app.tasks.triposr_pipeline",
        "app.tasks.mesh_repair",
        "app.tasks.export",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    # GPU queue: AI inference tasks (rembg U2Net + TripoSR)
    # CPU queue: pure numpy/trimesh operations (no GPU benefit)
    #
    # RTX 4090 24GB budget:
    #   rembg U2Net:  ~200MB VRAM
    #   TripoSR:      ~6GB VRAM
    #   Peak total:   ~6.2GB / 24GB (26%)
    task_routes={
        "app.tasks.preprocessing.*": {"queue": "gpu"},
        "app.tasks.reconstruction.*": {"queue": "gpu"},
        "app.tasks.triposr_pipeline.*": {"queue": "cpu"},
        "app.tasks.mesh_repair.*": {"queue": "cpu"},
        "app.tasks.export.*": {"queue": "cpu"},
        "app.tasks.pipeline.*": {"queue": "cpu"},
    },

    # GPU worker: concurrency=1 to avoid VRAM contention
    # (TripoSR singleton model moves to/from GPU per job)
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

    # Redis broker visibility timeout - must be longer than longest task
    # TripoSR pipeline: ~5-10s per job, 10 min timeout is generous
    broker_transport_options={
        "visibility_timeout": 600,  # 10 minutes
    },

    # Task acknowledgement - ack early to prevent re-delivery
    task_acks_late=False,

    # Retry policy
    task_default_retry_delay=30,
    task_max_retries=3,
)
