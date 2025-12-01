# app/repository/edl_repository.py
from sqlalchemy.orm import Session
from app.model.edl import EDLEntry

class EDLRepository:

    def save_edl_record(
        self, db: Session, process_id: str, edl_name: str, path: str,
        frame_rate: float, drop_frame: bool, total_events: int,
        validation_status: str, validation_errors: list
    ) -> int:
        edl = EDLEntry(
            process_id=process_id,
            edl_name=edl_name,
            path=path,
            frame_rate=frame_rate,
            drop_frame=drop_frame,
            total_events=total_events,
            validation_status=validation_status,
            validation_errors=",".join(validation_errors)
        )
        db.add(edl)
        db.commit()
        db.refresh(edl)
        return edl.id

    def update_status(self, db: Session, edl_id: int, validation_status: str, validation_errors: list = None):
        edl = db.get(EDLEntry, edl_id)
        if not edl:
            return None
        edl.validation_status = validation_status
        if validation_errors is not None:
            edl.validation_errors = ",".join(validation_errors)
        db.commit()
        db.refresh(edl)
        return edl

    def get_edl(self, db: Session, edl_id: int):
        edl = db.get(EDLEntry, edl_id)
        if not edl:
            return None
        return {
            "id": edl.id,
            "process_id": edl.process_id,
            "edl_name": edl.edl_name,
            "file_path": edl.path,
            "frame_rate": edl.frame_rate,
            "drop_frame": edl.drop_frame,
            "total_events": edl.total_events,
            "validation_status": edl.validation_status,
            "validation_errors": edl.validation_errors.split(",") if edl.validation_errors else [],
            "created_at": edl.created_at,
        }
