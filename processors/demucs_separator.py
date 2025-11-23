import subprocess
import sys
from pathlib import Path
from core.logger import Logger
from core.config import Config

class DemucsSeparator:
    def __init__(self):
        self.logger = Logger()
        self.config = Config()
        self.demucs_available = self._check_demucs_availability()
    
    def _check_demucs_availability(self):
        """Verifica se o Demucs está disponível no sistema"""
        try:
            # Tenta diferentes comandos para verificar o Demucs
            commands_to_try = [
                ["demucs", "--help"],
                [sys.executable, "-m", "demucs", "--help"],  # Tenta como módulo Python
                ["python", "-m", "demucs", "--help"],
                ["python3", "-m", "demucs", "--help"]
            ]
            
            for cmd in commands_to_try:
                try:
                    self.logger.info(f"🔍 Testando comando: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        self.logger.info(f"✅ Demucs encontrado via: {' '.join(cmd)}")
                        return True
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            self.logger.warning("❌ Demucs não encontrado em nenhum dos comandos testados")
            return False
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao verificar Demucs: {e}")
            return False

    def separate_audio(self, audio_path: Path):
        """
        Separa áudio em componentes usando Demucs
        Retorna dicionário com paths dos arquivos separados
        """
        if not self.demucs_available:
            self.logger.warning("🚫 Demucs não disponível - pulando separação")
            return {}
            
        try:
            output_dir = self.config.PASTA_SAIDA / "demucs_separated"
            output_dir.mkdir(exist_ok=True)
            
            self.logger.info(f"🎵 Separando áudio com Demucs: {audio_path.name}")
            
            # Tenta diferentes formas de executar o Demucs
            cmd_versions = [
                ["demucs", "-n", "htdemucs", "-o", str(output_dir), str(audio_path)],
                [sys.executable, "-m", "demucs", "-n", "htdemucs", "-o", str(output_dir), str(audio_path)],
                ["python", "-m", "demucs", "-n", "htdemucs", "-o", str(output_dir), str(audio_path)],
                ["python3", "-m", "demucs", "-n", "htdemucs", "-o", str(output_dir), str(audio_path)]
            ]
            
            for cmd in cmd_versions:
                try:
                    self.logger.info(f"🔧 Executando: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)  # 1 hora timeout
                    
                    if result.returncode == 0:
                        self.logger.info("✅ Separação Demucs concluída com sucesso")
                        break
                    else:
                        self.logger.error(f"❌ Erro no Demucs: {result.stderr}")
                        continue
                        
                except subprocess.TimeoutExpired:
                    self.logger.error("⏰ Timeout - Demucs está demorando muito")
                    return {}
                except FileNotFoundError:
                    continue
            else:
                self.logger.error("❌ Não foi possível executar o Demucs em nenhum formato")
                return {}
            
            # Encontra os arquivos resultantes
            separated_files = {}
            model_dir = output_dir / "htdemucs" / audio_path.stem
            
            if model_dir.exists():
                for track_file in model_dir.glob("*.wav"):
                    track_name = track_file.stem
                    separated_files[track_name] = track_file
                    self.logger.info(f"🎵 Track {track_name}: {track_file}")
                
                self.logger.info(f"✅ Encontrados {len(separated_files)} tracks separados")
            else:
                self.logger.warning(f"⚠️ Pasta de resultados não encontrada: {model_dir}")
            
            return separated_files
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar Demucs: {e}")
            return {}