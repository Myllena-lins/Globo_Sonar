import os
from pathlib import Path

def safe_delete(file_path: Path):
    """Deleta arquivo de forma segura"""
    try:
        if file_path.exists():
            file_path.unlink()
            return True
    except Exception:
        return False
    return False

def get_file_size_mb(file_path: Path):
    """Retorna tamanho do arquivo em MB"""
    if file_path.exists():
        return file_path.stat().st_size / (1024 * 1024)
    return 0

def cleanup_old_files(directory: Path, max_age_days: int = 7):
    """Limpa arquivos antigos do diretório"""
    import time
    from datetime import datetime, timedelta
    
    cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
    
    for file_path in directory.glob("*"):
        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
            safe_delete(file_path)