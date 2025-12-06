# 🎵 Glogo SONAR 🎵

## 📋 Sobre o Projeto
Este projeto é uma plataforma web que extrai, de um arquivo MXF, todas as músicas retornando a sua identificação via Shazam e a minutagem onde aparecem, permitindo o download de um arquivo EDL (Edit Decision List).

![Frontend](https://./frontend-screenshot.png)

---

## 🎯 Contexto do Problema
O problema surgiu por parte da emissora Globo, que, por vezes não conseguia identificar as músicas utilizadas a tempo de legalizar o uso dos direitos autorais. A plataforma automatiza esse processo, identificando automaticamente todas as faixas de áudio em arquivos MXF e gerando relatórios com os timestamps correspondentes.

---

## 📝 Processamento e Download do EDL

Para utilizar a plataforma, basta acessar o site e fazer o upload do arquivo MXF, seja arrastando-o para a área indicada ou clicando no botão **Enviar**. Após o envio, o sistema processará automaticamente o conteúdo e exibirá o resultado com todas as músicas identificadas. Em seguida, você pode verificar as informações detectadas ou realizar o download do arquivo **EDL** gerado.

---

## 🏗️ Arquitetura do Sistema

### Built With

### Backend - Microsserviços

#### 🔹  Microsserviço de Identificação Musical - Python
- FastAPI  
- ffmpeg  
- Shazam API  

#### 🔹  Microsserviço de Processamento de Áudio - C#
- .NET Core  
- Entity Framework  

### Frontend
⚡ Interface Web - Node.js  
- React.js  
- TypeScript  

### Infraestrutura
- 🐳 Containerização - Docker & Docker Compose  
- 🗄️ Armazenamento - PostgreSQL  
- 🔄 Comunicação - REST APIs  

---

## 🐳 Execução com Docker

### Pré-requisitos
- Docker Engine 20.10+  
- Docker Compose 2.0+  

---

## 🚀 Passo a Passo para Execução

### Passo 1: Clone o Repositório
```bash
git clone https://github.com/Myllena-lins/Globo_Sonar/
cd Globo_Sonar
```


### Passo 2: Inicie os Containers
```bash
docker-compose up -d
```


### Passo 3: Verifique o Status dos Serviços
```bash
docker-compose ps
```

Deverá aparecer algo similar a:

```bash
NOME                    STATUS              PORTOS
mxf-extractor-front     running             0.0.0.0:3000->3000/tcp
mxf-extractor-python    running             0.0.0.0:8000->8000/tcp
mxf-extractor-csharp    running             0.0.0.0:8080->8080/tcp
postgres-db             running             0.0.0.0:5432->5432/tcp
```
### Passo 4: Acesse a Aplicação

Frontend: [http://localhost:3000](http://localhost:3000)>


