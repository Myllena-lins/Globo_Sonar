import logging
from datetime import datetime
from pathlib import Path
import os
from core.config import Config

class Logger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.config = Config()
        self.log_format = '%(asctime)s - %(levelname)s - %(message)s'
        self.date_format = '%d-%m-%Y'
        self._initialized = True
    
    def _get_logger(self, log_name):
        """Cria e configura um logger específico"""
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.DEBUG)
        
        # Remove handlers existentes para evitar duplicação
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Configura o arquivo de log diário
        today = datetime.now().strftime(self.date_format)
        log_file = self.config.LOGS_PATH / f"{today}.log"
        
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(self.log_format))
        
        # Adiciona também console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(self.log_format))
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger
    
    def info(self, message):
        """Registra uma mensagem de nível INFO"""
        logger = self._get_logger("info_logger")
        logger.info(message)
    
    def error(self, message):
        """Registra uma mensagem de nível ERROR"""
        logger = self._get_logger("error_logger")
        logger.error(message)
    
    def warning(self, message):
        """Registra uma mensagem de nível WARNING"""
        logger = self._get_logger("warning_logger") 
        logger.warning(message)
    
    def debug(self, message):
        """Registra uma mensagem de nível DEBUG"""
        logger = self._get_logger("debug_logger")
        logger.debug(message)