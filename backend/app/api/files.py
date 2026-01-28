"""File serving API endpoint."""
from flask import Blueprint, jsonify, send_file
from pathlib import Path

from app.storage.local import get_job_storage, get_export_storage
from app.utils import get_logger

logger = get_logger(__name__)

files_bp = Blueprint("files", __name__)


@files_bp.route("/files/jobs/<job_id>/<filename>", methods=["GET"])
def serve_job_file(job_id: str, filename: str):
    """Serve a file from job storage.

    Args:
        job_id: Job identifier
        filename: File name to serve

    Returns:
        Binary file
    """
    job_storage = get_job_storage()

    file_path = job_storage.get_path(f"{job_id}/{filename}")

    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404

    # Determine mime type based on extension
    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".obj": "text/plain",
        ".ply": "application/octet-stream",
    }

    ext = Path(filename).suffix.lower()
    mime_type = mime_types.get(ext, "application/octet-stream")

    return send_file(file_path, mimetype=mime_type)


@files_bp.route("/files/exports/<job_id>/<filename>", methods=["GET"])
def serve_export_file(job_id: str, filename: str):
    """Serve a file from export storage.

    Args:
        job_id: Job identifier
        filename: File name to serve

    Returns:
        Binary file
    """
    export_storage = get_export_storage()

    file_path = export_storage.get_path(f"{job_id}/{filename}")

    if not file_path.exists():
        return jsonify({"error": "File not found"}), 404

    # Determine mime type based on extension
    mime_types = {
        ".stl": "application/sla",
        ".obj": "text/plain",
        ".ply": "application/octet-stream",
    }

    ext = Path(filename).suffix.lower()
    mime_type = mime_types.get(ext, "application/octet-stream")

    return send_file(file_path, mimetype=mime_type)
