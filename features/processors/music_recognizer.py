import asyncio
from shazamio import Shazam
from pydub import AudioSegment, silence
from pathlib import Path
from core.logger import Logger
from core.config import Config
from datetime import datetime

class MusicRecognizer:
    def __init__(self):
        self.shazam = Shazam()
        self.config = Config()
        self.logger = Logger()
    
    async def recognize_song(self, audio_path: Path):
        """Reconhece uma música usando Shazam e retorna metadados completos"""
        try:
            if not audio_path.exists():
                self.logger.error(f"Arquivo não encontrado: {audio_path}")
                return None
            
            self.logger.info(f"Reconhecendo música: {audio_path}")
            result = await self.shazam.recognize(str(audio_path))
            
            if result and 'track' in result:
                track = result['track']
                title = track.get('title', 'Desconhecido')
                artist = track.get('subtitle', 'Desconhecido')
                
                self.logger.info(f"Música reconhecida: {artist} - {title}")
                
                # Extrai metadados completos
                metadata = self._extract_complete_metadata(result, audio_path)
                return metadata
            
            self.logger.warning(f"Música não reconhecida: {audio_path}")
            return None
            
        except Exception as e:
            self.logger.error(f"Erro no reconhecimento Shazam: {e}")
            return None
    
    def _extract_complete_metadata(self, shazam_result, audio_path):
        """Extrai metadados completos do resultado do Shazam"""
        track = shazam_result.get('track', {})
        matches = shazam_result.get('matches', [])
        
        # Informações básicas
        metadata = {
            'title': track.get('title', 'Desconhecido'),
            'artist': track.get('subtitle', 'Desconhecido'),
            'shazam_data': shazam_result,
            'audio_file': audio_path.name,
            'recognition_time': datetime.now().isoformat()
        }
        
        # ISRC
        metadata['isrc'] = track.get('isrc')
        
        # Gêneros
        genres = track.get('genres', {})
        metadata['genre_primary'] = genres.get('primary')
        metadata['genre_secondary'] = genres.get('secondary')
        
        # Album e informações de lançamento - CORREÇÃO AQUI
        sections = track.get('sections', [])
        metadata['album'] = ''
        if sections and len(sections) > 0:
            metadata_section = sections[0].get('metadata', [])
            if metadata_section and len(metadata_section) > 0:
                # Procura por informação de álbum
                for meta in metadata_section:
                    if meta.get('title') in ['Album', 'Álbum']:
                        metadata['album'] = meta.get('text', '')
                        break
        
        metadata['release_date'] = track.get('release_date')
        metadata['label'] = track.get('label')
        
        # Duração
        metadata['duration_ms'] = track.get('duration_ms')
        
        # URL e links
        metadata['url'] = track.get('url')
        metadata['apple_music_url'] = track.get('apple_music_url')
        
        # Imagens (capa do álbum)
        images = track.get('images', {})
        metadata['cover_art'] = images.get('coverart')
        metadata['cover_art_hq'] = images.get('coverarthq')
        
        # Hub information (artistas relacionados, etc.)
        hub = track.get('hub', {})
        related_artists = []
        for artist in hub.get('artists', [])[:5]:
            if artist.get('alias'):
                related_artists.append(artist.get('alias'))
        metadata['related_artists'] = related_artists
        
        # Confidence score - CORREÇÃO AQUI
        metadata['confidence'] = 0.0
        if matches and len(matches) > 0:
            metadata['confidence'] = matches[0].get('confidence', 0) * 100
            metadata['match_offset'] = matches[0].get('offset', 0)
            metadata['match_timecode'] = matches[0].get('timecode', '')
        
        # Seções da música (letras, etc.)
        for section in sections:
            if section.get('type') == 'LYRICS':
                metadata['has_lyrics'] = True
            elif section.get('type') == 'VIDEO':
                metadata['has_video'] = True
        
        self.logger.info(f"Metadados extraídos: {metadata['artist']} - {metadata['title']} (ISRC: {metadata.get('isrc', 'N/A')})")
        return metadata
    
    def split_audio_segments(self, audio_path: Path, min_duration: int = None):
        """Divide áudio em segmentos baseado em silêncio - OTIMIZADO"""
        try:
            if min_duration is None:
                min_duration = self.config.MIN_SEGMENT_DURATION
            
            self.logger.info(f"Dividindo áudio em segmentos: {audio_path.name}")
            audio = AudioSegment.from_wav(str(audio_path))
            
            # Configurações mais agressivas para processamento mais rápido
            segments = silence.split_on_silence(
                audio,
                silence_thresh=self.config.SILENCE_THRESHOLD,
                min_silence_len=2000,  # Aumenta para 2 segundos (mais rápido)
                keep_silence=1000      # Reduz para 1 segundo entre segmentos
            )
            
            self.logger.info(f"Áudio dividido em {len(segments)} segmentos brutos")
            
            segment_files = []
            for i, segment in enumerate(segments, start=1):
                # Aumenta o mínimo para 10 segundos para evitar segmentos muito curtos
                if len(segment) > 10000:  # 10 segundos mínimo
                    output_path = self.config.PASTA_SAIDA / f"{audio_path.stem}_segment_{i}.wav"
                    segment.export(str(output_path), format="wav")
                    segment_files.append(output_path)
                    self.logger.info(f"Segmento exportado: {output_path.name} ({len(segment)/1000:.1f}s)")
            
            self.logger.info(f"Exportados {len(segment_files)} segmentos válidos")
            return segment_files
            
        except Exception as e:
            self.logger.error(f"Erro na divisão de áudio: {e}")
            return []
    
    async def recognize_audio_with_segments(self, audio_path: Path):
        """Reconhece áudio completo e seus segmentos"""
        results = []
        
        # Reconhecimento do áudio completo
        full_recognition = await self.recognize_song(audio_path)
        if full_recognition:
            full_recognition['segment_type'] = 'full'
            full_recognition['segment_duration'] = len(AudioSegment.from_wav(str(audio_path)))
            results.append(full_recognition)
        
        # Reconhecimento por segmentos
        segments = self.split_audio_segments(audio_path)
        for segment_path in segments:
            segment_recognition = await self.recognize_song(segment_path)
            if segment_recognition:
                segment_recognition['segment_type'] = 'partial'
                segment_recognition['segment_file'] = segment_path.name
                segment_recognition['segment_duration'] = len(AudioSegment.from_wav(str(segment_path)))
                results.append(segment_recognition)
        
        return results