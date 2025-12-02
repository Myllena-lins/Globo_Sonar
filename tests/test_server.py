import asyncio
import aiohttp
import json
from datetime import datetime

class FastAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    async def test_health_check(self):
        """Testa o endpoint de health check"""
        print("🧪 Testando Health Check...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    data = await response.json()
                    print(f"✅ Health Check: {json.dumps(data, indent=2)}")
                    return data
        except Exception as e:
            print(f"❌ Health Check falhou: {e}")
            return None
    
    async def test_analysis_scenarios(self):
        """Testa múltiplas análises para obter diferentes cenários mockados"""
        print("🧪 Testando Diferentes Cenários de Análise...")
        print("=" * 60)
        
        scenarios = []
        
        for i in range(6):  # Testa mais vezes para ver diferentes cenários
            print(f"\n📦 Executando análise {i+1}/6...")
            
            test_file_content = f"Mock MXF file analysis {i} - {datetime.now().timestamp()}".encode() + b"X" * 500
            
            form_data = aiohttp.FormData()
            form_data.add_field(
                'file',
                test_file_content,
                filename=f'test_analysis_{i}.mxf',
                content_type='application/octet-stream'
            )
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/analyze",
                        data=form_data
                    ) as response:
                        data = await response.json()
                        
                        # Identifica o tipo de cenário
                        has_musicas = data.get('musicas_detectadas') is not None
                        has_edl = data.get('arquivo_edl') is not None
                        
                        if has_musicas and has_edl:
                            scenario_type = "Músicas + EDL"
                        elif has_musicas:
                            scenario_type = "Apenas Músicas"
                        elif has_edl:
                            scenario_type = "Apenas EDL"
                        else:
                            scenario_type = "Nenhum Resultado"
                        
                        print(f"  ✅ Cenário {i+1}: {scenario_type}")
                        print(f"     📝 Mensagem: {data.get('mensagem')}")
                        
                        if has_musicas:
                            print(f"     🎵 Músicas: {len(data['musicas_detectadas'])} detectadas")
                            for musica in data['musicas_detectadas']:
                                print(f"        - {musica['artista']} - {musica['musica']} (t: {musica['timestamp']}s)")
                        
                        if has_edl:
                            print(f"     📁 EDL: {data['arquivo_edl']}")
                        
                        scenarios.append({
                            'scenario_number': i + 1,
                            'scenario_type': scenario_type,
                            'data': data,
                            'status': 'success'
                        })
                        
            except Exception as e:
                print(f"  ❌ Análise {i+1} falhou: {e}")
                scenarios.append({
                    'scenario_number': i + 1,
                    'scenario_type': 'Erro',
                    'error': str(e),
                    'status': 'failed'
                })
        
        return scenarios
    
    async def test_specific_scenario(self, scenario_name="music_only"):
        """Testa um cenário específico forçando um request_id específico"""
        print(f"🧪 Testando Cenário Específico: {scenario_name}")
        
        # Gera conteúdo único baseado no cenário para forçar um hash específico
        if scenario_name == "music_only":
            content = b"MUSIC_ONLY_SCENARIO" + b"X" * 1000  # Força cenário 0
        elif scenario_name == "edl_only":
            content = b"EDL_ONLY_SCENARIO" + b"Y" * 1000    # Força cenário 1
        elif scenario_name == "both":
            content = b"BOTH_SCENARIO" + b"Z" * 1000        # Força cenário 2
        else:
            content = b"EMPTY_SCENARIO" + b"W" * 1000       # Força cenário 3
        
        form_data = aiohttp.FormData()
        form_data.add_field(
            'file',
            content,
            filename=f'scenario_{scenario_name}.mxf',
            content_type='application/octet-stream'
        )
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/analyze",
                    data=form_data
                ) as response:
                    data = await response.json()
                    
                    print(f"✅ Cenário '{scenario_name}':")
                    print(f"📊 Dados completos: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    return data
                    
        except Exception as e:
            print(f"❌ Cenário específico falhou: {e}")
            return None
    
    async def test_download_test_file(self):
        """Testa o download do arquivo de teste"""
        print("🧪 Testando Download de Arquivo de Teste...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/test-file") as response:
                    if response.status == 200:
                        content = await response.read()
                        print(f"✅ Arquivo de teste baixado ({len(content)} bytes)")
                        print(f"   Primeiros 50 bytes: {content[:50]}")
                        return {
                            'file_size': len(content),
                            'first_bytes': content[:50].decode('utf-8', errors='ignore'),
                            'status': 'success'
                        }
                    else:
                        print(f"❌ Download falhou: {response.status}")
                        return {'status': 'failed', 'error': f'HTTP {response.status}'}
        except Exception as e:
            print(f"❌ Download de teste falhou: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    async def test_invalid_file_type(self):
        """Testa envio de arquivo com tipo inválido"""
        print("🧪 Testando Arquivo Inválido...")
        
        test_file_content = b"This is not an MXF file"
        
        form_data = aiohttp.FormData()
        form_data.add_field(
            'file',
            test_file_content,
            filename='invalid_file.txt',  # Arquivo não MXF
            content_type='text/plain'
        )
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/analyze",
                    data=form_data
                ) as response:
                    data = await response.json()
                    print(f"✅ Validação de arquivo funcionou:")
                    print(f"   Erro: {data.get('detail')}")
                    print(f"   Status: {response.status}")
                    return data
                    
        except Exception as e:
            print(f"❌ Teste de arquivo inválido falhou: {e}")
            return None
    
    async def run_comprehensive_test(self):
        """Executa todos os testes e retorna todos os dados mockados"""
        print("🚀 INICIANDO TESTE COMPLETO DO FASTAPI SERVER")
        print("=" * 70)
        
        all_results = {}
        
        # 1. Health Check
        print("\n1. 🏥 TESTANDO HEALTH CHECK")
        health_data = await self.test_health_check()
        all_results['health_check'] = health_data
        
        # 2. Download Test File
        print("\n2. 📥 TESTANDO DOWNLOAD DE ARQUIVO")
        download_data = await self.test_download_test_file()
        all_results['download_test'] = download_data
        
        # 3. Teste de arquivo inválido
        print("\n3. ❌ TESTANDO ARQUIVO INVÁLIDO")
        invalid_file_data = await self.test_invalid_file_type()
        all_results['invalid_file_test'] = invalid_file_data
        
        # 4. Cenários específicos
        print("\n4. 🎯 TESTANDO CENÁRIOS ESPECÍFICOS")
        specific_scenarios = {}
        
        for scenario in ["music_only", "edl_only", "both", "empty"]:
            scenario_data = await self.test_specific_scenario(scenario)
            specific_scenarios[scenario] = scenario_data
            await asyncio.sleep(0.5)  # Pequena pausa entre requests
        
        all_results['specific_scenarios'] = specific_scenarios
        
        # 5. Múltiplos cenários aleatórios
        print("\n5. 🔄 TESTANDO MÚLTIPLOS CENÁRIOS ALEATÓRIOS")
        random_scenarios = await self.test_analysis_scenarios()
        all_results['random_scenarios'] = random_scenarios
        
        # Relatório final
        print("\n" + "=" * 70)
        print("📊 RELATÓRIO FINAL - DADOS MOCKADOS OBTIDOS")
        print("=" * 70)
        
        self._print_summary(all_results)
        
        return all_results
    
    def _print_summary(self, all_results):
        """Imprime um resumo dos dados obtidos"""
        
        # Health Check
        if all_results.get('health_check'):
            print(f"🏥 Health Check: {all_results['health_check']}")
        
        # Download
        if all_results.get('download_test', {}).get('status') == 'success':
            print(f"📥 Download: {all_results['download_test']['file_size']} bytes")
        
        # Cenários específicos
        specific_scenarios = all_results.get('specific_scenarios', {})
        print(f"\n🎯 Cenários Específicos Testados: {len(specific_scenarios)}")
        
        for scenario_name, data in specific_scenarios.items():
            if data:
                music_count = len(data.get('musicas_detectadas', []))
                has_edl = data.get('arquivo_edl') is not None
                print(f"   {scenario_name}: {music_count} músicas, EDL: {has_edl}")
        
        # Cenários aleatórios
        random_scenarios = all_results.get('random_scenarios', [])
        scenario_types = {}
        for scenario in random_scenarios:
            if scenario['status'] == 'success':
                scenario_type = scenario['scenario_type']
                scenario_types[scenario_type] = scenario_types.get(scenario_type, 0) + 1
        
        print(f"\n🔄 Cenários Aleatórios: {len(random_scenarios)} execuções")
        for scenario_type, count in scenario_types.items():
            print(f"   {scenario_type}: {count} vezes")
        
        # Exemplo de dados completos de um cenário
        print(f"\n📋 Exemplo de Dados Completos (Primeiro Cenário Específico):")
        if specific_scenarios and next(iter(specific_scenarios.values())):
            first_scenario = next(iter(specific_scenarios.values()))
            print(json.dumps(first_scenario, indent=2, ensure_ascii=False))

async def main():
    """Função principal que retorna todos os dados mockados"""
    tester = FastAPITester()
    
    print("🎵 FASTAPI AUDIO ANALYSIS SERVER - TESTE DE DADOS MOCKADOS")
    print("💡 Este teste demonstrará todos os cenários de resposta da API")
    print("⏳ Executando testes...\n")
    
    all_mock_data = await tester.run_comprehensive_test()
    
    print("\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO!")
    print("📁 Todos os dados mockados foram obtidos e exibidos acima.")
    print("\n💡 Acesse http://localhost:8000/docs para ver a documentação completa")
    
    return all_mock_data

if __name__ == "__main__":
    # Executa os testes e obtém os dados
    mock_data = asyncio.run(main())
    
    # Opcional: Salvar em arquivo JSON para análise
    with open('mock_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(mock_data, f, indent=2, ensure_ascii=False, default=str)
    
    print("💾 Resultados salvos em 'mock_test_results.json'")