from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from pathlib import Path

from .base_controller import BaseController


class EdlController(BaseController):
    def __init__(self):
        self.OUTPUT_DIR = Path("/home/enio/dev/Globo_Sonar/files/edl")
        
        super().__init__()

    def _register_routes(self):
        self.router.add_api_route(
            "/{request_id}",
            self.download_edl,
            methods=["GET"],
            summary="Baixar arquivo EDL",
            description="Faz download do arquivo .edl gerado para a análise",
        )

    async def download_edl(self, request_id: str):
        edl_path = self.OUTPUT_DIR / f"{request_id}.edl"

        if not edl_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Arquivo EDL não encontrado para request_id: {request_id}",
            )

        return FileResponse(
            path=edl_path,
            filename=f"{request_id}.edl",
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={request_id}.edl"},
        )
