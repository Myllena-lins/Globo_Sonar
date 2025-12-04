import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    # Paths
    FFMPEG_PATH = os.getenv('FFMPEG_PATH', 'ffmpeg')
    FFPROBE_PATH = os.getenv('FFPROBE_PATH', 'ffprobe')
    PASTA_SAIDA = Path(os.getenv('PASTA_SAIDA', 'files/export'))
    LOGS_PATH = Path(os.getenv('CAMINHO_DIRETORIO_LOGS', 'logs'))
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mxf.db")
    
    # Watchfolder
    WATCHFOLDER_INPUT = Path(os.getenv('WATCHFOLDER_INPUT', 'files/input'))
    WATCHFOLDER_OUTPUT = Path(os.getenv('WATCHFOLDER_OUTPUT', 'files/output'))
    WATCHFOLDER_PROCESSED = Path(os.getenv('WATCHFOLDER_PROCESSED', 'files/processed'))
    WATCHFOLDER_SCHEDULE = os.getenv('WATCHFOLDER_SCHEDULE', '09:00')
    
    # Audio Processing
    SILENCE_THRESHOLD = int(os.getenv('SILENCE_THRESHOLD', '-60'))
    MIN_SILENCE_LEN = int(os.getenv('MIN_SILENCE_LEN', '1000'))
    MIN_SEGMENT_DURATION = int(os.getenv('MIN_SEGMENT_DURATION', '5000'))
    
    # SharePoint
    SHAREPOINT_CLIENT_ID = os.getenv('SHAREPOINT_CLIENT_ID')
    SHAREPOINT_CLIENT_SECRET = os.getenv('SHAREPOINT_CLIENT_SECRET')
    SHAREPOINT_TENANT_ID = os.getenv('SHAREPOINT_TENANT_ID')
    SHAREPOINT_SITE_NAME = os.getenv('SHAREPOINT_SITE_NAME')
    SHAREPOINT_INPUT_FOLDER = os.getenv('SHAREPOINT_INPUT_FOLDER', 'input')
    SHAREPOINT_OUTPUT_FOLDER = os.getenv('SHAREPOINT_OUTPUT_FOLDER', 'output')
    SHAREPOINT_PROCESSED_FOLDER = os.getenv('SHAREPOINT_PROCESSED_FOLDER', 'processed')
    
    # Modo de operação
    USE_SHAREPOINT = os.getenv('USE_SHAREPOINT', 'false').lower() == 'true'
    
    def __init__(self):
        # Create directories
        self.PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
        self.LOGS_PATH.mkdir(parents=True, exist_ok=True)
        self.WATCHFOLDER_INPUT.mkdir(parents=True, exist_ok=True)
        self.WATCHFOLDER_OUTPUT.mkdir(parents=True, exist_ok=True)
        self.WATCHFOLDER_PROCESSED.mkdir(parents=True, exist_ok=True)