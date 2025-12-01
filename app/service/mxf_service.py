from pathlib import Path
from core.config import Config
from core.file_processor import MXFProcessor
from core.logger import Logger
from features.workflows.unmixed_audio import UnmixedAudioWorkflow
from features.workflows.mixed_audio import MixedAudioWorkflow
from app.repository.edl_repository import EDLRepository
from app.service.edl_service import EDLService


class MXFService:

    def __init__(self, repository, edl_service: EDLService = None):
        self.repository = repository
        self.logger = Logger()
        self.config = Config()
        self.workflows = [
            UnmixedAudioWorkflow(),
            MixedAudioWorkflow()
        ]
        self.edl_service = EDLService(EDLRepository())

    async def process_uploaded_mxf(self, db, file_name: str, file_path: Path):
        self.logger.info(f"▶ Processando upload: {file_name}")

        mxf = self.repository.save_file_record(db, file_name, str(file_path))

        processor = MXFProcessor()
        streams = processor.get_streams(file_path)

        if not streams:
            self.repository.update_status(db, mxf.id, "error")
            return False

        workflow = next((wf for wf in self.workflows if wf.can_handle(streams)), None)

        if not workflow:
            self.repository.update_status(db, mxf.id, "no_workflow")
            return False

        results = await workflow.process(file_path)

        process_id = Path(file_name).stem
        await self.edl_service.create_and_store_edl(db, process_id, file_name, results)

        self.repository.update_status(db, mxf.id, "processed")

        return True