import asyncio
from pathlib import Path
from core.config import Config
from core.logger import Logger
from core.file_processor import MXFProcessor
from workflows.unmixed_audio import UnmixedAudioWorkflow
from workflows.mixed_audio import MixedAudioWorkflow
from processors.edl_generator import EDLGenerator

class WatchFolderScheduler:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.workflows = [
            UnmixedAudioWorkflow(),
            MixedAudioWorkflow()
        ]
        self.edl_generator = EDLGenerator()
    
    async def process_pending_files(self):
        """Processa todos os MXFs na pasta de entrada UMA VEZ"""
        try:
            mxf_files = list(self.config.WATCHFOLDER_INPUT.glob("*.mxf"))
            
            if not mxf_files:
                self.logger.info("📭 Nenhum arquivo MXF encontrado para processamento")
                return
            
            self.logger.info(f"📥 Encontrados {len(mxf_files)} arquivos MXF para processar")
            
            processed_count = 0
            for mxf_path in mxf_files:
                try:
                    success = await self.process_single_file(mxf_path)
                    if success:
                        processed_count += 1
                    else:
                        self.logger.error(f"❌ Falha no processamento: {mxf_path.name}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Erro processando {mxf_path.name}: {e}")
                    # Move para pasta de erro
                    error_path = self.config.WATCHFOLDER_INPUT / "error" / mxf_path.name
                    error_path.parent.mkdir(exist_ok=True)
                    mxf_path.rename(error_path)
            
            self.logger.info(f"✅ Processamento concluído: {processed_count}/{len(mxf_files)} arquivos processados com sucesso")
            return processed_count
            
        except Exception as e:
            self.logger.error(f"💥 Erro no processamento em lote: {e}")
            return 0
    
    async def process_single_file(self, mxf_path: Path):
        """Processa um único arquivo MXF"""
        try:
            self.logger.info(f"🔄 Processando arquivo: {mxf_path.name}")
            
            processor = MXFProcessor()
            streams = processor.get_streams(mxf_path)
            
            if not streams:
                self.logger.warning(f"⚠️ Nenhum stream encontrado em {mxf_path.name}")
                return False
            
            # Encontra workflow apropriado
            workflow = None
            for wf in self.workflows:
                if wf.can_handle(streams):
                    workflow = wf
                    break
            
            if not workflow:
                self.logger.warning(f"⚠️ Nenhum workflow adequado para {mxf_path.name}")
                return False
            
            self.logger.info(f"🔧 Usando workflow: {workflow.get_workflow_name()}")
            
            # Processa o arquivo
            results = await workflow.process(mxf_path)
            
            # Gera EDL
            edl_content = self.edl_generator.generate_edl(results, mxf_path.name)
            
            # Salva EDL
            edl_filename = f"{mxf_path.stem}.edl"
            edl_path = self.config.WATCHFOLDER_OUTPUT / edl_filename
            self.edl_generator.save_edl(edl_content, edl_path)
            
            # Move MXF processado
            processed_path = self.config.WATCHFOLDER_PROCESSED / mxf_path.name
            mxf_path.rename(processed_path)
            self.logger.info(f"✅ Arquivo processado e movido: {processed_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro processando {mxf_path.name}: {e}")
            return False