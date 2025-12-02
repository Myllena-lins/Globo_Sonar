import asyncio
from pathlib import Path
from core.config import Config
from core.logger import Logger
from core.file_processor import MXFProcessor
from features.workflows.unmixed_audio import UnmixedAudioWorkflow
from features.workflows.mixed_audio import MixedAudioWorkflow
from features.processors.edl_generator import EDLGenerator
from features.sharepoint.client import SharePointClient

class SharePointScheduler:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.workflows = [
            UnmixedAudioWorkflow(),
            MixedAudioWorkflow()
        ]
        self.edl_generator = EDLGenerator()
        self.sharepoint = SharePointClient()
    
    async def process_pending_files(self):
        """Processa todos os MXFs do SharePoint UMA VEZ"""
        try:
            if not self.config.USE_SHAREPOINT:
                self.logger.info("📂 Modo SharePoint desativado")
                return 0
            
            # Lista arquivos no SharePoint
            sharepoint_files = self.sharepoint.list_files_in_folder()
            
            if not sharepoint_files:
                self.logger.info("📭 Nenhum arquivo MXF encontrado no SharePoint")
                return 0
            
            self.logger.info(f"📥 Encontrados {len(sharepoint_files)} arquivos no SharePoint")
            
            processed_count = 0
            for file_info in sharepoint_files:
                file_name = file_info['name']
                try:
                    success = await self.process_single_sharepoint_file(file_name)
                    if success:
                        processed_count += 1
                        self.logger.info(f"✅ Processamento concluído: {file_name}")
                    else:
                        self.logger.error(f"❌ Falha no processamento: {file_name}")
                        
                except Exception as e:
                    self.logger.error(f"❌ Erro processando {file_name}: {e}")
            
            self.logger.info(f"🎉 Processamento concluído: {processed_count}/{len(sharepoint_files)} arquivos processados")
            return processed_count
            
        except Exception as e:
            self.logger.error(f"💥 Erro no processamento em lote do SharePoint: {e}")
            return 0
    
    async def process_single_sharepoint_file(self, file_name):
        """Processa um único arquivo do SharePoint"""
        try:
            self.logger.info(f"🔄 Iniciando processamento do SharePoint: {file_name}")
            
            # 1. Download do arquivo
            local_mxf_path = self.sharepoint.download_file(file_name)
            if not local_mxf_path or not local_mxf_path.exists():
                self.logger.error(f"❌ Falha no download: {file_name}")
                return False
            
            # 2. Processa o arquivo localmente
            processor = MXFProcessor()
            streams = processor.get_streams(local_mxf_path)
            
            if not streams:
                self.logger.warning(f"⚠️ Nenhum stream encontrado em {file_name}")
                local_mxf_path.unlink(missing_ok=True)
                return False
            
            # Encontra workflow apropriado
            workflow = None
            for wf in self.workflows:
                if wf.can_handle(streams):
                    workflow = wf
                    break
            
            if not workflow:
                self.logger.warning(f"⚠️ Nenhum workflow adequado para {file_name}")
                local_mxf_path.unlink(missing_ok=True)
                return False
            
            self.logger.info(f"🔧 Usando workflow: {workflow.get_workflow_name()}")
            
            # 3. Processa o arquivo
            results = await workflow.process(local_mxf_path)
            
            # 4. Gera EDL
            edl_content = self.edl_generator.generate_edl(results, file_name)
            
            # 5. Salva EDL localmente
            edl_filename = f"{local_mxf_path.stem}.edl"
            local_edl_path = self.config.WATCHFOLDER_OUTPUT / edl_filename
            self.edl_generator.save_edl(edl_content, local_edl_path)
            
            # 6. Upload do EDL para SharePoint
            upload_success = self.sharepoint.upload_file(local_edl_path)
            
            # 7. Move arquivo para processados no SharePoint
            move_success = self.sharepoint.move_file_to_processed(file_name)
            
            # 8. Limpeza local
            local_mxf_path.unlink(missing_ok=True)
            local_edl_path.unlink(missing_ok=True)
            
            if upload_success and move_success:
                self.logger.info(f"✅ Processamento completo: {file_name}")
                return True
            else:
                self.logger.warning(f"⚠️ Processamento parcial: {file_name}")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Erro processando {file_name}: {e}")
            
            # Limpeza em caso de erro
            local_mxf_path = self.config.WATCHFOLDER_INPUT / file_name
            local_mxf_path.unlink(missing_ok=True)
            
            return False