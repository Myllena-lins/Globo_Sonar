from workflows.base_workflow import BaseWorkflow
from processors.audio_extractor import AudioExtractor
from processors.music_recognizer import MusicRecognizer
from core.file_processor import MXFProcessor
from pathlib import Path

class UnmixedAudioWorkflow(BaseWorkflow):
    """Processa MXFs não mixados (trilhas separadas por tracks)"""
    
    def can_handle(self, streams) -> bool:
        audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
        has_multiple_tracks = len(audio_streams) >= 4
        
        if has_multiple_tracks:
            self.logger.info(f"Workflow UnmixedAudio: {len(audio_streams)} tracks de áudio detectadas")
        else:
            self.logger.info(f"Workflow UnmixedAudio: Apenas {len(audio_streams)} tracks - insuficiente")
        
        return has_multiple_tracks
    
    async def process(self, mxf_path: Path):
        self.logger.info(f"Iniciando processamento MXF não mixado: {mxf_path.name}")
        
        processor = MXFProcessor()
        extractor = AudioExtractor()
        recognizer = MusicRecognizer()
        
        streams = processor.get_streams(mxf_path)
        all_results = []
        
        # Extrai todos os streams de áudio
        extracted_files = extractor.extract_all_audio_streams(mxf_path)
        
        # Processa cada stream extraído
        for file_info in extracted_files:
            stream_index = file_info['stream_index']
            file_path = file_info['path']
            
            self.logger.info(f"Processando stream {stream_index}: {file_path.name}")
            
            # Reconhecimento musical
            stream_results = await recognizer.recognize_audio_with_segments(file_path)
            
            # Adiciona metadados do stream
            for result in stream_results:
                result.update({
                    'source_file': mxf_path.name,
                    'stream_index': stream_index,
                    'channels': file_info['channels'],
                    'workflow': 'unmixed'
                })
                all_results.append(result)
        
        self.logger.info(f"Processamento concluído. {len(all_results)} resultados encontrados")
        return all_results