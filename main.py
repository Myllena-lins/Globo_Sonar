#!/usr/bin/env python3
"""
GLOBO_SONAR - Sistema de conversão MXF para EDL
Execução sob demanda via script batch + API FastAPI
"""

import asyncio
import sys
from pathlib import Path

from fastapi import FastAPI
from app.controllers.mxf_controller import router as mxf_router

sys.path.append(str(Path(__file__).parent))

from core.config import Config
from core.logger import Logger
from core.database import Base, engine
from features.watchfolder.scheduler import WatchFolderScheduler
from features.watchfolder.sharepoint_scheduler import SharePointScheduler

# ------------------------------
# Criação automática das tabelas
# ------------------------------
Base.metadata.create_all(bind=engine)

# ------------------------------
# Inicializa FastAPI
# ------------------------------
app = FastAPI(
    title="Globo Sonar API",
    description="API para Análise de Áudio em Arquivos MXF",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
app.include_router(mxf_router)

async def main_async():
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
