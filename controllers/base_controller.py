# controllers/base_controller.py
from fastapi import APIRouter, HTTPException
from abc import ABC, abstractmethod
from pathlib import Path
import uuid
from datetime import datetime

class BaseController(ABC):
    def __init__(self):
        self.router = APIRouter()
        self._register_routes()
    
    @abstractmethod
    def _register_routes(self):
        """Método abstrato para registrar rotas - deve ser implementado pelas classes filhas"""
        pass
    
    # Métodos utilitários que podem ser usados por todos os controllers
    def generate_request_id(self) -> str:
        """Gera um ID único para a requisição"""
        return str(uuid.uuid4())[:8]
    
    def get_timestamp(self) -> str:
        """Retorna timestamp atual em ISO format"""
        return datetime.now().isoformat()
    
    def validate_file_extension(self, filename: str, allowed_extensions: list) -> bool:
        """Valida a extensão do arquivo"""
        return any(filename.lower().endswith(ext) for ext in allowed_extensions)
    
    def save_uploaded_file(self, file_content: bytes, upload_dir: Path, filename: str) -> Path:
        """Salva arquivo enviado e retorna o caminho"""
        upload_dir.mkdir(parents=True, exist_ok=True)
        saved_path = upload_dir / filename
        
        with open(saved_path, 'wb') as f:
            f.write(file_content)
        
        return saved_path