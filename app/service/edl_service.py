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

    async def create_and_store_edl(
        self, db, process_id: str, source_file: str, recognition_results, 
        frame_rate: float = 29.97, drop_frame: bool = False
    ):
        edl_name = f"{Path(source_file).stem}.edl"
        edl_path = self.config.WATCHFOLDER_OUTPUT / edl_name

        # Gera os eventos
        events = self.generate_structured_events(recognition_results, source_file)
        total_events = len(events)
        validation_status = "validated" if total_events > 0 else "no_music"
        validation_errors = [] if total_events > 0 else ["No music recognized"]

        # Gera o conteúdo do EDL
        edl_content = self.generate_edl(recognition_results, source_file)

        # Salva registro no banco já com o blob
        edl_id = await self.repository.save_edl_record(
            db,
            process_id=process_id,
            edl_name=edl_name,
            path=str(edl_path),
            blob=edl_content,  # salva o EDL no banco
            frame_rate=frame_rate,
            drop_frame=drop_frame,
            total_events=total_events,
            validation_status=validation_status,
            validation_errors=validation_errors
        )

        # Salva no filesystem (opcional, para backup físico)
        saved_file = self.save_edl(edl_content, edl_path)

        # Atualiza status se houve erro no arquivo
        if not saved_file:
            await self.repository.update_status(db, edl_id, "error", ["Failed to save EDL file"])
            validation_status = "error"
        else:
            await self.repository.update_status(
                db, edl_id, validation_status, validation_errors if validation_errors else None
            )

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

    def generate_structured_events(self, recognition_results, source_file):
        events = []
        event_number = 1
        for r in recognition_results:
            if not r.get("title") or r.get("title") == "Desconhecido":
                continue
            events.append({
                "event_number": event_number,
                "reel": "AX",
                "track_type": "AX",
                "edit_type": "C",
                "source_start": r.get("source_start", "00:00:00:00"),
                "source_end": r.get("source_end", "00:00:30:00"),
                "record_start": r.get("record_start", "00:00:00:00"),
                "record_end": r.get("record_end", "00:00:30:00"),
                "clip_name": Path(source_file).name,
                "music_title": r.get("title"),
                "music_artist": r.get("artist"),
            })
            event_number += 1
        return events

    def generate_edl(self, recognition_results, source_file, format_version="1.0"):
        try:
            edl_lines = []

            edl_lines.append(f"TITLE: {source_file}")
            edl_lines.append(f"FCM: NON-DROP FRAME")
            edl_lines.append(f"CREATED: {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}")
            edl_lines.append("")

            event_number = 1
            for result in recognition_results:
                if 'title' in result and result['title'] != 'Desconhecido':
                    start_time = result.get('source_start', "00:00:00:00")
                    end_time = result.get('source_end', "00:00:30:00")
                    event_line = f"{event_number:03d}  AX       V     C        {start_time} {end_time} {start_time} {end_time}"
                    edl_lines.append(event_line)

                    music_info = self._format_music_metadata(result)
                    if music_info:
                        edl_lines.append(music_info)

                    event_number += 1

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
        
    def create_and_store_edl_sync(self, source_file: str, recognition_results):
        """
        Versão síncrona, para rodar dentro de thread separada.
        Não usa AsyncSession nem await.
        """
        edl_name = f"{Path(source_file).stem}.edl"
        edl_path = self.config.WATCHFOLDER_OUTPUT / edl_name

        events = self.generate_structured_events(recognition_results, source_file)

        edl_content = self.generate_edl(recognition_results, source_file)

        # Aqui você salva o EDL no filesystem (opcional)
        self.save_edl(edl_content, edl_path)

        # Se quiser, pode salvar em DB usando métodos sync do repository
        try:
            self.repository.save_edl_record_sync(
                process_id=Path(source_file).stem,
                edl_name=edl_name,
                path=str(edl_path),
                blob=edl_content,
                total_events=len(events)
            )
        except Exception as e:
            self.logger.error(f"Erro ao salvar EDL sync no repository: {e}")

        return events