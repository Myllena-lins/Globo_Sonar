from datetime import datetime
from pathlib import Path
from core.logger import Logger

class EDLGenerator:
    def __init__(self):
        self.logger = Logger()
    
    def generate_edl(self, recognition_results, source_file, format_version="1.0"):
        """Gera arquivo EDL com metadados completos do Shazam"""
        try:
            edl_content = []
            
            # Header
            edl_content.append(f"TITLE: {source_file}")
            edl_content.append(f"FCM: NON-DROP FRAME")
            edl_content.append(f"CREATED: {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}")
            edl_content.append("")
            
            # Eventos
            event_number = 1
            for result in recognition_results:
                if 'title' in result and result['title'] != 'Desconhecido':
                    # Linha do evento
                    event_line = f"{event_number:03d}  AX       V     C        "
                    
                    # Timecode (placeholder - precisa ser calculado baseado no tempo real)
                    start_time = "00:00:00:00"
                    end_time = "00:00:30:00"  # Exemplo fixo - precisa ser calculado
                    
                    event_line += f"{start_time} {end_time} {start_time} {end_time}"
                    edl_content.append(event_line)
                    
                    # Metadados da música
                    music_info = self._format_music_metadata(result)
                    edl_content.append(music_info)
                    
                    event_number += 1
            
            if event_number == 1:
                edl_content.append("*** NO MUSIC RECOGNIZED ***")
            
            return "\n".join(edl_content)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar EDL: {e}")
            return f"ERROR: {e}"
    
    def _format_music_metadata(self, result):
        """Formata os metadados completos da música"""
        metadata_lines = []
        
        # Informações básicas
        artist = result.get('artist', 'Artista Desconhecido')
        title = result.get('title', 'Título Desconhecido')
        
        metadata_lines.append(f" |MUSIC: {artist} - {title}")
        
        # Tipo de reconhecimento
        if result.get('segment_type') == 'partial':
            segment_file = result.get('segment_file', '')
            metadata_lines.append(f" |SEGMENT: {segment_file}")
        
        # Metadados do Shazam
        shazam_data = result.get('shazam_data', {})
        track_info = shazam_data.get('track', {})
        
        # ISRC
        isrc = track_info.get('isrc') or result.get('isrc')
        if isrc:
            metadata_lines.append(f" |ISRC: {isrc}")
        
        # Gênero
        genres = track_info.get('genres', {}).get('primary') or result.get('genre_primary')
        if genres:
            metadata_lines.append(f" |GENRE: {genres}")
        
        # Album
        album = result.get('album', '')
        if album and album != title:  # Só adiciona se for diferente do título
            metadata_lines.append(f" |ALBUM: {album}")
        
        # Ano de lançamento
        release_date = track_info.get('release_date') or result.get('release_date')
        if release_date:
            # Extrai apenas o ano se for uma data completa
            year = release_date.split('-')[0] if '-' in release_date else release_date
            metadata_lines.append(f" |YEAR: {year}")
        
        # Label
        label = track_info.get('label') or result.get('label')
        if label:
            metadata_lines.append(f" |LABEL: {label}")
        
        # Duração da música
        duration_ms = track_info.get('duration_ms') or result.get('duration_ms')
        if duration_ms:
            duration_sec = duration_ms // 1000
            minutes = duration_sec // 60
            seconds = duration_sec % 60
            metadata_lines.append(f" |DURATION: {minutes}:{seconds:02d}")
        
        # Stream index e workflow
        stream_index = result.get('stream_index', 'N/A')
        workflow = result.get('workflow', 'N/A')
        strategy = result.get('processing_strategy', 'N/A')
        metadata_lines.append(f" |SOURCE: Stream {stream_index} - {workflow} ({strategy})")
        
        # Shazam confidence - CORREÇÃO AQUI
        confidence = result.get('confidence', 0)
        if confidence > 0:
            metadata_lines.append(f" |CONFIDENCE: {confidence:.1f}%")
        else:
            # Tenta pegar do matches se não estiver no result
            matches = shazam_data.get('matches', [])
            if matches and len(matches) > 0:
                confidence = matches[0].get('confidence', 0) * 100
                if confidence > 0:
                    metadata_lines.append(f" |CONFIDENCE: {confidence:.1f}%")
        
        # URL da música (se disponível)
        url = track_info.get('url') or result.get('url')
        if url:
            metadata_lines.append(f" |URL: {url}")
        
        # Artistas relacionados
        related_artists = result.get('related_artists', [])
        if related_artists:
            metadata_lines.append(f" |RELATED_ARTISTS: {', '.join(related_artists)}")
        
        return "\n".join(metadata_lines)
    
    def save_edl(self, edl_content, output_path: Path):
        """Salva conteúdo EDL em arquivo"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(edl_content)
            self.logger.info(f"EDL salvo: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar EDL: {e}")
            return False