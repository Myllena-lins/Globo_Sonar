# models/process.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .schemas import BaseSchema, ProcessStatus

class ProcessBase(BaseSchema):
    filename: str = Field(..., description="Nome do arquivo original")
    status: ProcessStatus = Field(..., description="Status do processamento")

class ProcessCreate(BaseSchema):
    filename: str = Field(..., description="Nome do arquivo MXF")

class ProcessResponse(ProcessBase):
    id: str = Field(..., description="ID único do processo")
    request_id: str = Field(..., description="ID da requisição")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data da última atualização")
    processing_time: Optional[float] = Field(None, description="Tempo de processamento em segundos")
    error_message: Optional[str] = Field(None, description="Mensagem de erro em caso de falha")
    streams_count: int = Field(0, description="Número de streams extraídos")
    songs_count: int = Field(0, description="Número de músicas detectadas")