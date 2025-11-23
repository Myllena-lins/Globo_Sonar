from pathlib import Path
import json
import subprocess
from core.config import Config
from core.logger import Logger

class MXFProcessor:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
    
    def get_streams(self, file_path: Path):
        """Obtém informações dos streams do arquivo MXF"""
        try:
            cmd = [
                self.config.FFPROBE_PATH,
                '-v', 'error',
                '-show_entries', 'stream=index,codec_type,codec_name,channels,duration,bit_rate,tags:stream_tags',
                '-of', 'json',
                str(file_path)
            ]
            
            self.logger.info(f"Analisando streams do arquivo: {file_path}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Erro no ffprobe: {result.stderr}")
            
            data = json.loads(result.stdout)
            streams = data.get('streams', [])
            self.logger.info(f"Encontrados {len(streams)} streams")
            return streams
            
        except Exception as e:
            self.logger.error(f"Erro ao obter streams: {e}")
            return []
    
    def extract_audio_stream(self, file_path: Path, stream_index: int, output_path: Path):
        """Extrai um stream de áudio específico"""
        try:
            cmd = [
                self.config.FFMPEG_PATH,
                '-i', str(file_path),
                '-map', f'0:{stream_index}',
                '-c:a', 'pcm_s16le',
                '-y',
                str(output_path)
            ]
            
            self.logger.info(f"Extraindo stream {stream_index} para: {output_path}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Erro ao extrair stream {stream_index}: {result.stderr}")
            
            self.logger.info(f"Stream {stream_index} extraído com sucesso")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Erro na extração do stream {stream_index}: {e}")
            raise