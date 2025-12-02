# app/api/edl_controller.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO

from app.repository.edl_repository import EDLRepository
from core.database import get_db

router = APIRouter(
    prefix="/v1/edl",
    tags=["EDL"],
    responses={404: {"description": "Não encontrado"}}
)

repository = EDLRepository()

@router.get("/{edl_id}/download", summary="Download do arquivo EDL")
async def download_edl(edl_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retorna o arquivo EDL armazenado no banco como download.
    """
    edl_record = await repository.get_edl(db, edl_id)
    if not edl_record or not edl_record.get("validation_status"):
        raise HTTPException(status_code=404, detail="EDL não encontrado")

    blob = edl_record.get("blob")
    if not blob:
        raise HTTPException(status_code=404, detail="Blob do EDL não encontrado")

    filename = edl_record.get("edl_name", f"edl_{edl_id}.edl")

    # Cria um stream para o blob
    file_stream = BytesIO(blob.encode("utf-8"))

    return StreamingResponse(
        file_stream,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
