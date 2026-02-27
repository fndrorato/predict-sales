# Predict Sales — Sistema de Previsão de Vendas

> [Leer en Español](README.es.md)

Sistema completo de previsão de vendas desenvolvido para o supermercado **BOX MAYORISTA**. A plataforma integra machine learning para projeção de demanda, gestão de pedidos de compra, controle de estoque e um chatbot assistente, tudo em uma interface web responsiva.

## Arquitetura

O projeto é composto por três módulos independentes que se comunicam entre si:

```
predict-sales/
├── forecast/       # Serviço de ML — previsão de vendas (Flask + MLflow)
├── server/         # Backend — API REST + WebSocket (Django)
├── web/            # Frontend — interface web (React)
└── docker-compose.yml
```

### forecast
Microsserviço Python responsável pelo treinamento e serving dos modelos de previsão de vendas. Expõe uma API e um dashboard próprio para visualização das previsões.

- **Framework:** Flask
- **Modelos:** Prophet, XGBoost, scikit-learn
- **Rastreamento de experimentos:** MLflow
- **Porta:** `5001`

### server
Backend principal da aplicação. Gerencia autenticação, pedidos de compra, estoque, fornecedores, lojas e notificações em tempo real. Também integra um chatbot com RAG (Retrieval-Augmented Generation).

- **Framework:** Django 5 + Django REST Framework
- **Banco de dados:** PostgreSQL
- **Cache / filas:** Redis
- **WebSocket:** Django Channels + Daphne
- **Autenticação:** JWT (SimpleJWT)
- **Chatbot:** LangChain + ChromaDB + Groq
- **Porta:** `8000` (ou `5001` via Docker)

### web
Frontend da aplicação, consumindo a API REST e WebSocket do backend.

- **Framework:** React.js (CoreUI Admin Template)
- **Porta:** `3000`

## Pré-requisitos

- [Docker](https://www.docker.com/) e Docker Compose
- Python 3.11+ (para execução local do `forecast`)
- Node.js 18+ (para execução local do `web`)

## Configuração

Crie um arquivo `.env` na raiz do projeto com as variáveis necessárias:

```env
# Banco de dados
DB_NAME=compras
DB_USER=postgres
DB_PASSWORD=sua_senha

# Django
SECRET_KEY=sua_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

Cada módulo pode ter seu próprio `.env` para variáveis específicas (veja `.env` dentro de `forecast/` e `web/`).

## Execução com Docker

O `docker-compose.yml` na raiz sobe todos os serviços de uma vez:

```bash
docker compose up --build
```

| Serviço   | URL                        |
|-----------|----------------------------|
| Frontend  | http://localhost:3000      |
| Backend   | http://localhost:5001      |
| PostgreSQL| localhost:5438             |

> O serviço `forecast` possui seu próprio `docker-compose.yml` dentro de `forecast/` e pode ser iniciado de forma independente.

## Execução local (sem Docker)

### Backend (server)

```bash
cd server
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
daphne app.asgi:application -b 0.0.0.0 -p 8000
```

### Forecast

```bash
cd forecast
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py
# MLflow UI disponível em http://localhost:5002
```

### Frontend (web)

```bash
cd web
npm install
npm start
```

## Principais funcionalidades

- **Dashboard** — visão geral de vendas e indicadores
- **Previsão de vendas** — projeção de demanda por produto e loja usando ML
- **Gestão de pedidos de compra** — criação, aprovação e acompanhamento de OCs
- **Controle de estoque** — monitoramento por loja e fornecedor
- **Gestão de itens e fornecedores**
- **Chatbot assistente** — consultas em linguagem natural via RAG
- **Notificações em tempo real** — via WebSocket
- **Administração de usuários e grupos**

## Stack tecnológica

| Camada       | Tecnologia                                      |
|--------------|-------------------------------------------------|
| Frontend     | React.js, CoreUI, AG Grid, Handsontable         |
| Backend      | Django 5, DRF, Daphne, Channels                 |
| ML / Forecast| Flask, Prophet, XGBoost, MLflow, scikit-learn   |
| Banco de dados| PostgreSQL 15                                  |
| Cache        | Redis 7                                         |
| IA / Chatbot | LangChain, ChromaDB, Groq                       |
| Containers   | Docker, Docker Compose                          |

## Licença

MIT License
