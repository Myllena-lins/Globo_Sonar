from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.model.edl import EDLEntry

class EDLRepository:

    async def save_edl_record(
        self, db: AsyncSession, process_id, edl_name, path=None, blob=None,
        frame_rate=29.97, drop_frame=False, total_events=0,
        validation_status="pending", validation_errors=None
    ):
        edl = EDLEntry(
            process_id=process_id,
            edl_name=edl_name,
            path=path,
            blob=blob,
            frame_rate=frame_rate,
            drop_frame=drop_frame,
            total_events=total_events,
            validation_status=validation_status,
            validation_errors=",".join(validation_errors) if validation_errors else None
        )
        db.add(edl)
        await db.commit()
        await db.refresh(edl)
        return edl.id

    async def update_status(
        self, db: AsyncSession, edl_id: int, validation_status: str, validation_errors: list = None
    ):
        edl = await db.get(EDLEntry, edl_id)
        if not edl:
            return None
        edl.validation_status = validation_status
        if validation_errors is not None:
            edl.validation_errors = ",".join(validation_errors)
        await db.commit()
        await db.refresh(edl)
        return edl

    async def get_edl(self, db: AsyncSession, edl_id: int):
        edl = await db.get(EDLEntry, edl_id)
        if not edl:
            return None
        return {
            "id": edl.id,
            "process_id": edl.process_id,
            "edl_name": edl.edl_name,
            "blob": edl.blob,
            "file_path": edl.path,
            "frame_rate": edl.frame_rate,
            "drop_frame": edl.drop_frame,
            "total_events": edl.total_events,
            "validation_status": edl.validation_status,
            "validation_errors": edl.validation_errors.split(",") if edl.validation_errors else [],
            "created_at": edl.created_at,
        }

    def save_edl_record_sync(
        self, db: Session, process_id, edl_name, path=None, blob=None,
        frame_rate=29.97, drop_frame=False, total_events=0,
        validation_status="pending", validation_errors=None
    ):
        """
        Versão síncrona de save_edl_record para rodar em threads de background.
        """
        edl = EDLEntry(
            process_id=process_id,
            edl_name=edl_name,
            path=path,
            blob=blob,
            frame_rate=frame_rate,
            drop_frame=drop_frame,
            total_events=total_events,
            validation_status=validation_status,
            validation_errors=",".join(validation_errors) if validation_errors else None
        )
        db.add(edl)
        db.commit()
        db.refresh(edl)
        return edl.id

    def update_status_sync(
        self, db: Session, edl_id: int, validation_status: str, validation_errors: list | None = None
    ):
        """
        Versão síncrona de update_status para uso no fluxo sync.
        """
        edl = db.get(EDLEntry, edl_id)
        if not edl:
            return None
        edl.validation_status = validation_status
        if validation_errors is not None:
            edl.validation_errors = ",".join(validation_errors)
        db.commit()
        db.refresh(edl)
        return edl