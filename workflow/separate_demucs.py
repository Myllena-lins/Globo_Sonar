import subprocess
from pathlib import Path
from utils.Logger import Logger

logger = Logger()

def separar_com_demucs(audio_path):
    """
    Roda o Demucs para separar vocais, bateria, baixo, etc.
    """
    try:
        output_dir = Path("files/export/demucs")
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
