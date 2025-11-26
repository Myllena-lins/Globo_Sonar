#!/usr/bin/env python3
"""
GLOBO_SONAR - Sistema de conversão MXF para EDL
Execução sob demanda via script batch
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.config import Config
from core.logger import Logger
from watchfolder.scheduler import WatchFolderScheduler
from watchfolder.sharepoint_scheduler import SharePointScheduler
from fastapi import FastAPI
from controllers.mxf_controller import router as mxf_router


app = FastAPI()
app.include_router(mxf_router)

async def main_async():
    """Função principal assíncrona"""
    logger = Logger()
    config = Config()
    
    try:
        logger.info("=" * 60)
        logger.info("🎵 GLOBO_SONAR - Iniciando Processamento")
        
        if config.USE_SHAREPOINT:
            logger.info("🌐 Modo: SharePoint Online")
            scheduler = SharePointScheduler()
        else:
            logger.info("📂 Modo: Watchfolder Local")
            scheduler = WatchFolderScheduler()
            
        logger.info("=" * 60)
        
        # Executa o processamento uma vez
        await scheduler.process_pending_files()
        
        logger.info("✅ Processamento concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"💥 Erro no processamento: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()