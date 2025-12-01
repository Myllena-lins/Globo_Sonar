from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from pathlib import Path
from repository.mxf_repository import MXFRepository
from core.database import get_db
from service.mxf_service import MXFService
import aiofiles

router = APIRouter()
service = MXFService(MXFRepository())


async def process_file_in_background(db, filename: str, path: Path):
    await service.process_uploaded_mxf(db, filename, path)


async def save_upload(file: UploadFile, save_path: Path):
    """
    Salva arquivo grande em chunks reais.
    Substitui o uso inválido de file.stream().
    """
    save_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(save_path, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)  
            if not chunk:
                break
            await f.write(chunk)


@router.post("/upload-mxf")
async def upload_mxf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db=Depends(get_db)
):
    # Validação simples
    if not file.filename.lower().endswith(".mxf"):
        raise HTTPException(status_code=400, detail="Arquivo precisa ser .mxf")

    save_path = Path("uploads") / file.filename

    # Salva o arquivo fisicamente
    await save_upload(file, save_path)

    # Adiciona o processamento pesado em background
    background_tasks.add_task(
        process_file_in_background,
        db, file.filename, save_path
    )

    return {"message": "Arquivo recebido. Processamento iniciado em background."}
