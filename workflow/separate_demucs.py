import subprocess
from pathlib import Path
from utils.Logger import Logger

logger = Logger()

def separar_com_demucs():
    """
    Roda o Demucs para separar vocais, bateria, baixo, etc.
    """
    try:

        audio_path = Path("files/streams/wav")
        output_dir = Path("files/songs/wav")
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            "demucs",
            "-n", "htdemucs",
            "-o", str(output_dir),
            str(audio_path)
        ]

        logger.registrar_info(f"🎶 Executando Demucs em: {audio_path}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.registrar_erro(f"❌ Erro no Demucs: {result.stderr}")
        else:
            logger.registrar_info(f"✅ Separação concluída — resultados em {output_dir}")

    except Exception as e:
        logger.registrar_erro(f"⚠️ Erro ao rodar Demucs: {e}")



# logger.registrar_info("🔍 Analisando canais de áudio...")

# probe = subprocess.run(
#     ["ffprobe", "-v", "error", "-show_streams", "-select_streams", "a", "-of", "json", mxf_file],
#     capture_output=True, text=True
# )

# streams = json.loads(probe.stdout).get("streams", [])
# num_streams = len(streams)
# logger.registrar_info(f"🎚️ Número de streams de áudio detectados: {num_streams}")

# if num_streams > 1:
#     amerge_inputs = ''.join(f"[0:a:{i}]" for i in range(num_streams))
#     amerge_filter = f"{amerge_inputs}amerge=inputs={num_streams}[aout]"
#     ffmpeg_cmd = [
#         "ffmpeg", "-i", mxf_file,
#         "-filter_complex", amerge_filter,
#         "-map", "[aout]",
#         "-ac", "2", "-ar", "44100",
#         wav_file, "-y"
#     ]
# else:
#     ffmpeg_cmd = [
#         "ffmpeg", "-i", mxf_file,
#         "-map", "0:a:0",
#         "-ac", "2", "-ar", "44100",
#         wav_file, "-y"
#     ]

# logger.registrar_info("🎬 Extraindo áudio com FFmpeg...")
# subprocess.run(ffmpeg_cmd, check=True)
# logger.registrar_info(f"✅ Áudio extraído: {wav_file}")