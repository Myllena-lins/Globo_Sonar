from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from pathlib import Path
from app.service.mxf_service import MXFService
from app.repository.mxf_repository import MXFRepository
from core.database import get_db
from pydantic import BaseModel
import aiofiles

router = APIRouter(
    prefix="/v1/mxf",
    tags=["Análise de MXF"],
    responses={404: {"description": "Não encontrado"}}
)

service = MXFService(MXFRepository())

# Response model para Swagger
class UploadResponse(BaseModel):
    message: str = "Mensagem de status do upload"

async def process_file_in_background(db, filename: str, path: Path):
    """
    Processa o arquivo MXF em background.
    """
    await service.process_uploaded_mxf(db, filename, path)

async def save_upload(file: UploadFile, save_path: Path):
    """
    Salva arquivo grande em chunks reais.
    """
    save_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(save_path, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)  # 1MB por vez
            if not chunk:
                break
            await f.write(chunk)

@router.post(
    "",
    summary="Upload de arquivo MXF",
    description=(
        "Faz o upload de um arquivo `.mxf` para processamento. "
        "O arquivo é salvo no servidor e processado em background. "
        "Retorna uma mensagem de confirmação imediata."
    ),
    response_model=UploadResponse,
    status_code=202
)
async def upload_mxf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Arquivo MXF a ser processado"),
    db=Depends(get_db)
):
    """
    Endpoint para receber um arquivo MXF e iniciar processamento assíncrono.

    - **file**: arquivo .mxf a ser processado
    - Retorna uma mensagem de confirmação
    """
    if not file.filename.lower().endswith(".mxf"):
        raise HTTPException(status_code=400, detail="Arquivo precisa ser .mxf")

    save_path = Path("uploads") / file.filename

    await save_upload(file, save_path)

    background_tasks.add_task(process_file_in_background, db, file.filename, save_path)

    return {"message": f"Arquivo '{file.filename}' recebido. Processamento iniciado em background."}
