import subprocess
import json
from spleeter.separator import Separator
#from utils.Logger import Logger
import os
import uuid
from datetime import datetime
from pathlib import Path  # Importação necessária para trabalhar com paths
import shutil  # Importação para operações de arquivo/diretório

#logger = Logger()

def extrador_de_melodias():
    # Entrada: arquivo de áudio original
    # Saída: arquivos de medlodia na pasta files/songs/wav
    
    # === 1️⃣ Definição de paths ===
    audio_file = Path("Pixote - Insegurança (15 Anos)(Ao Vivo)(Vídeo Oficial).mp4")  # Arquivo de entrada - ajuste conforme necessário
    output_melody_path = Path("files/songs/wav")  # Pasta final para melodias
    temp_dir = Path(f"temp_{uuid.uuid4()}")  # Pasta temporária para processamento
    
    # Cria os diretórios necessários
    output_melody_path.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # === 2️⃣ Separação com Spleeter ===
    print("🎶 Separando faixas com Spleeter (voz e acompanhamento)...")
    
    try:
        # Inicializa o separador do Spleeter
        separator = Separator('spleeter:2stems')
        
        # Executa a separação - isso cria pasta com mesmo nome do arquivo dentro do temp_dir
        separator.separate_to_file(str(audio_file), str(temp_dir))
        
        # === 3️⃣ Localiza e processa os arquivos separados ===
        # O Spleeter cria uma pasta com o nome do arquivo dentro do diretório de output
        audio_filename = audio_file.stem  # Nome do arquivo sem extensão
        spleeter_output_dir = temp_dir / audio_filename
        
        # Verifica se a separação foi bem sucedida
        if spleeter_output_dir.exists():
            # Arquivos gerados pelo Spleeter (2stems)
            accompaniment_file = spleeter_output_dir / "accompaniment.wav"  # Arquivo da melodia/música
            vocals_file = spleeter_output_dir / "vocals.wav"  # Arquivo da voz
            
            # === 4️⃣ Processa apenas a melodia (acompanhamento) ===
            if accompaniment_file.exists():
                # Lista arquivos de melodia existentes para determinar o próximo índice
                existing_songs = list(output_melody_path.glob("song_*.wav"))
                next_index = len(existing_songs)  # Próximo índice disponível
                
                # Nome do novo arquivo de melodia
                new_melody_name = f"song_{next_index}.wav"
                melody_output_path = output_melody_path / new_melody_name
                
                # Move o arquivo de acompanhamento (melodia) para a pasta final
                shutil.move(str(accompaniment_file), str(melody_output_path))
                print(f"✅ Melodia salva como: {new_melody_name}")
                
            else:
                print("❌ Arquivo de acompanhamento não encontrado")
                return None
                
        else:
            print("❌ Pasta de output do Spleeter não encontrada")
            return None
            
    except Exception as e:
        print(f"❌ Erro durante a separação: {e}")
        return None
        
    finally:
        # === 5️⃣ Limpeza: remove pasta temporária e arquivos de voz ===
        if temp_dir.exists():
            shutil.rmtree(temp_dir)  # Deleta toda a pasta temporária recursivamente
            print("🗑️ Pasta temporária removida")
    
    print("🏁 Processo finalizado com sucesso!")
    return output_melody_path  # Retorna o path para as melodias

# Exemplo de uso
if __name__ == "__main__":
    resultado = extrador_de_melodias()
    if resultado:
        print(f"🎵 Músicas disponíveis em: {resultado}")
