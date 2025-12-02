from pydantic import BaseModel
from typing import List
from app.dto.TimeRangeResponse import TimeRangeResponse

class AudioTrackResponse(BaseModel):
    id: int
    name: str
    album: str | None = None
    year: str | None = None
    authors: list[str] | None = None
    genres: list[str] | None = None
    isrc: str | None = None
    gmusic: str | None = None
    image_url: str | None = None
    occurrences: List[TimeRangeResponse] = []
