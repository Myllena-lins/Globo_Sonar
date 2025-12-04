from pathlib import Path
from datetime import datetime
from core.config import Config
from core.logger import Logger
from app.repository.edl_repository import EDLRepository
from core.database import SessionLocal  
from app.repository.mxf_repository import MXFRepository
from sqlalchemy.orm import Session
import asyncio

class EDLService:

    def __init__(self, repository: EDLRepository):
        self.repository = repository
        self.logger = Logger()
        self.config = Config()

    async def create_and_store_edl(
        self, db, process_id: str, source_file: str, recognition_results,
        frame_rate: float = 29.97, drop_frame: bool = False,
        mxf_id: int | None = None
    ):
        edl_name = f"{Path(source_file).stem}.edl"
        edl_path = self.config.WATCHFOLDER_OUTPUT / edl_name

        self.logger.debug("create_and_store_edl: entry")
        self.logger.debug(f"create_and_store_edl: calling repository.get_all_timestamps for db")
        timestamps = await self.repository.get_all_timestamps(db)
        self.logger.debug(f"create_and_store_edl: got timestamps count={len(timestamps)}")
        for i, t in enumerate(timestamps):
            self.logger.debug(f" timestamp[{i}] = {t}")

        timestamps_by_track = {t["audio_track_id"]: t for t in (timestamps or []) if t.get("audio_track_id") is not None}
        self.logger.debug(f"timestamps_by_track mapping keys: {list(timestamps_by_track.keys())}")

        if not timestamps_by_track:
            self.logger.debug("timestamps_by_track empty — tentando fallback por audio_track_id nos recognition_results")
            for r in recognition_results:
                audio_track_id = r.get("audio_track_id")
                if audio_track_id is None:
                    continue
                try:
                    ts = await self.repository.get_timestamp_by_audio_track_id(db, audio_track_id)
                    self.logger.debug(f" fallback fetched for audio_track_id={audio_track_id}: {ts}")
                    if ts:
                        timestamps_by_track[audio_track_id] = ts
                except Exception as e:
                    self.logger.error(f"Erro no fallback get_timestamp_by_audio_track_id for {audio_track_id}: {e}")

        self.logger.debug(f"final timestamps_by_track keys: {list(timestamps_by_track.keys())}")

        if timestamps_by_track and all(r.get("audio_track_id") is None for r in recognition_results):
            keys = list(timestamps_by_track.keys())
            self.logger.debug(f"recognition_results sem audio_track_id — atribuindo a partir de timestamps_by_track keys={keys}")
            for i, r in enumerate(recognition_results):
                assigned = keys[i % len(keys)]
                r["audio_track_id"] = assigned
                self.logger.debug(f" assigned recognition_result[{i}].audio_track_id = {assigned}")

        events = self.generate_structured_events(recognition_results, source_file, timestamps_by_track)
        total_events = len(events)
        validation_status = "validated" if total_events > 0 else "no_music"
        validation_errors = [] if total_events > 0 else ["No music recognized"]

        edl_content = self.generate_edl(recognition_results, source_file, timestamps_by_track)

        try:
            edl_id = await self.repository.save_edl_record(
                db,
                process_id=process_id,
                edl_name=edl_name,
                path=str(edl_path),
                blob=edl_content,
                frame_rate=frame_rate,
                drop_frame=drop_frame,
                total_events=total_events,
                validation_status=validation_status,
                validation_errors=validation_errors
            )
        except Exception as e:
            self.logger.error(f"Erro ao salvar EDL no banco: {e}")
            edl_id = None

        if mxf_id and edl_id:
            try:
                await self.repository.update_status(db, edl_id, validation_status)  # opcional
            except Exception:
                pass

        return edl_id

    def _ms_to_hhmmss(self, ms) -> str:
        """
        Converte milissegundos (int/str/float) para 'HH:MM:SS'.
        Se ms for None ou inválido, retorna '00:00:00'.
        """
        if ms is None:
            return "00:00:00"
        try:
            total_ms = int(float(ms))
        except Exception:
            return "00:00:00"
        total_seconds = total_ms // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def generate_structured_events(self, recognition_results, source_file, timestamps_by_track=None):
        events = []
        event_number = 1
        self.logger.debug(f"Generating structured events with timestamps_by_track present: {bool(timestamps_by_track)}")
        for idx, r in enumerate(recognition_results):
            if not r.get("title") or r.get("title") == "Desconhecido":
                self.logger.debug(f" skip result[{idx}] missing/unknown title: {r.get('title')}")
                continue
            audio_track_id = r.get("audio_track_id")
            timestamp = None
            if audio_track_id is not None and timestamps_by_track:
                timestamp = timestamps_by_track.get(audio_track_id)
            self.logger.debug(f" result[{idx}] lookup audio_track_id={audio_track_id} -> timestamp={timestamp}")

            start = self._ms_to_hhmmss(timestamp.get("start_time")) if timestamp else "00:00:00"
            end = self._ms_to_hhmmss(timestamp.get("end_time")) if timestamp else "00:00:00"

            events.append({
                "event_number": event_number,
                "reel": "AX",
                "track_type": "AX",
                "edit_type": "C",
                "source_start": start,
                "source_end": end,
                "record_start": start,
                "record_end": end,
                "clip_name": Path(source_file).name,
                "music_title": r.get("title"),
                "music_artist": r.get("artist"),
                "audio_track_id": audio_track_id,
            })
            event_number += 1
        return events

    def generate_edl(self, recognition_results, source_file, timestamps_by_track=None, format_version="1.0"):
        try:
            edl_lines = []
            edl_lines.append(f"TITLE: {source_file}")
            edl_lines.append(f"FCM: NON-DROP FRAME")
            edl_lines.append(f"CREATED: {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}")
            edl_lines.append("")

            self.logger.debug(f"Generating EDL with timestamps_by_track present: {bool(timestamps_by_track)}")
            event_number = 1
            for result in recognition_results:
                if 'title' in result and result['title'] != 'Desconhecido':
                    audio_track_id = result.get("audio_track_id")
                    timestamp = (timestamps_by_track or {}).get(audio_track_id) if audio_track_id is not None else None

                    start_time = self._ms_to_hhmmss(timestamp.get("start_time")) if timestamp else "00:00:00"
                    end_time = self._ms_to_hhmmss(timestamp.get("end_time")) if timestamp else "00:00:00"
                    event_line = f"{event_number:03d}  AX       V     C        {start_time} {end_time} {start_time} {end_time}"
                    edl_lines.append(event_line)

                    music_info = self._format_music_metadata(result)
                    if music_info:
                        edl_lines.append(music_info)

                    event_number = 1

            if event_number == 1:
                edl_lines.append("*** NO MUSIC RECOGNIZED ***")

            return "\n".join(edl_lines)

        except Exception as e:
            self.logger.error(f"Erro ao gerar EDL: {e}")
            return f"ERROR: {e}"

    def _format_music_metadata(self, result):
        metadata_lines = []

        artist = result.get('artist', 'Artista Desconhecido')
        title = result.get('title', 'Título Desconhecido')
        metadata_lines.append(f" |MUSIC: {artist} - {title}")

        if result.get('segment_type') == 'partial':
            segment_file = result.get('segment_file', '')
            metadata_lines.append(f" |SEGMENT: {segment_file}")

        shazam_data = result.get('shazam_data', {}) or {}
        track_info = shazam_data.get('track', {}) or {}

        isrc = track_info.get('isrc') or result.get('isrc')
        if isrc:
            metadata_lines.append(f" |ISRC: {isrc}")

        genres = track_info.get('genres', {}).get('primary') or result.get('genre_primary')
        if genres:
            metadata_lines.append(f" |GENRE: {genres}")

        album = result.get('album', '')
        if album and album != title:
            metadata_lines.append(f" |ALBUM: {album}")

        release_date = track_info.get('release_date') or result.get('release_date')
        if release_date:
            year = release_date.split('-')[0] if '-' in release_date else release_date
            metadata_lines.append(f" |YEAR: {year}")

        label = track_info.get('label') or result.get('label')
        if label:
            metadata_lines.append(f" |LABEL: {label}")

        duration_ms = track_info.get('duration_ms') or result.get('duration_ms')
        if duration_ms:
            try:
                duration_ms = int(duration_ms)
                duration_sec = duration_ms // 1000
                minutes = duration_sec // 60
                seconds = duration_sec % 60
                metadata_lines.append(f" |DURATION: {minutes}:{seconds:02d}")
            except Exception:
                pass

        stream_index = result.get('stream_index', 'N/A')
        workflow = result.get('workflow', 'N/A')
        strategy = result.get('processing_strategy', 'N/A')
        metadata_lines.append(f" |SOURCE: Stream {stream_index} - {workflow} ({strategy})")

        confidence = result.get('confidence', 0)
        if confidence and confidence > 0:
            try:
                metadata_lines.append(f" |CONFIDENCE: {float(confidence):.1f}%")
            except Exception:
                metadata_lines.append(f" |CONFIDENCE: {confidence}")
        else:
            matches = shazam_data.get('matches', [])
            if matches and len(matches) > 0:
                try:
                    conf = matches[0].get('confidence', 0) * 100
                    if conf > 0:
                        metadata_lines.append(f" |CONFIDENCE: {conf:.1f}%")
                except Exception:
                    pass

        url = track_info.get('url') or result.get('url')
        if url:
            metadata_lines.append(f" |URL: {url}")

        related_artists = result.get('related_artists', [])
        if related_artists:
            metadata_lines.append(f" |RELATED_ARTISTS: {', '.join(related_artists)}")

        return "\n".join(metadata_lines)

    def save_edl(self, edl_content, output_path: Path):
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(edl_content)
            self.logger.info(f"EDL salvo: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar EDL: {e}")
            return False
        
    def create_and_store_edl_sync(self, source_file: str, timestamp_table, recognition_results, mxf_id: int | None = None):
        """
        Versão síncrona: salva EDL e retorna o id do registro (int) ou None em caso de falha.
        """
        edl_name = f"{Path(source_file).stem}.edl"
        edl_path = self.config.WATCHFOLDER_OUTPUT / edl_name

        events = self.generate_structured_events(recognition_results, source_file, timestamp_table)
        total_events = len(events)
        validation_status = "validated" if total_events > 0 else "no_music"
        validation_errors = [] if total_events > 0 else ["No music recognized"]
        edl_content = self.generate_edl(recognition_results, source_file, timestamp_table)

        try:
            self.save_edl(edl_content, edl_path)
        except Exception:
            pass

        db = None
        edl_id = None
        try:
            db = SessionLocal()
        except Exception as e:
            self.logger.error(f"Não foi possível abrir sessão sync: {e}")
            return None

        try:
            edl_id = self.repository.save_edl_record_sync(
                db,
                process_id=Path(source_file).stem,
                edl_name=edl_name,
                path=str(edl_path),
                blob=edl_content,
                total_events=total_events,
                validation_status=validation_status,
                validation_errors=validation_errors
            )
            saved_file = True
            try:
                saved_file = self.save_edl(edl_content, edl_path)
            except Exception:
                saved_file = False

            if not saved_file:
                try:
                    self.repository.update_status_sync(db, edl_id, "error", ["Failed to save EDL file"])
                    validation_status = "error"
                except Exception:
                    pass
            else:
                try:
                    self.repository.update_status_sync(db, edl_id, validation_status, validation_errors if validation_errors else None)
                except Exception:
                    pass

            if mxf_id and edl_id:
                try:
                    db2 = SessionLocal()
                    try:
                        updated = MXFRepository().update_edl_id_sync(db2, mxf_id, edl_id)
                        if updated:
                            self.logger.info(f"MXF id={mxf_id} vinculado ao EDL id={edl_id}")
                        else:
                            self.logger.warning(f"Nenhum MXF encontrado para id={mxf_id} ao tentar vincular EDL id={edl_id}")
                    finally:
                        db2.close()
                except Exception as e:
                    self.logger.error(f"Erro ao atualizar MXF.edl_id (sync flow): {e}")

            return edl_id
        except Exception as e:
            self.logger.error(f"Erro ao salvar EDL sync no repository: {e}")
            try:
                db.rollback()
            except Exception:
                pass
            return None
        finally:
            try:
                if db:
                    db.close()
            except Exception:
                pass
    
    def get_timestamp(self, db):
        return self.repository.get_timestamp(db)