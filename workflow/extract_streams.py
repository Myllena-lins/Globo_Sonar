import subprocess
import os
import asyncio
from dotenv import load_dotenv
from utils.Logger import Logger
from workflow.audio_analysis import AudioAnalyzer

logger = Logger()
load_dotenv()

ffmpeg_path = os.getenv('FFMPEG_PATH')
arquivo_mxf = os.getenv('ARQUIVO_MXF')
pasta_saida = os.getenv('PASTA_SAIDA')

def extrair_audio(streams):
    """Extrai todos os streams de áudio do arquivo MXF"""
    streams_audio = [s for s in streams if s.get('codec_type') == 'audio']
    
    if not streams_audio:
        logger.registrar_erro("❌ Nenhum stream de áudio encontrado.")
        return []
    
    logger.registrar_info(f"🎵 Encontrados {len(streams_audio)} streams de áudio para extração.")
    
    extracted_files = []
    
    for stream in streams_audio:
        indice = stream.get('index')
        codec = stream.get('codec_name', 'unknown')
        canais = stream.get('channels', 2)
        
        saida_wav = os.path.join(pasta_saida, f'audio_{indice}_{canais}c_{codec}.wav')

        cmd_extract = [
            ffmpeg_path,
            '-i', arquivo_mxf,
            '-map', f'0:{indice}',
            '-c:a', 'pcm_s16le',
            '-y',
            saida_wav
        ]

        result_extract = subprocess.run(cmd_extract, capture_output=True, text=True)
        if result_extract.returncode != 0:
            logger.registrar_erro(f"❌ Erro ao extrair stream {indice}: {result_extract.stderr}")
        else:
            logger.registrar_info(f"✅ Stream {indice} extraída com sucesso: {saida_wav}")
            extracted_files.append(saida_wav)
    
    return extracted_files

async def processar_audio_com_shazam(streams):
    """
    Processa os streams extraídos com Shazam para reconhecimento musical
    """
    try:
        analyzer = AudioAnalyzer()
        results = await analyzer.analyze_streams(streams)
        
        # Log dos resultados
        if results:
            logger.registrar_info("🎉 RESUMO DO RECONHECIMENTO MUSICAL:")
            for result in results:
                logger.registrar_info(f"   🎵 {result['artist']} - {result['title']} (Stream {result['stream']})")
        else:
            logger.registrar_aviso("📭 Nenhuma música reconhecida")
            
        return results
        
    except Exception as e:
        logger.registrar_erro(f"❌ Erro no processamento Shazam: {e}")
        return []