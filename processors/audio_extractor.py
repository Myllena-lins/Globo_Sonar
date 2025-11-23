from pathlib import Path
from core.file_processor import MXFProcessor
from core.logger import Logger

class AudioExtractor:
    def __init__(self):
        self.processor = MXFProcessor()
        self.logger = Logger()
    
    def extract_all_audio_streams(self, mxf_path: Path):
        """Extrai todos os streams de áudio do MXF"""
        try:
            streams = self.processor.get_streams(mxf_path)
            audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
            
            if not audio_streams:
                self.logger.warning("Nenhum stream de áudio encontrado")
                return []
            
            self.logger.info(f"Encontrados {len(audio_streams)} streams de áudio")
            
            extracted_files = []
            for stream in audio_streams:
                stream_index = stream.get('index')
                codec = stream.get('codec_name', 'unknown')
                channels = stream.get('channels', 2)
                
                output_filename = f"audio_{stream_index}_{channels}c_{codec}_{mxf_path.stem}.wav"
                output_path = self.processor.config.PASTA_SAIDA / output_filename
                
                try:
                    extracted_path = self.processor.extract_audio_stream(mxf_path, stream_index, output_path)
                    extracted_files.append({
                        'path': extracted_path,
                        'stream_index': stream_index,
                        'channels': channels,
                        'codec': codec
                    })
                except Exception as e:
                    self.logger.error(f"Falha ao extrair stream {stream_index}: {e}")
                    continue
            
            return extracted_files
            
        except Exception as e:
            self.logger.error(f"Erro na extração de áudio: {e}")
            return []