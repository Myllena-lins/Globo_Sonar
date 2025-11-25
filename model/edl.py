# models/edl.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from .schemas import BaseSchema

class EDLEvent(BaseSchema):
    event_number: int = Field(..., description="Número do evento", gt=0)
    reel: str = Field(..., description="Nome do reel")
    track_type: str = Field(..., example="AX", description="Tipo de track")
    edit_type: str = Field(..., example="C", description="Tipo de edição")
    source_start: str = Field(..., example="00:00:00:00", description="Início do source")
    source_end: str = Field(..., example="00:00:30:00", description="Fim do source")
    record_start: str = Field(..., example="00:00:00:00", description="Início do record")
    record_end: str = Field(..., example="00:00:30:00", description="Fim do record")
    clip_name: str = Field(..., description="Nome do clip")
    music_title: Optional[str] = Field(None, description="Título da música")
    music_artist: Optional[str] = Field(None, description="Artista da música")

class EDLBase(BaseSchema):
    title: str = Field(..., description="Título do EDL")
    frame_rate: float = Field(29.97, description="Taxa de frames por segundo")
    drop_frame: bool = Field(False, description="Usar drop frame notation")

class EDLCreate(BaseSchema):
    process_id: str = Field(..., description="ID do processo")
    frame_rate: Optional[float] = 29.97
    drop_frame: Optional[bool] = False

class EDLResponse(EDLBase):
    id: str = Field(..., description="ID único do EDL")
    process_id: str = Field(..., description="ID do processo associado")
    events: List[EDLEvent] = Field(..., description="Eventos do EDL")
    file_path: str = Field(..., description="Caminho do arquivo EDL")
    created_at: datetime = Field(..., description="Data de criação")
    total_events: int = Field(..., description="Número total de eventos")
    validation_status: str = Field(..., description="Status da validação")
    validation_errors: List[str] = Field(default_factory=list, description="Erros de validação")

class EDLValidation(BaseSchema):
    is_valid: bool = Field(..., description="Se o EDL é válido")
    errors: List[str] = Field(default_factory=list, description="Lista de erros")
    warnings: List[str] = Field(default_factory=list, description="Lista de avisos")
    compatible_standards: List[str] = Field(default_factory=list, description="Padrões compatíveis")