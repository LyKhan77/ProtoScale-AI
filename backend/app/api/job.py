"""Job status API endpoint."""
from flask import Blueprint, jsonify

from app.services.job_service import get_job_service
from app.utils import get_logger

logger = get_logger(__name__)

job_bp = Blueprint("job", __name__)


@job_bp.route("/job/<job_id>", methods=["GET"])
def get_job_status(job_id: str):
    """Get job status and progress.

    Args:
        job_id: Job identifier

    Returns:
        JSON with status, progress, and optional error info
    """
    job_service = get_job_service()
    job = job_service.get_job(job_id)

    if not job:
        return jsonify({"error": "Job not found"}), 404

    response = {
        "job_id": job["id"],
        "status": job["status"],
        "progress": job["progress"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
    }

    # Add error info if present
    if job.get("error_message"):
        response["error_message"] = job["error_message"]
    if job.get("error_stage"):
        response["error_stage"] = job["error_stage"]

    return jsonify(response), 200
