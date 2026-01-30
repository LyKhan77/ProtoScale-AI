from pydantic import BaseModel
from enum import Enum
from typing import Optional


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class UploadSettings(BaseModel):
    remove_background: bool = True
    enhanced_detail: bool = False


class JobCreatedResponse(BaseModel):
    job_id: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int = 0
    stage: Optional[str] = None
    error: Optional[str] = None


class JobListItem(BaseModel):
    job_id: str
    has_model: bool
    created_at: str


class AnalysisData(BaseModel):
    watertight: bool = True
    dimensions: dict = {"x": 0, "y": 0, "z": 0}
    volume: float = 0
