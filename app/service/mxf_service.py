from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import Config
from core.file_processor import MXFProcessor
from core.logger import Logger

from features.workflows.unmixed_audio import UnmixedAudioWorkflow
from features.workflows.mixed_audio import MixedAudioWorkflow

from app.repository.mxf_repository import MXFRepository
from app.repository.edl_repository import EDLRepository
from app.service.edl_service import EDLService


class MXFService:
    def __init__(self, repository: MXFRepository, edl_service: EDLService = None):
        self.repository = repository
        self.logger = Logger()
        self.config = Config()

        self.workflows = [
            UnmixedAudioWorkflow(),
            MixedAudioWorkflow(),
        ]

        self.edl_service = edl_service or EDLService(EDLRepository())

    async def create_mxf_record(self, db: AsyncSession, file_name: str, file_path: str):
        return await self.repository.save_file_record(db, file_name, file_path)

    async def process_uploaded_mxf(self, db: AsyncSession, mxf_id: int, file_path: Path):
        mxf = await self.repository.get_by_id(db, mxf_id)
        if not mxf:
            raise ValueError(f"MXF id {mxf_id} não encontrado")

        processor = MXFProcessor()
        streams = processor.get_streams(file_path)

        if not streams:
            await self.repository.update_status(db, mxf.id, "error")
            return False

        workflow = next((wf for wf in self.workflows if wf.can_handle(streams)), None)

        if not workflow:
            await self.repository.update_status(db, mxf.id, "no_workflow")
            return False

        results = await workflow.process(file_path)

        await self.repository.save_audio_tracks(db, mxf, results)

        process_id = Path(file_path.name).stem
        await self.edl_service.create_and_store_edl(
            db, process_id, file_path.name, results
        )

        self.logger.info(f"✅ Processamento concluído: {file_path.name}")

        await self.repository.update_status(db, mxf.id, "processed")
        return True

    async def get_mxf_details(self, db: AsyncSession, mxf_id: int):
        return await self.repository.get_mxf_with_tracks(db, mxf_id)
