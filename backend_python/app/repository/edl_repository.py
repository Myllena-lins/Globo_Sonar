from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from core.logger import Logger
from app.model.edl import EDLEntry
from app.model.time_range import TimeRange
from sqlalchemy import select

class EDLRepository:

    def __init__(self):
        self.logger = Logger()

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
        

    async def get_timestamp(self, db: AsyncSession):
        self.logger.debug("get_timestamp: entry")
        """
        Retorna um único registro de time_range (id, audio_track_id, start_time, end_time).
        Por padrão retorna o último registro (maior id). Ajuste ORDER BY/WHERE conforme necessidade.
        """
        try:
            self.logger.debug("Buscando timestamp usando ORM")
            stmt = select(
                TimeRange.id,
                TimeRange.audio_track_id,
                TimeRange.start_time,
                TimeRange.end_time
            ).order_by(TimeRange.id.desc()).limit(1)

            result = await db.execute(stmt)
            row = result.first()
            self.logger.debug(f"get_timestamp: raw row -> {row}")

            if not row:
                return None

            return {
                "id": row[0],
                "audio_track_id": row[1],
                "start_time": row[2],
                "end_time": row[3],
            }

        except Exception as e:
            self.logger.error(f"Erro ao buscar timestamp com ORM: {e}")
            return None

    async def get_all_timestamps(self, db: AsyncSession):
        self.logger.debug("get_all_timestamps: entry")
        """
        Retorna todos os registros de time_range como lista de dicts:
        [{ "id": ..., "audio_track_id": ..., "start_time": ..., "end_time": ... }, ...]
        """
        try:
            stmt = select(
                TimeRange.id,
                TimeRange.audio_track_id,
                TimeRange.start_time,
                TimeRange.end_time
            ).order_by(TimeRange.id)
            result = await db.execute(stmt)
            rows = result.all()
            self.logger.debug(f"get_all_timestamps: fetched {len(rows)} rows")
            for i, r in enumerate(rows):
                self.logger.debug(f" get_all_timestamps row[{i}] = {r}")
            return [
                {
                    "id": r[0],
                    "audio_track_id": r[1],
                    "start_time": r[2],
                    "end_time": r[3],
                }
                for r in rows
            ]
        except Exception as e:
            self.logger.error(f"Erro ao buscar todos os timestamps: {e}")
            return []

    async def get_timestamp_by_audio_track_id(self, db: AsyncSession, audio_track_id: int):
        self.logger.debug(f"get_timestamp_by_audio_track_id: entry audio_track_id={audio_track_id}")
        """
        Retorna o último time_range para o audio_track_id fornecido (se existir).
        """
        try:
            stmt = select(
                TimeRange.id,
                TimeRange.audio_track_id,
                TimeRange.start_time,
                TimeRange.end_time
            ).where(TimeRange.audio_track_id == audio_track_id).order_by(TimeRange.id.desc()).limit(1)
            result = await db.execute(stmt)
            row = result.first()
            self.logger.debug(f"get_timestamp_by_audio_track_id({audio_track_id}) -> {row}")
            if not row:
                return None
            return {"id": row[0], "audio_track_id": row[1], "start_time": row[2], "end_time": row[3]}
        except Exception as e:
            self.logger.error(f"Erro ao buscar timestamp por audio_track_id={audio_track_id}: {e}")
            return None

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