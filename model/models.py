# models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ProcessStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class StreamType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"
    DATA = "data"

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        use_enum_values = True

class HealthResponse(BaseSchema):
    status: str = Field(..., example="healthy")
    timestamp: datetime = Field(...)
    service: str = Field(..., example="Audio Analysis API")
    version: str = Field(..., example="1.0.0")