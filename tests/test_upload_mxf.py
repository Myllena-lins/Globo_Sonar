import asyncio
import aiohttp
import os
from pathlib import Path
import json
from datetime import datetime
import time

class FastMXFUploadTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.mxf_folder = Path("tests/files")
        self.timeout = aiohttp.ClientTimeout(total=300)  # 5 minutos timeout
    
    def get_existing_mxf_files(self):
        """Busca arquivos MXF existentes"""
        print("🔍 Buscando arquivos MXF existentes...")
        
        if not self.mxf_folder.exists():
            print(f"❌ Pasta não encontrada: {self.mxf_folder}")
            return []
        
        mxf_files = list(self.mxf_folder.glob("*.mxf"))
        
        if not mxf_files:
            print(f"❌ Nenhum arquivo MXF encontrado")
            return []
        
        # Ordena por tamanho (menor primeiro para testes rápidos)
        mxf_files.sort(key=lambda x: x.stat().st_size)
        
        print(f"✅ Encontrados {len(mxf_files)} arquivos MXF:")
        for mxf_file in mxf_files:
            file_size_mb = mxf_file.stat().st_size / (1024 * 1024)
            print(f"   📁 {mxf_file.name} ({file_size_mb:.1f} MB)")
        
        return mxf_files
    
    async def test_upload_single_mxf(self, mxf_path):
        """Testa upload de um arquivo MXF com medição de tempo"""
        print(f"\n🧪 Testando Upload: {mxf_path.name}")
        
        start_time = time.time()
        
        try:
            # Lê o arquivo
            file_size = mxf_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            print(f"   📏 Tamanho: {file_size_mb:.1f} MB")
            
            with open(mxf_path, 'rb') as f:
                file_content = f.read()
            
            # Prepara o form data
            form_data = aiohttp.FormData()
            form_data.add_field(
                'file',
                file_content,
                filename=mxf_path.name,
                content_type='application/octet-stream'
            )
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/analyze",
                    data=form_data
                ) as response:
                    
                    response_data = await response.json()
                    end_time = time.time()
                    total_time = end_time - start_time
                    
                    if response.status == 200:
                        speed_mbps = (file_size / (1024 * 1024)) / total_time
                        print(f"✅ Upload bem-sucedido em {total_time:.1f}s ({speed_mbps:.1f} MB/s)")
                        print(f"   Request ID: {response_data.get('request_id')}")
                        print(f"   Tempo Processamento: {response_data.get('tempo_processamento', 0):.2f}s")
                        
                        # Verificação rápida do nome
                        saved_path = response_data.get('arquivo_salvo_em', '')
                        if saved_path and "_" in Path(saved_path).name:
                            print(f"✅ Arquivo salvo com nome correto")
                        
                        return {
                            'status': 'success',
                            'response_data': response_data,
                            'file_size_mb': file_size_mb,
                            'upload_time': total_time,
                            'speed_mbps': speed_mbps,
                            'test_name': f'upload_{mxf_path.name}'
                        }
                    else:
                        print(f"❌ Upload falhou em {total_time:.1f}s: Status {response.status}")
                        return {
                            'status': 'failed',
                            'error': f"HTTP {response.status}",
                            'upload_time': total_time,
                            'test_name': f'upload_{mxf_path.name}'
                        }
                        
        except asyncio.TimeoutError:
            end_time = time.time()
            total_time = end_time - start_time
            print(f"❌ Timeout após {total_time:.1f}s")
            return {
                'status': 'failed',
                'error': 'Timeout',
                'upload_time': total_time,
                'test_name': f'upload_{mxf_path.name}'
            }
        except Exception as e:
            end_time = time.time()
            total_time = end_time - start_time
            print(f"❌ Upload falhou em {total_time:.1f}s: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'upload_time': total_time,
                'test_name': f'upload_{mxf_path.name}'
            }
    
    async def test_small_files_first(self):
        """Testa primeiro os arquivos menores para debug rápido"""
        mxf_files = self.get_existing_mxf_files()
        
        if not mxf_files:
            return []
        
        print(f"\n🚀 Testando {len(mxf_files)} arquivos (do menor para o maior)")
        
        results = []
        for mxf_file in mxf_files:
            file_size_mb = mxf_file.stat().st_size / (1024 * 1024)
            
            # Pula arquivos muito grandes no teste inicial

            result = await self.test_upload_single_mxf(mxf_file)
            results.append(result)
            
            # Pausa maior entre arquivos grandes
            if file_size_mb > 100000000:
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(1)
        
        return results
    
    async def run_fast_test(self):
        """Executa teste rápido"""
        print("🚀 INICIANDO TESTE RÁPIDO DE UPLOAD")
        print("=" * 60)
        
        results = await self.test_small_files_first()
        
        # Relatório de performance
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE PERFORMANCE")
        print("=" * 60)
        
        successful_uploads = [r for r in results if r.get('status') == 'success']
        
        if successful_uploads:
            avg_speed = sum(r.get('speed_mbps', 0) for r in successful_uploads) / len(successful_uploads)
            avg_time = sum(r.get('upload_time', 0) for r in successful_uploads) / len(successful_uploads)
            
            print(f"✅ Uploads bem-sucedidos: {len(successful_uploads)}/{len(results)}")
            print(f"📊 Velocidade média: {avg_speed:.1f} MB/s")
            print(f"⏱️  Tempo médio: {avg_time:.1f}s")
            
            # Detalhes por arquivo
            print(f"\n📋 Detalhes por arquivo:")
            for result in successful_uploads:
                test_name = result.get('test_name', '')
                file_size = result.get('file_size_mb', 0)
                upload_time = result.get('upload_time', 0)
                speed = result.get('speed_mbps', 0)
                print(f"   • {test_name}: {file_size:.1f}MB em {upload_time:.1f}s ({speed:.1f} MB/s)")
        
        return results

async def main():
    """Função principal otimizada"""
    tester = FastMXFUploadTester()
    
    print("🎵 TESTE RÁPIDO - UPLOAD MXF")
    print("💡 Testando apenas arquivos menores para debug rápido")
    print("⏳ Executando...\n")
    
    start_time = time.time()
    results = await tester.run_fast_test()
    total_time = time.time() - start_time
    
    print(f"\n⏱️  Tempo total do teste: {total_time:.1f}s")
    print("✅ Teste concluído!")

if __name__ == "__main__":
    asyncio.run(main()) 