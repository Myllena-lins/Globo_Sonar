from abc import ABC, abstractmethod
from pathlib import Path
from core.logger import Logger

class BaseWorkflow(ABC):
    def __init__(self):
        self.logger = Logger()
    
    @abstractmethod
    async def process(self, mxf_path: Path):
        """Processa arquivo MXF e retorna resultados"""
        pass
    
    @abstractmethod
    def can_handle(self, streams) -> bool:
        """Verifica se pode processar os streams"""
        pass
    
    def get_workflow_name(self):
        """Retorna nome do workflow"""
        return self.__class__.__name__