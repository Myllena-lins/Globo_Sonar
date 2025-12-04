from typing import List, Optional
from pydantic import BaseModel
from app.dto.AudioTrackResponse import AudioTrackResponse

class MXFDetailResponse(BaseModel):
    id: int
    edl_id: int
    file_name: str
    file_path: str
    status: str
    audio_tracks: List[AudioTrackResponse] = [] # type: ignore
