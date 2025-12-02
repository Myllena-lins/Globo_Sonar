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

    def run_workflow_with_edl(self, file_path: Path):
        """Função síncrona para rodar workflow e EDLService sem tocar no AsyncSession"""
        processor = MXFProcessor()
        streams = processor.get_streams(file_path)

        workflow = next((wf for wf in self.workflows if wf.can_handle(streams)), None)
        if not workflow:
            return []

        # workflow.process é async, rodamos apenas dentro da thread
        results = asyncio.run(workflow.process(file_path))

        # EDLService: criamos e armazenamos o EDL sem AsyncSession
        try:
            self.edl_service.create_and_store_edl_sync(file_path.name, results)
        except Exception as e:
            self.logger.error(f"Erro ao criar EDL: {e}")

        return results
