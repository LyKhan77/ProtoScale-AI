"""Job state management service using Redis."""
import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from app.extensions import get_redis
from app.config import get_config
from app.utils import get_logger

logger = get_logger(__name__)


class JobStatus(str, Enum):
    """Job status enumeration."""
    UPLOADED = "uploaded"
    GENERATING_MULTI_ANGLES = "generating_multi_angles"
    PREPROCESSING = "preprocessing"
    RECONSTRUCTING_3D = "reconstructing_3d"
    MESH_REPAIRING = "mesh_repairing"
    EXPORTING_STL = "exporting_stl"
    DONE = "done"
    ERROR = "error"


class JobService:
    """Service for managing job state in Redis."""

    KEY_PREFIX = "job:"

    def __init__(self):
        self.redis = get_redis()
        self.config = get_config()

    def _get_key(self, job_id: str) -> str:
        """Get Redis key for a job."""
        return f"{self.KEY_PREFIX}{job_id}"

    def create_job(self, image_path: str) -> dict:
        """Create a new job.

        Args:
            image_path: Path to uploaded image

        Returns:
            Job data dictionary
        """
        job_id = str(uuid.uuid4())
        job_data = {
            "id": job_id,
            "status": JobStatus.UPLOADED.value,
            "progress": 0,
            "image_path": image_path,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "error_message": None,
            "error_stage": None,
            "multi_angle_images": [],
            "preprocessed_image": None,
            "mesh_path": None,
            "stl_path": None,
            "obj_path": None,
            "analysis_data": None,
        }

        key = self._get_key(job_id)
        self.redis.setex(
            key,
            self.config.JOB_EXPIRY_SECONDS,
            json.dumps(job_data)
        )

        logger.info(f"Created job {job_id}")
        return job_data

    def get_job(self, job_id: str) -> Optional[dict]:
        """Get job data by ID.

        Args:
            job_id: Job identifier

        Returns:
            Job data dictionary or None if not found
        """
        key = self._get_key(job_id)
        data = self.redis.get(key)
        if not data:
            return None
        return json.loads(data)

    def update_job(self, job_id: str, updates: dict) -> Optional[dict]:
        """Update job data.

        Args:
            job_id: Job identifier
            updates: Dictionary of fields to update

        Returns:
            Updated job data or None if not found
        """
        job = self.get_job(job_id)
        if not job:
            return None

        job.update(updates)
        job["updated_at"] = datetime.utcnow().isoformat()

        key = self._get_key(job_id)
        # Get remaining TTL
        ttl = self.redis.ttl(key)
        if ttl > 0:
            self.redis.setex(key, ttl, json.dumps(job))
        else:
            self.redis.setex(key, self.config.JOB_EXPIRY_SECONDS, json.dumps(job))

        return job

    def update_status(self, job_id: str, status: JobStatus, progress: int = None) -> Optional[dict]:
        """Update job status.

        Args:
            job_id: Job identifier
            status: New status
            progress: Optional progress percentage

        Returns:
            Updated job data or None if not found
        """
        updates = {"status": status.value}
        if progress is not None:
            updates["progress"] = progress

        logger.info(f"Job {job_id} status: {status.value}, progress: {progress}")
        return self.update_job(job_id, updates)

    def update_progress(self, job_id: str, progress: int) -> Optional[dict]:
        """Update job progress.

        Args:
            job_id: Job identifier
            progress: Progress percentage (0-100)

        Returns:
            Updated job data or None if not found
        """
        return self.update_job(job_id, {"progress": min(100, max(0, progress))})

    def set_error(self, job_id: str, message: str, stage: str = None) -> Optional[dict]:
        """Set job to error state.

        Args:
            job_id: Job identifier
            message: Error message
            stage: Stage where error occurred

        Returns:
            Updated job data or None if not found
        """
        logger.error(f"Job {job_id} error at {stage}: {message}")
        return self.update_job(job_id, {
            "status": JobStatus.ERROR.value,
            "error_message": message,
            "error_stage": stage,
        })

    def set_done(self, job_id: str, stl_path: str, obj_path: str, analysis_data: dict) -> Optional[dict]:
        """Set job to done state with results.

        Args:
            job_id: Job identifier
            stl_path: Path to STL file
            obj_path: Path to OBJ file
            analysis_data: Mesh analysis data

        Returns:
            Updated job data or None if not found
        """
        logger.info(f"Job {job_id} completed")
        return self.update_job(job_id, {
            "status": JobStatus.DONE.value,
            "progress": 100,
            "stl_path": stl_path,
            "obj_path": obj_path,
            "analysis_data": analysis_data,
        })

    def set_multi_angle_images(self, job_id: str, image_paths: list) -> Optional[dict]:
        """Set multi-angle image paths.

        Args:
            job_id: Job identifier
            image_paths: List of image paths

        Returns:
            Updated job data or None if not found
        """
        return self.update_job(job_id, {"multi_angle_images": image_paths})

    def set_preprocessed_image(self, job_id: str, image_path: str) -> Optional[dict]:
        """Set preprocessed image path.

        Args:
            job_id: Job identifier
            image_path: Path to preprocessed image

        Returns:
            Updated job data or None if not found
        """
        return self.update_job(job_id, {"preprocessed_image": image_path})

    def set_mesh_path(self, job_id: str, mesh_path: str) -> Optional[dict]:
        """Set mesh file path.

        Args:
            job_id: Job identifier
            mesh_path: Path to mesh file

        Returns:
            Updated job data or None if not found
        """
        return self.update_job(job_id, {"mesh_path": mesh_path})


# Singleton instance
_job_service = None


def get_job_service() -> JobService:
    """Get job service singleton."""
    global _job_service
    if _job_service is None:
        _job_service = JobService()
    return _job_service
