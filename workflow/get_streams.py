import subprocess
import os
import json
from dotenv import load_dotenv
from utils.Logger import Logger

logger = Logger()
load_dotenv()
ffprobe_path = os.getenv('FFPROBE_PATH')

def get_streams(file_path):
    cmd = [
        ffprobe_path,
        '-v', 'error',
        '-show_entries', 'stream=index,codec_type,codec_name,channels',
        '-of', 'json',
        file_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        logger.registrar_erro(f"Erro no ffprobe: {result.stderr}")

    data = json.loads(result.stdout)
    return data.get('streams', [])
