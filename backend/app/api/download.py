"""Download API endpoint."""
from flask import Blueprint, jsonify, send_file

from app.services.result_service import get_result_service
from app.utils import NotFoundError, get_logger

logger = get_logger(__name__)

download_bp = Blueprint("download", __name__)


@download_bp.route("/download/<job_id>/<format>", methods=["GET"])
def download_file(job_id: str, format: str):
    """Download generated file.

    Args:
        job_id: Job identifier
        format: File format (stl or obj)

    Returns:
        Binary file download
    """
    if format not in ("stl", "obj"):
        return jsonify({"error": "Invalid format. Use 'stl' or 'obj'"}), 400

    result_service = get_result_service()

    try:
        file_path = result_service.get_download_path(job_id, format)

        mime_types = {
            "stl": "application/sla",
            "obj": "text/plain",
        }

        return send_file(
            file_path,
            mimetype=mime_types.get(format, "application/octet-stream"),
            as_attachment=True,
            download_name=f"model_{job_id[:8]}.{format}"
        )

    except NotFoundError as e:
        return jsonify({"error": e.message}), 404

    except Exception as e:
        logger.error(f"Error downloading {format} for job {job_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
