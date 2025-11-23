import numpy as np
from scipy import signal
from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter
from pathlib import Path
from core.logger import Logger
from core.config import Config

class LightSeparator:
    def __init__(self):
        self.logger = Logger()
        self.config = Config()
    
    def separate_vocals_light(self, audio_path: Path):
        """
        Separa vocais usando filtros de frequência leves
        Método rápido mas menos preciso que Demucs
        """
        try:
            self.logger.info(f"🎵 Separando vocais (método leve): {audio_path.name}")
            
            # Carrega o áudio
            audio = AudioSegment.from_wav(str(audio_path))
            
            # Método 1: Filtro passa-alta para isolar vocais (300Hz - 3000Hz)
            vocals = self._extract_vocals_bandpass(audio)
            
            # Método 2: Redução de ruído básica
            cleaned_vocals = self._reduce_noise(vocals)
            
            # Salva os vocais processados
            output_path = self.config.PASTA_SAIDA / f"{audio_path.stem}_vocals_light.wav"
            cleaned_vocals.export(str(output_path), format="wav")
            
            self.logger.info(f"✅ Vocais leves extraídos: {output_path.name}")
            
            return {
                'vocals': output_path,
                'method': 'light_bandpass'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro na separação leve: {e}")
            return {}
    
    def _extract_vocals_bandpass(self, audio_segment):
        """Extrai vocais usando filtro bandpass"""
        # Frequências típicas de vocais humanos
        low_freq = 300   # Hz
        high_freq = 3000 # Hz
        
        # Aplica filtro passa-banda
        vocals = audio_segment.low_pass_filter(high_freq)
        vocals = vocals.high_pass_filter(low_freq)
        
        return vocals
    
    def _reduce_noise(self, audio_segment):
        """Redução básica de ruído"""
        try:
            # Aumenta um pouco o volume para compensar a filtragem
            boosted = audio_segment + 3  # +3dB
            
            # Compressão leve para uniformizar o áudio
            # (simulação básica de compressor)
            return boosted
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erro na redução de ruído: {e}")
            return audio_segment
    
    def enhance_audio_for_recognition(self, audio_path: Path):
        """
        Melhora o áudio para reconhecimento do Shazam
        sem separação complexa
        """
        try:
            self.logger.info(f"🎵 Otimizando áudio para reconhecimento: {audio_path.name}")
            
            audio = AudioSegment.from_wav(str(audio_path))
            
            # 1. Normaliza o volume
            normalized = self._normalize_audio(audio)
            
            # 2. Aplica filtro para reduzir graves muito altos
            filtered = normalized.high_pass_filter(100)  # Remove frequências abaixo de 100Hz
            
            # 3. Pequeno boost nos médios (onde geralmente estão vocais)
            # Simulado aumentando um pouco o volume geral
            enhanced = filtered + 2  # +2dB
            
            output_path = self.config.PASTA_SAIDA / f"{audio_path.stem}_enhanced.wav"
            enhanced.export(str(output_path), format="wav")
            
            self.logger.info(f"✅ Áudio otimizado: {output_path.name}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"❌ Erro na otimização de áudio: {e}")
            return audio_path
    
    def _normalize_audio(self, audio_segment):
        """Normaliza o volume do áudio"""
        try:
            # Pega a amplitude máxima
            max_dBFS = audio_segment.dBFS
            target_dBFS = -20.0  # Nível alvo
            
            # Calcula quanto precisa aumentar/diminuir
            change_in_dBFS = target_dBFS - max_dBFS
            
            # Aplica a normalização (limita a +/- 10dB para não distorcer)
            change_in_dBFS = max(min(change_in_dBFS, 10), -10)
            
            return audio_segment.apply_gain(change_in_dBFS)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erro na normalização: {e}")
            return audio_segment