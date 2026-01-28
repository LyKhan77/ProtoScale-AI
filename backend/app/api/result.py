"""Result API endpoint."""
from flask import Blueprint, jsonify

from app.services.result_service import get_result_service
from app.utils import NotFoundError, get_logger

logger = get_logger(__name__)

result_bp = Blueprint("result", __name__)


@result_bp.route("/result/<job_id>", methods=["GET"])
def get_result(job_id: str):
    """Get complete job result with all outputs.

    Args:
        job_id: Job identifier

    Returns:
        JSON with multi_angle_images, preview_obj, stl_download_url, analysis_data
    """
    result_service = get_result_service()

    try:
        result = result_service.get_result(job_id)
        return jsonify(result), 200

    except NotFoundError as e:
        return jsonify({"error": e.message}), 404

    except Exception as e:
        logger.error(f"Error getting result for job {job_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
