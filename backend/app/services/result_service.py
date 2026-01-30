"""Result service for aggregating job results."""
from typing import Optional

from app.services.job_service import get_job_service, JobStatus
from app.storage.local import get_job_storage, get_export_storage
from app.utils import NotFoundError, get_logger

logger = get_logger(__name__)


class ResultService:
    """Service for aggregating and retrieving job results."""

    def __init__(self):
        self.job_service = get_job_service()
        self.job_storage = get_job_storage()
        self.export_storage = get_export_storage()

    def get_result(self, job_id: str) -> dict:
        """Get complete result for a job.

        Args:
            job_id: Job identifier

        Returns:
            Result dictionary with all outputs

        Raises:
            NotFoundError: If job not found
        """
        job = self.job_service.get_job(job_id)
        if not job:
            raise NotFoundError(f"Job {job_id} not found")

        result = {
            "job_id": job_id,
            "status": job["status"],
            "progress": job["progress"],
            "created_at": job["created_at"],
            "updated_at": job["updated_at"],
        }

        # Add error info if present
        if job["status"] == JobStatus.ERROR.value:
            result["error_message"] = job.get("error_message")
            result["error_stage"] = job.get("error_stage")

        # Add preprocessed image if available
        if job.get("preprocessed_image"):
            result["preprocessed_image"] = f"/api/files/jobs/{job_id}/{job['preprocessed_image']}"

        # Add 3D preview if available
        if job.get("obj_path"):
            result["preview_obj"] = f"/api/files/exports/{job_id}/{job['obj_path']}"

        # Add download URLs if done
        if job["status"] == JobStatus.DONE.value:
            if job.get("stl_path"):
                result["stl_download_url"] = f"/api/download/{job_id}/stl"
            if job.get("obj_path"):
                result["obj_download_url"] = f"/api/download/{job_id}/obj"

        # Add analysis data if available
        if job.get("analysis_data"):
            result["analysis_data"] = job["analysis_data"]
            # Extract mesh dimensions for frontend scaling tools
            dims = job["analysis_data"].get("dimensions", {})
            result["mesh_dimensions"] = {
                "x_mm": dims.get("x", 0),
                "y_mm": dims.get("y", 0),
                "z_mm": dims.get("z", 0),
                "volume_mm3": job["analysis_data"].get("volume", 0),
                "watertight": job["analysis_data"].get("watertight", False),
                "manifold": job["analysis_data"].get("manifold", False),
            }

        return result

    def get_download_path(self, job_id: str, format: str) -> Optional[str]:
        """Get file path for download.

        Args:
            job_id: Job identifier
            format: File format (stl or obj)

        Returns:
            Full file path or None if not found

        Raises:
            NotFoundError: If job not found
        """
        job = self.job_service.get_job(job_id)
        if not job:
            raise NotFoundError(f"Job {job_id} not found")

        if job["status"] != JobStatus.DONE.value:
            raise NotFoundError(f"Job {job_id} not yet completed")

        if format == "stl" and job.get("stl_path"):
            return self.export_storage.get_path(f"{job_id}/{job['stl_path']}")
        elif format == "obj" and job.get("obj_path"):
            return self.export_storage.get_path(f"{job_id}/{job['obj_path']}")
        else:
            raise NotFoundError(f"Format {format} not available for job {job_id}")


# Singleton instance
_result_service = None


def get_result_service() -> ResultService:
    """Get result service singleton."""
    global _result_service
    if _result_service is None:
        _result_service = ResultService()
    return _result_service
