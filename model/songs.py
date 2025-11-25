# models/song.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .schemas import BaseSchema

class SongDetection(BaseSchema):
    start_time: float = Field(..., description="Início em segundos", ge=0)
    end_time: float = Field(..., description="Fim em segundos", ge=0)
    confidence: float = Field(..., description="Confiança (0-1)", ge=0, le=1)

class SongBase(BaseSchema):
    title: str = Field(..., description="Título da música")
    artist: str = Field(..., description="Artista/banda")
    album: Optional[str] = Field(None, description="Álbum")

class SongCreate(BaseSchema):
    title: str
    artist: str
    album: Optional[str] = None

class SongResponse(SongBase):
    id: str = Field(..., description="ID único da música")
    process_id: str = Field(..., description="ID do processo associado")
    stream_id: str = Field(..., description="ID do stream onde foi detectada")
    detections: List[SongDetection] = Field(..., description="Detecções temporais")
    cover_art_url: Optional[str] = Field(None, description="URL da capa do álbum")
    isrc: Optional[str] = Field(None, description="Código ISRC internacional")
    gmusic_id: Optional[str] = Field(None, description="ID do Google Music")
    duration: float = Field(..., description="Duração total da música")
    wav_path: str = Field(..., description="Caminho do arquivo WAV")
    detected_at: datetime = Field(..., description="Data da detecção")

class TracksResponse(BaseSchema):
    process_id: str = Field(..., description="ID do processo")
    songs: List[SongResponse] = Field(..., description="Músicas detectadas")
    total_tracks: int = Field(..., description="Número total de músicas")
    analysis_time: float = Field(..., description="Tempo de análise em segundos")