from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from pathlib import Path
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles
import asyncio
from sqlalchemy.orm import Session
from core.database import SessionLocal

from app.dto.MXFDetailResponse import MXFDetailResponse
from app.dto.AudioTrackResponse import AudioTrackResponse
from app.dto.TimeRangeResponse import TimeRangeResponse
from app.service.mxf_service import MXFService
from app.repository.mxf_repository import MXFRepository
from core.database import get_db, async_session
from sqlalchemy.orm import sessionmaker, selectinload
from core.database import engine  # engine síncrono
SyncSession = sessionmaker(bind=engine)

router = APIRouter(
    prefix="/v1/mxf",
    tags=["Análise de MXF"],
    responses={404: {"description": "Não encontrado"}}
)

repository = MXFRepository()
service = MXFService(repository)


class UploadResponse(BaseModel):
    id: int
    message: str = "Arquivo recebido e processamento iniciado em background"


async def save_upload(file: UploadFile, save_path: Path):
    save_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(save_path, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            await f.write(chunk)
            
@router.post(
    "",
    summary="Upload de arquivo MXF",
    description="Cria registro e inicia processamento em background",
    response_model=UploadResponse,
    status_code=202
)
async def upload_mxf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Salva arquivo, cria registro MXF, agenda background task.
    """
    if not file.filename.lower().endswith(".mxf"):
        raise HTTPException(status_code=400, detail="Arquivo precisa ser .mxf")

    import shutil
    save_path = Path("uploads") / file.filename
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        mxf = await service.create_mxf_record(db, file.filename, str(save_path))
        
        service.logger.info(f"MXF record created: id={mxf.id}")

        background_tasks.add_task(service.process_file_in_background, async_session, mxf.id, str(save_path))

        return UploadResponse(id=mxf.id, message=f"Arquivo '{file.filename}' recebido.")
    
    except Exception as e:
        service.logger.error(f"Erro ao fazer upload: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {e}")


def ms_to_hms(ms: int) -> str:
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

@router.get("/{mxf_id}", response_model=MXFDetailResponse)
def get_mxf_details(mxf_id: int):
    """
    Rota SÍNCRONA — rodará em thread worker separada do background processing.
    Usa SessionLocal (síncrono) para evitar contenção com async_session do background.
    """
    db = None
    try:
        db = SessionLocal()
        
        mxf = repository.get_by_id_sync(db, mxf_id)
        
        if not mxf:
            raise HTTPException(status_code=404, detail="MXF não encontrado")

        audio_tracks = []
        for track in mxf.audio_tracks:
            occurrences = [
                TimeRangeResponse(
                    id=occ.id,
                    start_time=ms_to_hms(occ.start_time),
                    end_time=ms_to_hms(occ.end_time)
                )
                for occ in track.occurrences
            ]

            audio_tracks.append(
                AudioTrackResponse(
                    id=track.id,
                    name=track.name,
                    album=track.album,
                    year=track.year,
                    authors=track.authors,
                    genres=track.genres,
                    isrc=track.isrc,
                    gmusic=track.gmusic,
                    image_url=track.image_url,
                    occurrences=occurrences
                )
            )

        return MXFDetailResponse(
            id=mxf.id,
            edl_id=mxf.edl_id,
            file_name=mxf.file_name,
            file_path=mxf.path,
            status=mxf.status,
            audio_tracks=audio_tracks
        )
    finally:
        if db:
            db.close()