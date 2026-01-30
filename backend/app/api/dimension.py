"""
Dimension update API endpoints.

Handle mesh scaling and export with custom dimensions.
"""
from flask import Blueprint, request, jsonify, send_file
from pathlib import Path
import trimesh

from app.services.job_service import get_job_service
from app.storage.local import get_job_storage
from app.utils import get_logger

logger = get_logger(__name__)

# Create blueprint
dimension_bp = Blueprint('dimension', __name__, url_prefix='/dimension')


@dimension_bp.route('/update/<job_id>', methods=['POST'])
def update_dimension(job_id: str):
    """Update mesh dimensions and export scaled STL.

    Args:
        job_id: Job identifier

    Request JSON:
        {
            "scale": {"x": 1.0, "y": 1.0, "z": 1.0}  # Per-axis scale factors
        }

    Returns:
        JSON with download URL:
        {
            "download_url": "/download/<job_id>/stl_scaled",
            "scale": {"x": 1.0, "y": 1.0, "z": 1.0}
        }
    """
    job_service = get_job_service()
    job_storage = get_job_storage()

    try:
        # Get job
        job = job_service.get_job(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404

        # Get scale factors from request
        data = request.get_json()
        scale = data.get('scale', {'x': 1.0, 'y': 1.0, 'z': 1.0})

        # Validate scale factors
        if not all(k in scale for k in ['x', 'y', 'z']):
            return jsonify({"error": "Invalid scale format. Required: x, y, z"}), 400

        logger.info(f"Scaling mesh for job {job_id}: {scale}")

        # Get mesh path
        mesh_path = job.get('mesh_path')
        if not mesh_path:
            return jsonify({"error": "Mesh not found for this job"}), 404

        # Load mesh
        mesh_file = job_storage.get_path(f"{job_id}/{mesh_path}")
        if not mesh_file.exists():
            return jsonify({"error": "Mesh file not found"}), 404

        mesh = trimesh.load(mesh_file)

        # Apply scaling
        mesh.apply_scale([scale['x'], scale['y'], scale['z']])

        # Save scaled mesh
        scaled_filename = f"scaled_mesh_{scale['x']:.2f}x_{scale['y']:.2f}x_{scale['z']:.2f}x.stl"
        scaled_path = job_storage.get_path(f"{job_id}/{scaled_filename}")

        mesh.export(scaled_path)

        logger.info(f"Scaled mesh saved to {scaled_path}")

        # Return download URL
        download_url = f"/api/download/{job_id}/{scaled_filename}"

        return jsonify({
            "download_url": download_url,
            "scale": scale,
            "filename": scaled_filename
        })

    except Exception as e:
        logger.error(f"Failed to update dimension for job {job_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500


@dimension_bp.route('/validate/<job_id>', methods=['POST'])
def validate_dimension(job_id: str):
    """Validate proposed dimension changes.

    Args:
        job_id: Job identifier

    Request JSON:
        {
            "dimensions": {"x": 50.0, "y": 30.0, "z": 12.5}  # Target dimensions in mm
        }

    Returns:
        JSON with calculated scale factors:
        {
            "scale": {"x": 1.106, "y": 1.0, "z": 1.0},
            "original_dimensions": {"x": 45.2, "y": 30.0, "z": 12.5},
            "new_dimensions": {"x": 50.0, "y": 30.0, "z": 12.5}
        }
    """
    job_service = get_job_service()

    try:
        # Get job
        job = job_service.get_job(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404

        # Get target dimensions
        data = request.get_json()
        target_dims = data.get('dimensions')

        if not target_dims or not all(k in target_dims for k in ['x', 'y', 'z']):
            return jsonify({"error": "Invalid dimensions format. Required: x, y, z"}), 400

        # Get original dimensions
        mesh_data = job.get('mesh_dimensions')
        if not mesh_data:
            return jsonify({"error": "Mesh dimensions not available"}), 404

        original_dims = mesh_data['dimensions']

        # Calculate scale factors
        scale = {
            'x': round(target_dims['x'] / original_dims['x_mm'], 4),
            'y': round(target_dims['y'] / original_dims['y_mm'], 4),
            'z': round(target_dims['z'] / original_dims['z_mm'], 4)
        }

        # Calculate new dimensions
        new_dims = {
            'x': round(original_dims['x_mm'] * scale['x'], 2),
            'y': round(original_dims['y_mm'] * scale['y'], 2),
            'z': round(original_dims['z_mm'] * scale['z'], 2)
        }

        logger.info(f"Validated dimensions for job {job_id}: scale={scale}")

        return jsonify({
            "scale": scale,
            "original_dimensions": {
                "x": original_dims['x_mm'],
                "y": original_dims['y_mm'],
                "z": original_dims['z_mm']
            },
            "new_dimensions": new_dims
        })

    except Exception as e:
        logger.error(f"Failed to validate dimension for job {job_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500
