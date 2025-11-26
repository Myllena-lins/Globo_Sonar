from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pathlib import Path
from repository.mxf_repository import MXFRepository
from core.database import get_db
from service.mxf_service import MXFService

router = APIRouter()

service = MXFService(MXFRepository())

@router.post("/upload-mxf")
async def upload_mxf(
    file: UploadFile = File(...),
    db = Depends(get_db)
):
    if not file.filename.lower().endswith(".mxf"):
        raise HTTPException(status_code=400, detail="Arquivo precisa ser .mxf")

    save_path = Path("uploads") / file.filename
    save_path.parent.mkdir(exist_ok=True, parents=True)

    with save_path.open("wb") as buffer:
        buffer.write(await file.read())

    success = await service.process_uploaded_mxf(db, file.filename, save_path)

    if not success:
        raise HTTPException(status_code=500, detail="Falha no processamento")

    return {"message": "Arquivo recebido e processado com sucesso"}
