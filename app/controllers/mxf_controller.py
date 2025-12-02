from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from pathlib import Path
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import aiofiles
import asyncio

from app.dto.MXFDetailResponse import MXFDetailResponse
from app.dto.AudioTrackResponse import AudioTrackResponse
from app.dto.TimeRangeResponse import TimeRangeResponse
from app.service.mxf_service import MXFService
from app.repository.mxf_repository import MXFRepository
from core.database import get_db, async_session
from sqlalchemy.orm import sessionmaker
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
            
async def process_file_in_background(mxf_id: int, file_path: Path):
    async with async_session() as db:
        mxf = await service.repository.get_by_id(db, mxf_id)
        if not mxf:
            await asyncio.to_thread(update_status_sync_thread, mxf_id, "error")
            return
        results = await asyncio.to_thread(service.run_workflow_with_edl, file_path, mxf.id)
        await service.repository.save_audio_tracks(db, mxf, results)

        await asyncio.to_thread(update_status_sync_thread, mxf.id, "processed")

def update_status_sync_thread(file_id: int, status: str):
    with SyncSession() as db:
        service.repository.update_status_sync(db, file_id, status)


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
    if not file.filename.lower().endswith(".mxf"):
        raise HTTPException(status_code=400, detail="Arquivo precisa ser .mxf")

    save_path = Path("uploads") / file.filename
    await save_upload(file, save_path)

    mxf = await service.create_mxf_record(db, file.filename, str(save_path))

    background_tasks.add_task(process_file_in_background, mxf.id, save_path)

    return UploadResponse(id=mxf.id, message=f"Arquivo '{file.filename}' recebido.")


@router.get("/{mxf_id}", response_model=MXFDetailResponse)
async def get_mxf_details(
    mxf_id: int,
    db: AsyncSession = Depends(get_db)
):
    mxf = await service.get_mxf_details(db, mxf_id)
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


def ms_to_hms(ms: int) -> str:
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"
