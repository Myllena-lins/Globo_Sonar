from dotenv import load_dotenv
load_dotenv()
from utils.Logger import Logger
from workflow.get_streams import get_streams
from workflow.extract_streams import extrair_audio, processar_audio_com_shazam
import pymsgbox
import os
import asyncio

async def main_async():
    logger = Logger()

    # Carrega variáveis de ambiente
    arquivo_mxf = os.getenv("ARQUIVO_MXF")
    pasta_saida = os.getenv("PASTA_SAIDA")

    try:
        # Verifica se o arquivo MXF existe
        if not os.path.exists(arquivo_mxf):
            logger.registrar_erro(f"❌ Arquivo MXF não encontrado: {arquivo_mxf}")
            pymsgbox.alert("Arquivo MXF não encontrado!")
            return

        # Cria a pasta de saída se não existir
        os.makedirs(pasta_saida, exist_ok=True)

        # Obter streams do arquivo MXF
        streams = get_streams(arquivo_mxf)

        if not streams:
            logger.registrar_erro("❌ Nenhum stream encontrado no arquivo MXF.")
            return

        logger.registrar_info(f"📊 Encontradas {len(streams)} streams no MXF.")

        # Processar streams de áudio
        extracted_files = extrair_audio(streams)

        if extracted_files:
            # Análise com Shazam
            shazam_results = await processar_audio_com_shazam(streams)
            
            # Aqui você pode usar os resultados para gerar EDL, relatórios, etc.
            if shazam_results:
                logger.registrar_info("🎵 Processamento musical concluído com sucesso!")
            else:
                logger.registrar_aviso("⚠️ Processamento concluído, mas nenhuma música reconhecida")

    except Exception as e:
        logger.registrar_erro(f"❌ Erro inesperado: {e}")
        pymsgbox.alert("Erro ao tentar executar o processo.")
        return

    # Finalização
    logger.registrar_info("\n✅ Processamento concluído!")
    pymsgbox.alert("Processo finalizado com sucesso!")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()