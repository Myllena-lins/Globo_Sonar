import asyncio
from shazamio import Shazam
from pydub import AudioSegment, silence
import os
from dotenv import load_dotenv
from utils.Logger import Logger

logger = Logger()
load_dotenv()

class AudioAnalyzer:
    def __init__(self):
        self.shazam = Shazam()
        self.pasta_saida = os.getenv('PASTA_SAIDA')
    
    async def recognize_audio_file(self, file_path, stream_index):
        """
        Reconhece música usando Shazam para um arquivo de áudio
        """
        try:
            logger.registrar_info(f"🎵 Iniciando reconhecimento Shazam para stream {stream_index}: {file_path}")
            
            if not os.path.exists(file_path):
                logger.registrar_erro(f"❌ Arquivo não encontrado para reconhecimento: {file_path}")
                return None
            
            # Reconhecimento com Shazam
            result = await self.shazam.recognize(file_path)
            
            if result and 'track' in result:
                track_info = result['track']
                title = track_info.get('title', 'Desconhecido')
                artist = track_info.get('subtitle', 'Desconhecido')
                
                logger.registrar_info(f"✅ Música reconhecida - Stream {stream_index}: {artist} - {title} - resultado bruto: {result}")
                return {
                    'stream': stream_index,
                    'title': title,
                    'artist': artist,
                    'shazam_data': result
                }
            else:
                logger.registrar_aviso(f"⚠️ Música não reconhecida - Stream {stream_index}")
                return None
                
        except Exception as e:
            logger.registrar_erro(f"❌ Erro no reconhecimento Shazam - Stream {stream_index}: {e}")
            return None
    
    def split_and_analyze_music(self, file_path, stream_index, silence_thresh=-60, min_silence_len=1000):
        """
        Divide o áudio em segmentos e prepara para análise
        """
        try:
            logger.registrar_info(f"🔊 Iniciando divisão de áudio - Stream {stream_index}")
            
            audio = AudioSegment.from_wav(file_path)
            segments = silence.split_on_silence(
                audio,
                silence_thresh=silence_thresh,
                min_silence_len=min_silence_len,
                keep_silence=500  # Mantém 500ms de silêncio entre segmentos
            )
            
            logger.registrar_info(f"📊 Stream {stream_index} dividido em {len(segments)} segmentos")
            
            # Exporta segmentos
            segment_files = []
            for i, segment in enumerate(segments, start=1):
                if len(segment) > 5000:  # Só exporta segmentos com mais de 5 segundos
                    output_path = os.path.join(
                        self.pasta_saida, 
                        f'stream_{stream_index}_segment_{i}.wav'
                    )
                    segment.export(output_path, format="wav")
                    segment_files.append(output_path)
                    logger.registrar_info(f"🎶 Segmento exportado: {output_path} ({len(segment)/1000:.1f}s)")
            
            return segment_files
            
        except Exception as e:
            logger.registrar_erro(f"❌ Erro na divisão de áudio - Stream {stream_index}: {e}")
            return []
    
    async def analyze_streams(self, streams_info):
        """
        Analisa todos os streams de áudio extraídos
        """
        audio_streams = [s for s in streams_info if s.get('codec_type') == 'audio']
        
        if not audio_streams:
            logger.registrar_aviso("⚠️ Nenhum stream de áudio para análise")
            return []
        
        logger.registrar_info(f"🎵 Iniciando análise de {len(audio_streams)} streams de áudio")
        
        results = []
        for stream in audio_streams:
            stream_index = stream.get('index')
            codec = stream.get('codec_name', 'unknown')
            canais = stream.get('channels', 2)
            
            # Constrói o nome do arquivo esperado
            audio_file = os.path.join(
                self.pasta_saida, 
                f'audio_{stream_index}_{canais}c_{codec}.wav'
            )
            
            if os.path.exists(audio_file):
                # Reconhecimento direto
                recognition_result = await self.recognize_audio_file(audio_file, stream_index)
                if recognition_result:
                    results.append(recognition_result)
                
                # Divisão em segmentos (opcional)
                segments = self.split_and_analyze_music(audio_file, stream_index)
                
                # Reconhecimento para cada segmento
                for segment_file in segments:
                    segment_result = await self.recognize_audio_file(segment_file, f"{stream_index}_segment")
                    if segment_result:
                        results.append(segment_result)
            else:
                logger.registrar_aviso(f"⚠️ Arquivo de áudio não encontrado: {audio_file}")
        
        return results