# models/stream.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from .schemas import BaseSchema, StreamType

class StreamBase(BaseSchema):
    stream_index: int = Field(..., description="Índice do stream", ge=0)
    codec_type: StreamType = Field(..., description="Tipo do stream")
    codec_name: str = Field(..., description="Nome do codec")
    duration: Optional[float] = Field(None, description="Duração em segundos")
    bit_rate: Optional[int] = Field(None, description="Bitrate em bps", ge=0)

class AudioStreamBase(StreamBase):
    channels: int = Field(..., description="Número de canais", ge=1)
    sample_rate: int = Field(..., description="Taxa de amostragem em Hz", ge=0)
    channel_layout: Optional[str] = Field(None, description="Layout dos canais")

class StreamCreate(BaseSchema):
    stream_index: int
    codec_type: StreamType
    codec_name: str
    channels: Optional[int] = None
    sample_rate: Optional[int] = None

class StreamResponse(AudioStreamBase):
    id: str = Field(..., description="ID único do stream")
    mxf_id: str = Field(..., description="ID do MXF associado")
    extracted_path: str = Field(..., description="Caminho do WAV extraído")
    file_size: int = Field(..., description="Tamanho do arquivo WAV")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais")