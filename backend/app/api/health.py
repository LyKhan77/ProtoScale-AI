"""Health check API endpoint."""
import torch
from flask import Blueprint, jsonify

from app.extensions import get_redis
from app.utils import get_logger

logger = get_logger(__name__)

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint.

    Returns:
        JSON with status, gpu availability, and redis connection
    """
    health = {
        "status": "healthy",
        "gpu": {
            "available": False,
            "device": None,
        },
        "redis": {
            "connected": False,
        },
    }

    # Check GPU
    try:
        if torch.cuda.is_available():
            health["gpu"]["available"] = True
            health["gpu"]["device"] = torch.cuda.get_device_name(0)
            health["gpu"]["memory_allocated"] = f"{torch.cuda.memory_allocated(0) / 1024**3:.2f}GB"
            health["gpu"]["memory_total"] = f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f}GB"
        elif torch.backends.mps.is_available():
            health["gpu"]["available"] = True
            health["gpu"]["device"] = "Apple MPS"
    except Exception as e:
        logger.warning(f"GPU check failed: {str(e)}")

    # Check Redis
    try:
        redis = get_redis()
        redis.ping()
        health["redis"]["connected"] = True
    except Exception as e:
        logger.warning(f"Redis check failed: {str(e)}")
        health["status"] = "degraded"

    status_code = 200 if health["status"] == "healthy" else 503

    return jsonify(health), status_code
