🎵 Glogo SONAR 🎵

📋 Sobre o Projeto
Este projeto é uma plataforma web que extrai, de um arquivo MXF, todas as músicas retornando a sua identificação via Shazam e a minutagem onde aparecem, permitindo o download de um arquivo EDL (Edit Decision List).

https://./frontend-screenshot.png

🎯 Contexto do Problema
O problema surgiu por parte da emissora Globo, que, por vezes não conseguia identificar as músicas utilizadas a tempo de legalizar o uso dos direitos autorais. A plataforma automatiza esse processo, identificando automaticamente todas as faixas de áudio em arquivos MXF e gerando relatórios com os timestamps correspondentes.

🏗️ Arquitetura do Sistema
Built With
Backend - Microsserviços

🔹 Microsserviço de Processamento de Áudio - Python

FastAPI | ffmpeg | Shazam API

🔹 Microsserviço de Identificação Musical - C#

.NET Core | Entity Framework

Frontend
⚡ Interface Web - Node.js

React.js | TypeScript 

Infraestrutura
🐳 Containerização - Docker & Docker Compose

🗄️ Armazenamento - PostgreSQL

🔄 Comunicação - REST APIs

🐳 Execução com Docker
Pré-requisitos
Docker Engine 20.10+

Docker Compose 2.0+

4GB RAM mínimo

2GB espaço em disco livre

🚀 Passo a Passo para Execução
Passo 1: Clone o Repositório
bash
git clone https://github.com/Myllena-lins/Globo_Sonar/
cd Globo_Sonar

Passo 2: Inicie os Containers
bash

# Inicie todos os serviços
docker-compose up -d
bash
Passo 4: Verifique o Status dos Serviços
bash
# Verifique se todos os containers estão rodando

docker-compose ps

 Deverá aparecer algo similar a:
NOME                   STATUS              PORTOS
 mxf-extractor-front    running             0.0.0.0:3000->3000/tcp
 mxf-extractor-python   running             0.0.0.0:8000->8000/tcp
 mxf-extractor-csharp   running             0.0.0.0:8080->8080/tcp
 postgres-db            running             0.0.0.0:5432->5432/tcp

Passo 5: Acesse a Aplicação
Frontend: http://localhost:3000

API Python: http://localhost:8000/docs

API C#: http://localhost:8080/swagger

Banco de Dados: localhost:5432

Passo 6: Execute Processamento de Exemplo
bash
# Execute um teste de processamento
docker-compose exec python-service python scripts/test_processing.py
Passo 7: Parar os Serviços
bash
# Parar todos os containers
docker-compose down


🔧 Comandos Úteis
Monitoramento
bash
# Ver logs em tempo real
docker-compose logs -f

# Ver logs específicos
docker-compose logs python-service
docker-compose logs csharp-service
docker-compose logs frontend

# Ver uso de recursos
docker stats
Manutenção
bash
# Reconstruir um serviço específico
docker-compose up -d --build python-service

# Executar comandos dentro do container
docker-compose exec python-service bash
docker-compose exec postgres-db psql -U postgres

