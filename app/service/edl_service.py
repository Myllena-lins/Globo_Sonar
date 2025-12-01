# app/service/edl_service.py
from pathlib import Path
from datetime import datetime
from core.config import Config
from core.logger import Logger
from app.repository.edl_repository import EDLRepository

class EDLService:

    def __init__(self, repository: EDLRepository):
        self.repository = repository
        self.logger = Logger()
        self.config = Config()

    async def create_and_store_edl(self, db, process_id: str, source_file: str, recognition_results, frame_rate: float = 29.97, drop_frame: bool = False):
        edl_name = f"{Path(source_file).stem}.edl"
        edl_path = self.config.WATCHFOLDER_OUTPUT / edl_name

        events = self.generate_structured_events(recognition_results, source_file)
        total_events = len(events)
        validation_status = "validated" if total_events > 0 else "no_music"
        validation_errors = [] if total_events > 0 else ["No music recognized"]

        edl_id = self.repository.save_edl_record(
            db,
            process_id=process_id,
            edl_name=edl_name,
            path=str(edl_path),
            frame_rate=frame_rate,
            drop_frame=drop_frame,
            total_events=total_events,
            validation_status=validation_status,
            validation_errors=validation_errors
        )

        edl_content = self.generate_edl(recognition_results, source_file)
        saved = self.save_edl(edl_content, edl_path)

        if not saved:
            self.repository.update_status(db, edl_id, "error", ["Failed to save EDL file"])
            validation_status = "error"
        else:
            self.repository.update_status(db, edl_id, validation_status, validation_errors if validation_errors else None)

        return {
            "id": str(edl_id),
            "process_id": process_id,
            "title": edl_name,
            "frame_rate": frame_rate,
            "drop_frame": drop_frame,
            "events": events,
            "file_path": str(edl_path),
            "created_at": datetime.now(),
            "total_events": total_events,
            "validation_status": validation_status,
            "validation_errors": validation_errors,
        }