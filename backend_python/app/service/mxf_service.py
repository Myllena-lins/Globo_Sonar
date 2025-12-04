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
import threading
from core.database import SessionLocal
from app.model.mxf import MXFFile
from app.model.audio_track import AudioTrack

class MXFService:
    def __init__(self, repository: MXFRepository, edl_service: EDLService = None):
        self.repository = repository
        self.logger = Logger()
        self.workflows = [UnmixedAudioWorkflow(), MixedAudioWorkflow()]
        self.edl_service = edl_service or EDLService(EDLRepository())

    async def create_mxf_record(self, db: AsyncSession, file_name: str, file_path: str):
        return await self.repository.save_file_record(db, file_name, file_path)

    async def run_workflow_with_edl(self, db, file_path: Path, mxf_id: int | None = None):
        """Executa o workflow e retorna results (não gera EDL aqui)."""
        processor = MXFProcessor()
        streams = processor.get_streams(file_path)

        workflow = next((wf for wf in self.workflows if wf.can_handle(streams)), None)
        if not workflow:
            return []

        results = await workflow.process(file_path)
        return results

    async def process_file_in_background(self, db_session_factory, mxf_id: int, file_path):
        """
        Agenda processamento em thread separada (não bloqueia event loop do FastAPI).
        """
        self.logger.info(f"Agendando processamento em thread separada para mxf_id={mxf_id}")
        
        threading.Thread(
            target=self._run_in_new_loop,
            args=(mxf_id, file_path),
            daemon=False
        ).start()

    def _run_in_new_loop(self, mxf_id: int, file_path):
        """
        Cria nova event loop e executa o worker nela (thread separada).
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                self._process_file_worker(mxf_id, file_path)
            )
        finally:
            loop.close()

    async def _process_file_worker(self, mxf_id: int, file_path):
        """
        Worker real que executa o processamento (rodando em thread separada com event loop própria).
        Usa SessionLocal (síncrono) para evitar problemas com AsyncSession em thread diferente.
        """
        db_sync = None
        try:
            db_sync = SessionLocal()
            
            mxf = db_sync.query(MXFFile).filter(MXFFile.id == mxf_id).first()
            if not mxf:
                self._update_status_sync(mxf_id, "error", db_sync)
                self.logger.error(f"MXF id={mxf_id} não encontrado")
                return

            results = await self.run_workflow_with_edl(db_sync, Path(file_path), mxf.id)

            try:
                self.repository.save_audio_tracks_sync(db_sync, mxf, results)
                self.logger.info(f"Audio tracks salvos para mxf_id={mxf_id}")
            except Exception as e:
                db_sync.rollback()
                self.logger.error(f"Erro ao salvar audio_tracks: {e}")
                self._update_status_sync(mxf_id, "error", db_sync)
                return

            try:
                edl_id = self.edl_service.create_and_store_edl_sync(
                    source_file=Path(file_path).name,
                    timestamp_table=None,
                    recognition_results=results,
                    mxf_id=mxf.id
                )
                self.logger.info(f"EDL gerado para mxf_id={mxf_id}, edl_id={edl_id}")
                
                if edl_id:
                    self.repository.update_edl_id_sync(db_sync, mxf_id, edl_id)
            except Exception as e:
                self.logger.error(f"Erro ao criar EDL: {e}")

            self._update_status_sync(mxf_id, "processed", db_sync)
            self.logger.info(f"Processamento concluído para mxf_id={mxf_id}")

        except Exception as e:
            self.logger.error(f"Erro fatal em _process_file_worker: {e}", exc_info=True)
            self._update_status_sync(mxf_id, "error", db_sync)
        finally:
            if db_sync:
                db_sync.close()

    def _update_status_sync(self, mxf_id: int, status: str, db = None):
        """
        Atualiza status do MXF usando sessão síncrona.
        """
        close_db = False
        try:
            if db is None:
                db = SessionLocal()
                close_db = True
            
            self.repository.update_status_sync(db, mxf_id, status)
            self.logger.info(f"MXF id={mxf_id} status atualizado para '{status}'")
        except Exception as e:
            self.logger.error(f"Erro ao atualizar status sync mxf_id={mxf_id}: {e}")
        finally:
            if close_db and db:
                db.close()