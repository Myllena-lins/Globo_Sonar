from io import BytesIO
import requests
import msal
from pathlib import Path
from core.config import Config
from core.logger import Logger
import os

class SharePointClient:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.access_token = None
        
        # Configurações do SharePoint do .env
        self.client_id = os.getenv('SHAREPOINT_CLIENT_ID')
        self.client_secret = os.getenv('SHAREPOINT_CLIENT_SECRET')
        self.tenant_id = os.getenv('SHAREPOINT_TENANT_ID')
        self.site_name = os.getenv('SHAREPOINT_SITE_NAME')
        self.input_folder = os.getenv('SHAREPOINT_INPUT_FOLDER', 'input')
        self.output_folder = os.getenv('SHAREPOINT_OUTPUT_FOLDER', 'output')
        self.processed_folder = os.getenv('SHAREPOINT_PROCESSED_FOLDER', 'processed')

    def authenticate(self):
        """Autentica e obtém token de acesso"""
        try:
            self.logger.info("🔐 Autenticando com SharePoint...")

            authority = f"https://login.microsoftonline.com/{self.tenant_id}"
            scope = ["https://graph.microsoft.com/.default"]

            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=authority,
                client_credential=self.client_secret
            )

            token_result = app.acquire_token_for_client(scopes=scope)

            if "access_token" not in token_result:
                raise Exception(token_result.get("error_description", "Token não retornado."))

            self.access_token = {"Authorization": f"Bearer {token_result['access_token']}"}
            self.logger.info("✅ Autenticação com SharePoint realizada com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro na autenticação SharePoint: {e}")
            return False

    def get_site_id(self):
        """Obtém o ID do site do SharePoint"""
        try:
            self.logger.info("📋 Obtendo site ID do SharePoint")
            url = f"https://graph.microsoft.com/v1.0/sites/root:/sites/{self.site_name}"
            resp = requests.get(url, headers=self.access_token)
            resp.raise_for_status()
            site_id = resp.json().get("id")
            self.logger.info(f"✅ Site ID obtido: {site_id}")
            return site_id
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter site_id: {e}")
            return None

    def get_drive_id(self, site_id):
        """Obtém o ID do drive (biblioteca de documentos)"""
        try:
            self.logger.info("📂 Obtendo drive ID")
            url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
            resp = requests.get(url, headers=self.access_token)
            resp.raise_for_status()
            
            # Procura pelo drive de documentos
            for drive in resp.json()["value"]:
                if "Documentos" in drive["name"] or "Documents" in drive["name"]:
                    drive_id = drive["id"]
                    self.logger.info(f"✅ Drive ID obtido: {drive_id}")
                    return drive_id
            
            raise Exception("Drive 'Documentos' não encontrado.")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter drive_id: {e}")
            return None

    def list_files_in_folder(self, folder_path=None):
        """Lista arquivos MXF na pasta do SharePoint"""
        try:
            if not self.access_token:
                if not self.authenticate():
                    return []
            
            site_id = self.get_site_id()
            if not site_id:
                return []
                
            drive_id = self.get_drive_id(site_id)
            if not drive_id:
                return []
            
            folder = folder_path or self.input_folder
            url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{folder}:/children"
            
            resp = requests.get(url, headers=self.access_token)
            resp.raise_for_status()
            
            files = []
            for item in resp.json()["value"]:
                if item["name"].lower().endswith('.mxf'):
                    files.append({
                        'name': item["name"],
                        'id': item["id"],
                        'size': item.get("size", 0),
                        'modified': item.get("lastModifiedDateTime")
                    })
            
            self.logger.info(f"📁 Encontrados {len(files)} arquivos MXF no SharePoint")
            return files
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao listar arquivos do SharePoint: {e}")
            return []

    def download_file(self, file_name, folder_path=None):
        """Faz download de um arquivo do SharePoint"""
        try:
            self.logger.info(f"⬇️ Baixando arquivo: {file_name}")
            
            if not self.access_token:
                if not self.authenticate():
                    return None
            
            site_id = self.get_site_id()
            if not site_id:
                return None
                
            drive_id = self.get_drive_id(site_id)
            if not drive_id:
                return None
            
            folder = folder_path or self.input_folder
            url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{folder}/{file_name}:/content"
            
            resp = requests.get(url, headers=self.access_token)
            resp.raise_for_status()
            
            # Salva o arquivo localmente
            local_path = self.config.WATCHFOLDER_INPUT / file_name
            with open(local_path, 'wb') as f:
                f.write(resp.content)
            
            self.logger.info(f"✅ Arquivo baixado: {local_path}")
            return local_path
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao baixar arquivo {file_name}: {e}")
            return None

    def upload_file(self, local_path, folder_path=None):
        """Faz upload de um arquivo para o SharePoint"""
        try:
            self.logger.info(f"⬆️ Enviando arquivo: {local_path.name}")
            
            if not self.access_token:
                if not self.authenticate():
                    return False
            
            site_id = self.get_site_id()
            if not site_id:
                return False
                
            drive_id = self.get_drive_id(site_id)
            if not drive_id:
                return False
            
            folder = folder_path or self.output_folder
            url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{folder}/{local_path.name}:/content"
            
            with open(local_path, 'rb') as f:
                file_content = f.read()
            
            resp = requests.put(url, headers=self.access_token, data=file_content)
            resp.raise_for_status()
            
            self.logger.info(f"✅ Arquivo enviado para SharePoint: {local_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar arquivo {local_path.name}: {e}")
            return False

    def move_file_to_processed(self, file_name):
        """Move arquivo para pasta de processados no SharePoint"""
        try:
            self.logger.info(f"🔄 Movendo arquivo para processados: {file_name}")
            
            if not self.access_token:
                if not self.authenticate():
                    return False
            
            site_id = self.get_site_id()
            if not site_id:
                return False
                
            drive_id = self.get_drive_id(site_id)
            if not drive_id:
                return False
            
            # URL para mover o arquivo
            url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{file_name}"
            
            move_payload = {
                "parentReference": {
                    "path": f"/drives/{drive_id}/root:/{self.processed_folder}"
                },
                "name": file_name
            }
            
            resp = requests.patch(url, headers=self.access_token, json=move_payload)
            
            if resp.status_code == 200:
                self.logger.info(f"✅ Arquivo movido para processados: {file_name}")
                return True
            else:
                self.logger.warning(f"⚠️ Não foi possível mover o arquivo, tentando deletar...")
                # Se não conseguir mover, tenta deletar
                return self.delete_file(file_name, self.input_folder)
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao mover arquivo {file_name}: {e}")
            return False

    def delete_file(self, file_name, folder_path=None):
        """Deleta arquivo do SharePoint"""
        try:
            self.logger.info(f"🗑️ Deletando arquivo: {file_name}")
            
            if not self.access_token:
                if not self.authenticate():
                    return False
            
            site_id = self.get_site_id()
            if not site_id:
                return False
                
            drive_id = self.get_drive_id(site_id)
            if not drive_id:
                return False
            
            folder = folder_path or self.input_folder
            url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{folder}/{file_name}"
            
            resp = requests.delete(url, headers=self.access_token)
            
            if resp.status_code in [200, 204]:
                self.logger.info(f"✅ Arquivo deletado: {file_name}")
                return True
            else:
                self.logger.warning(f"⚠️ Não foi possível deletar arquivo: {file_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao deletar arquivo {file_name}: {e}")
            return False