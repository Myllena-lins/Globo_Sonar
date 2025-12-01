from features.workflows.base_workflow import BaseWorkflow
from features.processors.audio_extractor import AudioExtractor
from features.processors.music_recognizer import MusicRecognizer
from features.processors.light_separator import LightSeparator
from core.file_processor import MXFProcessor
from pathlib import Path

class MixedAudioWorkflow(BaseWorkflow):
    """Processa MXFs mixados usando métodos leves de separação"""
    
    def __init__(self):
        super().__init__()
        self.light_separator = LightSeparator()
        self.recognizer = MusicRecognizer()  # ← ADICIONAR ESTA LINHA
    
    def can_handle(self, streams) -> bool:
        audio_streams = [s for s in streams if s.get('codec_type') == 'audio']
        is_likely_mixed = len(audio_streams) <= 2
        
        if is_likely_mixed:
            self.logger.info(f"🎵 Workflow MixedAudio: {len(audio_streams)} tracks - provavelmente mixado")
        else:
            self.logger.info(f"🎵 Workflow MixedAudio: {len(audio_streams)} tracks - muito para ser mixado")
        
        return is_likely_mixed
    
    async def process(self, mxf_path: Path):
        self.logger.info(f"🎵 Iniciando processamento MXF mixado (LEVE): {mxf_path.name}")
        
        processor = MXFProcessor()
        extractor = AudioExtractor()
        
        streams = processor.get_streams(mxf_path)
        all_results = []
        
        # Extrai o áudio mixado
        extracted_files = extractor.extract_all_audio_streams(mxf_path)
        if not extracted_files:
            self.logger.error("❌ Nenhum áudio extraído para processamento")
            return all_results
        
        mixed_audio_info = extracted_files[0]
        mixed_audio_path = mixed_audio_info['path']
        
        self.logger.info(f"🎵 Áudio mixado extraído: {mixed_audio_path.name}")
        
        # Estratégia: Tentar métodos progressivamente mais complexos
        results = await self._try_processing_strategies(mixed_audio_path, mxf_path, mixed_audio_info)
        all_results.extend(results)
        
        # Limpeza
        self._cleanup_temp_files(mixed_audio_path)
        
        self.logger.info(f"✅ Processamento mixado concluído. {len(all_results)} resultados encontrados")
        return all_results
    
    async def _try_processing_strategies(self, mixed_audio_path: Path, mxf_path: Path, audio_info: dict):
        """Tenta diferentes estratégias de processamento"""
        all_results = []
        
        # Estratégia 1: Reconhecimento direto no áudio original
        self.logger.info("🎯 Estratégia 1: Reconhecimento direto")
        direct_results = await self._process_direct(mixed_audio_path, mxf_path, audio_info)
        all_results.extend(direct_results)
        
        if len(direct_results) < 2:  # Se poucas músicas foram detectadas
            # Estratégia 2: Áudio otimizado
            self.logger.info("🎯 Estratégia 2: Áudio otimizado")
            enhanced_path = self.light_separator.enhance_audio_for_recognition(mixed_audio_path)
            enhanced_results = await self._process_enhanced(enhanced_path, mxf_path, audio_info)
            all_results.extend(enhanced_results)
            
            if len(enhanced_results) < 2:
                # Estratégia 3: Separação leve de vocais
                self.logger.info("🎯 Estratégia 3: Separação leve de vocais")
                separation_result = self.light_separator.separate_vocals_light(mixed_audio_path)
                if separation_result:
                    vocals_path = separation_result.get('vocals')
                    if vocals_path and vocals_path.exists():
                        vocals_results = await self._process_vocals(vocals_path, mxf_path, audio_info, separation_result)
                        all_results.extend(vocals_results)
        
        return all_results
    
    async def _process_direct(self, audio_path: Path, mxf_path: Path, audio_info: dict):
        """Processa o áudio original diretamente"""
        results = await self.recognizer.recognize_audio_with_segments(audio_path)
        for result in results:
            result.update({
                'source_file': mxf_path.name,
                'stream_index': audio_info['stream_index'],
                'channels': audio_info['channels'],
                'workflow': 'mixed_direct',
                'processing_strategy': 'direct'
            })
        return results
    
    async def _process_enhanced(self, enhanced_path: Path, mxf_path: Path, audio_info: dict):
        """Processa áudio otimizado"""
        results = await self.recognizer.recognize_audio_with_segments(enhanced_path)
        for result in results:
            result.update({
                'source_file': mxf_path.name,
                'stream_index': audio_info['stream_index'],
                'channels': audio_info['channels'],
                'workflow': 'mixed_enhanced',
                'processing_strategy': 'enhanced'
            })
        
        # Limpa arquivo temporário enhanced (se for diferente do original)
        try:
            if enhanced_path != audio_path and enhanced_path.exists():
                enhanced_path.unlink()
                self.logger.info(f"🧹 Arquivo enhanced removido: {enhanced_path.name}")
        except Exception as e:
            self.logger.warning(f"⚠️ Não foi possível remover enhanced: {e}")
            
        return results
    
    async def _process_vocals(self, vocals_path: Path, mxf_path: Path, audio_info: dict, separation_result: dict):
        """Processa vocais separados"""
        results = await self.recognizer.recognize_audio_with_segments(vocals_path)
        for result in results:
            result.update({
                'source_file': mxf_path.name,
                'stream_index': 'vocals_light',
                'channels': 2,
                'workflow': 'mixed_light_separation',
                'processing_strategy': 'vocals_separation',
                'separation_method': separation_result.get('method', 'light')
            })
        
        # Limpa arquivo temporário de vocais
        try:
            if vocals_path.exists():
                vocals_path.unlink()
                self.logger.info(f"🧹 Arquivo vocals removido: {vocals_path.name}")
        except Exception as e:
            self.logger.warning(f"⚠️ Não foi possível remover vocals: {e}")
            
        return results
    
    def _cleanup_temp_files(self, mixed_audio_path: Path):
        """Limpa arquivos temporários"""
        try:
            if mixed_audio_path.exists():
                mixed_audio_path.unlink()
                self.logger.info(f"🧹 Arquivo temporário removido: {mixed_audio_path.name}")
        except Exception as e:
            self.logger.warning(f"⚠️ Não foi possível remover arquivo temporário: {e}")