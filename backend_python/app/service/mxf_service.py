from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from core.file_processor import MXFProcessor
from core.logger import Logger
from features.workflows.unmixed_audio import UnmixedAudioWorkflow
from features.workflows.mixed_audio import MixedAudioWorkflow
from app.repository.mxf_repository import MXFRepository
from app.repository.edl_repository import EDLRepository
from app.service.edl_service import EDLService
import asyncio
from core.database import SessionLocal

class MXFService:
    def __init__(self, repository: MXFRepository, edl_service: EDLService = None):
        self.repository = repository
        self.logger = Logger()
        self.workflows = [UnmixedAudioWorkflow(), MixedAudioWorkflow()]
        self.edl_service = edl_service or EDLService(EDLRepository())

    async def create_mxf_record(self, db: AsyncSession, file_name: str, file_path: str):
        return await self.repository.save_file_record(db, file_name, file_path)

    async def get_mxf_details(self, db: AsyncSession, mxf_id: int):
        return await self.repository.get_mxf_with_tracks(db, mxf_id)

    def run_workflow_with_edl(self, file_path: Path, mxf_id: int | None = None):
        """Executa o workflow e cria EDL; se mxf_id for fornecido, atualiza mxf.edl_id."""
        processor = MXFProcessor()
        streams = processor.get_streams(file_path)

        workflow = next((wf for wf in self.workflows if wf.can_handle(streams)), None)
        if not workflow:
            return []

        results = asyncio.run(workflow.process(file_path))

        try:
            # passa o mxf_id para que o EDLService atualize MXF.edl_id internamente
            self.edl_service.create_and_store_edl_sync(file_path.name, results, mxf_id=mxf_id)
        except Exception as e:
            self.logger.error(f"Erro ao criar EDL: {e}")

        return results
