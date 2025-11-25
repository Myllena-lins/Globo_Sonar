# models/mxf.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from pathlib import Path
from .schemas import BaseSchema
from .stream import StreamResponse
from .process import ProcessStatus

class MXFUpload(BaseSchema):
    filename: str = Field(..., description="Nome do arquivo MXF")

class MXFBase(BaseSchema):
    file_path: str = Field(..., description="Caminho do arquivo salvo")
    file_size: int = Field(..., description="Tamanho em bytes", ge=0)
    duration: Optional[float] = Field(None, description="Duração em segundos")
    format_name: Optional[str] = Field(None, description="Formato do container")

class MXFResponse(MXFBase):
    id: str = Field(..., description="ID único do MXF")
    process_id: str = Field(..., description="ID do processo associado")
    status: ProcessStatus = Field(..., description="Status do processamento")
    created_at: datetime = Field(..., description="Data de upload")
    streams: List[StreamResponse] = Field(default_factory=list, description="Streams extraídos")
    extraction_time: Optional[float] = Field(None, description="Tempo de extração em segundos")
    
    @validator('file_size')
    def validate_file_size(cls, v):
        if v <= 0:
            raise ValueError('File size must be positive')
        return v

class MXFStatusResponse(BaseSchema):
    process_id: str = Field(..., description="ID do processo")
    status: ProcessStatus = Field(..., description="Status atual")
    progress: str = Field(..., description="Descrição do progresso")
    streams_extracted: int = Field(0, description="Streams extraídos")
    songs_detected: int = Field(0, description="Músicas detectadas")
    estimated_time_remaining: Optional[float] = Field(None, description="Tempo estimado restante")