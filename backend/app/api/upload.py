"""Upload API endpoint."""
from flask import Blueprint, request, jsonify

from app.services.upload_service import get_upload_service
from app.services.job_service import get_job_service
from app.utils import ValidationError, get_logger

logger = get_logger(__name__)

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["POST"])
def upload_image():
    """Upload an image and start the processing pipeline.

    Request:
        multipart/form-data with 'image' file field

    Returns:
        JSON with job_id and status
    """
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    upload_service = get_upload_service()
    job_service = get_job_service()

    try:
        # Validate and save the upload
        file_data = upload_service.validate_upload(file, file.filename)
        image_path = upload_service.save_upload(file_data, file.filename)

        # Create job
        job = job_service.create_job(image_path)

        # Start the processing pipeline
        from app.tasks.pipeline import start_pipeline
        start_pipeline.delay(job["id"])

        logger.info(f"Started pipeline for job {job['id']}")

        return jsonify({
            "job_id": job["id"],
            "status": job["status"],
        }), 201

    except ValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        return jsonify({"error": e.message}), 400

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
