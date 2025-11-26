from pathlib import Path
from core.config import Config
from core.file_processor import MXFProcessor
from core.logger import Logger
from processors.edl_generator import EDLGenerator
from workflows.mixed_audio import MixedAudioWorkflow
from workflows.unmixed_audio import UnmixedAudioWorkflow


class MXFService:

    def __init__(self, repository):
        self.repository = repository
        self.logger = Logger()
        self.config = Config()
        self.workflows = [
            UnmixedAudioWorkflow(),
            MixedAudioWorkflow()
        ]
        self.edl_generator = EDLGenerator()

    async def process_uploaded_mxf(self, db, file_name: str, file_path: Path):
        self.logger.info(f"▶ Processando upload: {file_name}")

        self.repository.save_file_record(db, file_name, str(file_path))

        processor = MXFProcessor()
        streams = processor.get_streams(file_path)

        if not streams:
            self.repository.update_status(db, file_name, "error")
            return False

        workflow = next((wf for wf in self.workflows if wf.can_handle(streams)), None)

        if not workflow:
            self.repository.update_status(db, file_name, "no_workflow")
            return False

        results = await workflow.process(file_path)

        edl_name = f"{Path(file_name).stem}.edl"
        edl_path = self.config.WATCHFOLDER_OUTPUT / edl_name

        edl_content = self.edl_generator.generate_edl(results, file_name)
        self.edl_generator.save_edl(edl_content, edl_path)

        self.repository.update_status(db, file_name, "processed")

        return True
