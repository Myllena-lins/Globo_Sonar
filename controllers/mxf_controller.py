# controllers/mxf_controller.py
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pathlib import Path
import asyncio
from datetime import datetime
from typing import List, Optional

from .base_controller import BaseController
from models.schemas import AnalysisResponse, MusicInfo
from services.audio_analyzer import AudioAnalyzer

class MXFController(BaseController):
    def __init__(self):
        # Configurações específicas do MXF
        self.MXF_UPLOAD_DIR = Path("/home/enio/dev/Globo_Sonar/files/mxf")
        self.allowed_extensions = ['.mxf']
        
        # Serviço de análise (pode ser mock ou real)
        self.analyzer = AudioAnalyzer()
        
        super().__init__()
    
    def _register_routes(self):
        """Registra as rotas específicas do MXF"""
        self.router.add_api_route(
            "/analyze",
            self.analyze_audio,
            methods=["POST"],
            response_model=AnalysisResponse,
            summary="Analisar arquivo MXF",
            description="Faz upload e análise de arquivo MXF para detecção de músicas"
        )
    
    async def analyze_audio(self, file: UploadFile = File(...)) -> AnalysisResponse:
        """Analisa arquivo MXF e retorna músicas detectadas"""
        start_time = datetime.now()
        
        try:
            # Validação do arquivo
            if not self.validate_file_extension(file.filename, self.allowed_extensions):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Arquivo deve ser MXF"
                )
            
            request_id = self.generate_request_id()
            print(f"📥 Iniciando upload: {file.filename} (ID: {request_id})")
            
            # Lê o conteúdo do arquivo
            file_content = await file.read()
            total_size = len(file_content)
            
            if total_size == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Arquivo vazio"
                )
            
            print(f"✅ Upload completo: {total_size//1024//1024}MB")
            
            # Salva o arquivo MXF
            original_name = Path(file.filename).stem
            extension = Path(file.filename).suffix
            saved_filename = f"{original_name}_{request_id}{extension}"
            saved_path = self.save_uploaded_file(
                file_content, 
                self.MXF_UPLOAD_DIR, 
                saved_filename
            )
            
            print(f"💾 MXF salvo em: {saved_path}")
            
            # Processa a análise
            analysis_start = datetime.now()
            result = await self.analyzer.analyze_mxf(
                file_content, 
                request_id, 
                file.filename, 
                str(saved_path)
            )
            analysis_time = (datetime.now() - analysis_start).total_seconds()
            
            total_time = (datetime.now() - start_time).total_seconds()
            print(f"⏱️  Tempos - Upload: {total_time - analysis_time:.2f}s, Análise: {analysis_time:.2f}s, Total: {total_time:.2f}s")
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Erro no processamento: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro interno: {str(e)}"
            )