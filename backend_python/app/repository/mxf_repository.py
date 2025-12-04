import logging
from fastapi import logger
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.model.audio_track import AudioTrack
from app.model.mxf import MXFFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.model.time_range import TimeRange

logger = logging.getLogger(__name__)

class MXFRepository:

    async def save_file_record(self, db: AsyncSession, file_name: str, file_path: str):
        mxf = MXFFile(file_name=file_name, path=file_path, status="pending")
        db.add(mxf)
        await db.commit()
        await db.refresh(mxf)
        return mxf
    
    from sqlalchemy.exc import SQLAlchemyError

    async def update_status(self, db: AsyncSession, file_id: int, status: str):
        try:
            stmt = (
                update(MXFFile)
                .where(MXFFile.id == file_id)
                .values(status=status)
            )
            await db.execute(stmt)
            await db.commit()
            return True
        except SQLAlchemyError as e:
            await db.rollback()
            raise RuntimeError(f"Erro ao atualizar status do MXFFile: {e}") from e

    async def save_audio_tracks(self, db: AsyncSession, mxf: MXFFile, results: list):
        for r in results:
            track = AudioTrack(
                mxf_id=mxf.id,
                name=r.get("title") or r.get("track", {}).get("title"),
                album=r.get("album"),
                year=r.get("release_date"),
                authors=[r.get("artist")] if r.get("artist") else [],
                genres=[r.get("genre_primary")] if r.get("genre_primary") else [],
                isrc=r.get("isrc"),
                gmusic=r.get("google_music_url") or None,
                image_url=r.get("cover_art") or r.get("cover_art_hq")
            )
            db.add(track)
            await db.flush()

            shazam_data = r.get("shazam_data") or {}
            matches = shazam_data.get("matches", [])
            for m in matches:
                tr = TimeRange(
                    audio_track_id=track.id,
                    start_time=int(m.get("offset", 0) * 1000),
                    end_time=int(m.get("offset", 0) * 1000) + r.get("segment_duration", 0)
                )
                db.add(tr)
        
        await db.commit()

    async def get_mxf_with_tracks(self, db: AsyncSession, mxf_id: int):
        """
        Busca MXF pelo ID e carrega todas as faixas de áudio e suas ocorrências (time ranges)
        """
        result = await db.execute(
            select(MXFFile)
            .where(MXFFile.id == mxf_id)
            .options(
                selectinload(MXFFile.audio_tracks).selectinload(AudioTrack.occurrences),
                selectinload(MXFFile.edl) 
            )
        )
        mxf = result.scalars().first()
        return mxf
    
    async def get_by_id(self, db: AsyncSession, file_id: int) -> MXFFile | None:
        """
        Busca um registro MXF pelo ID.
        """
        result = await db.execute(
            select(MXFFile).where(MXFFile.id == file_id)
        )
        return result.scalars().first()
    
    async def get_mxf_with_tracks(self, db: AsyncSession, mxf_id: int):
        """
        Busca MXF pelo ID e carrega todas as faixas de áudio e suas ocorrências (time ranges)
        """
        result = await db.execute(
            select(MXFFile)
            .where(MXFFile.id == mxf_id)
            .options(
                selectinload(MXFFile.audio_tracks).selectinload(AudioTrack.occurrences)
            )
        )
        mxf = result.scalars().first()
        return mxf
    
    def update_status_sync(self, db: Session, file_id: int, status: str):
        try:
            mxf = db.get(MXFFile, file_id)
            if not mxf:
                return False
            mxf.status = status
            db.commit()
            db.refresh(mxf)
            return True
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Erro ao atualizar status do MXFFile: {e}") from e
    
    def save_audio_tracks_sync(self, db: Session, mxf: MXFFile, results: list):
        """
        Versão síncrona de save_audio_tracks para uso em threads.
        """
        for r in results:
            track = AudioTrack(
                mxf_id=mxf.id,
                name=r.get("title") or r.get("track", {}).get("title"),
                album=r.get("album"),
                year=r.get("release_date"),
                authors=[r.get("artist")] if r.get("artist") else [],
                genres=[r.get("genre_primary")] if r.get("genre_primary") else [],
                isrc=r.get("isrc"),
                gmusic=r.get("google_music_url") or None,
                image_url=r.get("cover_art") or r.get("cover_art_hq")
            )
            db.add(track)
            db.flush()

            shazam_data = r.get("shazam_data") or {}
            matches = shazam_data.get("matches", [])
            for m in matches:
                tr = TimeRange(
                    audio_track_id=track.id,
                    start_time=int(m.get("offset", 0) * 1000),
                    end_time=int(m.get("offset", 0) * 1000) + r.get("segment_duration", 0)
                )
                db.add(tr)
        
        db.commit()

    def update_edl_id_sync(self, db: Session, mxf_id: int, edl_id: int) -> bool:
        """
        Atualiza o campo edl_id do MXF.
        """
        try:
            mxf = db.get(MXFFile, mxf_id)
            if not mxf:
                return False
            mxf.edl_id = edl_id
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise RuntimeError(f"Erro ao atualizar edl_id do MXFFile: {e}") from e
    
    def get_by_id_sync(self, db: Session, mxf_id: int):
        """
        GET síncrono com eager loading.
        """
        from app.model.mxf import MXFFile
        from app.model.audio_track import AudioTrack
        from sqlalchemy.orm import joinedload
        from sqlalchemy import select
        
        stmt = (
            select(MXFFile)
            .where(MXFFile.id == mxf_id)
            .options(joinedload(MXFFile.audio_tracks).joinedload(AudioTrack.occurrences))
        )
        result = db.execute(stmt)
        return result.unique().scalar_one_or_none()