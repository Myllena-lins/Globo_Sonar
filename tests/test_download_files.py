import asyncio
import aiohttp
import os
from pathlib import Path

class FileDownloadTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        # Cria a estrutura de diretórios se não existir
        Path("files/songs/wav").mkdir(parents=True, exist_ok=True)
        Path("files/edl").mkdir(parents=True, exist_ok=True)
    
    async def create_test_files(self):
        """Cria os arquivos de teste no servidor"""
        print("📁 Criando arquivos de teste no servidor...")
        
        # Cria arquivo WAV mock
        wav_content = b"RIFF\x24\x08\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00\x22\x56\x00\x00\x88\x58\x01\x00\x04\x00\x10\x00data\x00\x08\x00\x00" + b"\x00" * 1000
        wav_path = "files/songs/wav/song_0.wav"
        with open(wav_path, 'wb') as f:
            f.write(wav_content)
        print(f"✅ Arquivo WAV criado: {wav_path} ({len(wav_content)} bytes)")
        
        # Cria arquivo EDL mock
        edl_content = """TITLE: Test EDL File - Music Detection Results
FCM: NON-DROP FRAME

001  AX       A     C        00:00:00:00 00:00:30:00 00:00:00:00 00:00:30:00
* FROM CLIP NAME: song_0.wav
* MUSIC: Bohemian Rhapsody - Queen
* FROM CLIP BITC: 00:00:00:00
* TO CLIP BITC: 00:00:30:00

002  AX       A     C        00:01:15:00 00:01:45:00 00:00:30:00 00:01:00:00
* FROM CLIP NAME: song_1.wav  
* MUSIC: Sweet Child O'Mine - Guns N' Roses
* FROM CLIP BITC: 00:00:00:00
* TO CLIP BITC: 00:00:30:00

003  AX       A     C        00:02:30:00 00:03:30:00 00:01:00:00 00:02:00:00
* FROM CLIP NAME: song_2.wav
* MUSIC: Imagine - John Lennon
* FROM CLIP BITC: 00:00:00:00
* TO CLIP BITC: 00:01:00:00
"""
        edl_path = "files/edl/test_edl.edl"
        with open(edl_path, 'w', encoding='utf-8') as f:
            f.write(edl_content)
        print(f"✅ Arquivo EDL criado: {edl_path} ({len(edl_content)} bytes)")
        
        return wav_path, edl_path
    
    async def test_download_edl(self, request_id="test_edl"):
        """Testa download de arquivo EDL específico"""
        print(f"\n🧪 Testando Download EDL: {request_id}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/download/edl/{request_id}") as response:
                    
                    if response.status == 200:
                        content = await response.read()
                        content_type = response.headers.get('Content-Type', '')
                        content_disposition = response.headers.get('Content-Disposition', '')
                        
                        print(f"✅ Download EDL bem-sucedido!")
                        print(f"   Status: {response.status}")
                        print(f"   Content-Type: {content_type}")
                        print(f"   Content-Disposition: {content_disposition}")
                        print(f"   Tamanho: {len(content)} bytes")
                        print(f"   Primeiros 100 caracteres: {content[:100].decode('utf-8', errors='ignore')}")
                        
                        # Salva o arquivo baixado
                        downloaded_path = f"downloaded_{request_id}.edl"
                        with open(downloaded_path, 'wb') as f:
                            f.write(content)
                        print(f"   💾 Arquivo salvo como: {downloaded_path}")
                        
                        return {
                            'status': 'success',
                            'file_size': len(content),
                            'content_type': content_type,
                            'filename': downloaded_path,
                            'content_preview': content[:100].decode('utf-8', errors='ignore')
                        }
                    else:
                        error_text = await response.text()
                        print(f"❌ Download EDL falhou: Status {response.status}")
                        print(f"   Erro: {error_text}")
                        return {
                            'status': 'failed',
                            'error': f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            print(f"❌ Download EDL falhou: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def test_download_wav(self, filename="song_0.wav"):
        """Testa download de arquivo WAV específico"""
        print(f"\n🧪 Testando Download WAV: {filename}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/download/wav/{filename}") as response:
                    
                    if response.status == 200:
                        content = await response.read()
                        content_type = response.headers.get('Content-Type', '')
                        content_disposition = response.headers.get('Content-Disposition', '')
                        
                        print(f"✅ Download WAV bem-sucedido!")
                        print(f"   Status: {response.status}")
                        print(f"   Content-Type: {content_type}")
                        print(f"   Content-Disposition: {content_disposition}")
                        print(f"   Tamanho: {len(content)} bytes")
                        print(f"   Primeiros 50 bytes (hex): {content[:50].hex()}")
                        
                        # Verifica se é um arquivo WAV válido
                        is_wav = content.startswith(b'RIFF') and b'WAVE' in content[:12]
                        print(f"   ✅ Arquivo WAV válido: {is_wav}")
                        
                        # Salva o arquivo baixado
                        downloaded_path = f"downloaded_{filename}"
                        with open(downloaded_path, 'wb') as f:
                            f.write(content)
                        print(f"   💾 Arquivo salvo como: {downloaded_path}")
                        
                        return {
                            'status': 'success',
                            'file_size': len(content),
                            'content_type': content_type,
                            'is_valid_wav': is_wav,
                            'filename': downloaded_path
                        }
                    else:
                        error_text = await response.text()
                        print(f"❌ Download WAV falhou: Status {response.status}")
                        print(f"   Erro: {error_text}")
                        return {
                            'status': 'failed',
                            'error': f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            print(f"❌ Download WAV falhou: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def test_analysis_with_download_links(self):
        """Testa análise completa com verificação dos links de download"""
        print(f"\n🧪 Testando Análise Completa com Links de Download")
        
        # Primeiro faz uma análise para obter os links
        test_file_content = b"Mock MXF file for download test" + b"X" * 1000
        
        form_data = aiohttp.FormData()
        form_data.add_field(
            'file',
            test_file_content,
            filename='test_download.mxf',
            content_type='application/octet-stream'
        )
        
        try:
            async with aiohttp.ClientSession() as session:
                # Faz a análise
                async with session.post(
                    f"{self.base_url}/analyze",
                    data=form_data
                ) as response:
                    analysis_data = await response.json()
                    
                    print(f"✅ Análise concluída: {analysis_data['status']}")
                    print(f"📊 Request ID: {analysis_data['request_id']}")
                    
                    download_results = {}
                    
                    # Testa download do EDL se disponível
                    if analysis_data.get('arquivo_edl_url'):
                        edl_url = analysis_data['arquivo_edl_url']
                        request_id = analysis_data['request_id']
                        print(f"🔗 EDL URL: {edl_url}")
                        
                        edl_result = await self.test_download_edl(request_id)
                        download_results['edl'] = edl_result
                    
                    # Testa download dos WAVs se disponíveis
                    if analysis_data.get('musicas_detectadas'):
                        for i, musica in enumerate(analysis_data['musicas_detectadas']):
                            if musica.get('arquivo_wav_url'):
                                wav_url = musica['arquivo_wav_url']
                                filename = wav_url.split('/')[-1]
                                print(f"🔗 WAV URL {i+1}: {wav_url}")
                                
                                wav_result = await self.test_download_wav(filename)
                                download_results[f'wav_{i+1}'] = wav_result
                    
                    return {
                        'analysis': analysis_data,
                        'downloads': download_results
                    }
                    
        except Exception as e:
            print(f"❌ Teste de análise com downloads falhou: {e}")
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    async def run_complete_download_test(self):
        """Executa teste completo de download"""
        print("🚀 INICIANDO TESTE COMPLETO DE DOWNLOAD")
        print("=" * 60)
        
        # 1. Cria arquivos de teste
        await self.create_test_files()
        
        # 2. Testa downloads diretos
        print("\n1. 📥 TESTANDO DOWNLOADS DIRETOS")
        direct_results = {}
        
        # Testa download EDL
        edl_result = await self.test_download_edl("test_edl")
        direct_results['edl'] = edl_result
        
        # Testa download WAV  
        wav_result = await self.test_download_wav("song_0.wav")
        direct_results['wav'] = wav_result
        
        # 3. Testa análise com links automáticos
        print("\n2. 🔄 TESTANDO ANÁLISE COM LINKS AUTOMÁTICOS")
        analysis_results = await self.test_analysis_with_download_links()
        
        # Relatório final
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO FINAL - TESTE DE DOWNLOAD")
        print("=" * 60)
        
        # Estatísticas dos downloads diretos
        successful_direct = sum(1 for r in direct_results.values() if r.get('status') == 'success')
        print(f"📥 Downloads Diretos: {successful_direct}/{len(direct_results)} bem-sucedidos")
        
        # Estatísticas da análise
        if analysis_results and 'downloads' in analysis_results:
            successful_analysis = sum(1 for r in analysis_results['downloads'].values() if r.get('status') == 'success')
            print(f"🔗 Downloads via Análise: {successful_analysis}/{len(analysis_results['downloads'])} bem-sucedidos")
        
        print(f"\n💾 Arquivos baixados salvos como 'downloaded_*'")
        
        return {
            'direct_downloads': direct_results,
            'analysis_downloads': analysis_results
        }

async def main():
    """Função principal de teste de download"""
    tester = FileDownloadTester()
    
    print("🎵 FASTAPI DOWNLOAD TEST - EDL e WAV Files")
    print("💡 Testando endpoints de download de arquivos")
    print("⏳ Executando testes...\n")
    
    results = await tester.run_complete_download_test()
    
    print("\n" + "=" * 60)
    print("✅ TESTE DE DOWNLOAD CONCLUÍDO!")
    print("🎯 Verifique os arquivos baixados no diretório atual")
    
    return results

if __name__ == "__main__":
    # Executa os testes de download
    download_results = asyncio.run(main())
    
    # Verifica se algum download falhou
    all_direct = download_results.get('direct_downloads', {})
    direct_failures = [k for k, v in all_direct.items() if v.get('status') != 'success']
    
    if direct_failures:
        print(f"❌ Downloads diretos com falha: {direct_failures}")
    else:
        print("🎉 Todos os downloads diretos foram bem-sucedidos!")