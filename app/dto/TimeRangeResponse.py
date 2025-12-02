from pydantic import BaseModel
from datetime import datetime

class TimeRangeResponse(BaseModel):
    id: int
    start_time: str
    end_time: str