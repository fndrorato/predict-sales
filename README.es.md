# Predict Sales — Sistema de Predicción de Ventas

Sistema completo de predicción de ventas desarrollado para el supermercado **BOX MAYORISTA**. La plataforma integra machine learning para proyección de demanda, gestión de órdenes de compra, control de stock y un chatbot asistente, todo en una interfaz web responsiva.

## Arquitectura

El proyecto está compuesto por tres módulos independientes que se comunican entre sí:

```
predict-sales/
├── forecast/       # Servicio de ML — predicción de ventas (Flask + MLflow)
├── server/         # Backend — API REST + WebSocket (Django)
├── web/            # Frontend — interfaz web (React)
└── docker-compose.yml
```

### forecast
Microservicio Python responsable del entrenamiento y serving de los modelos de predicción de ventas. Expone una API y un dashboard propio para la visualización de las predicciones.

- **Framework:** Flask
- **Modelos:** Prophet, XGBoost, scikit-learn
- **Seguimiento de experimentos:** MLflow
- **Puerto:** `5001`

### server
Backend principal de la aplicación. Gestiona autenticación, órdenes de compra, stock, proveedores, sucursales y notificaciones en tiempo real. También integra un chatbot con RAG (Retrieval-Augmented Generation).

- **Framework:** Django 5 + Django REST Framework
- **Base de datos:** PostgreSQL
- **Caché / colas:** Redis
- **WebSocket:** Django Channels + Daphne
- **Autenticación:** JWT (SimpleJWT)
- **Chatbot:** LangChain + ChromaDB + Groq
- **Puerto:** `8000` (o `5001` vía Docker)

### web
Frontend de la aplicación, que consume la API REST y WebSocket del backend.

- **Framework:** React.js (CoreUI Admin Template)
- **Puerto:** `3000`

## Requisitos previos

- [Docker](https://www.docker.com/) y Docker Compose
- Python 3.11+ (para ejecución local de `forecast`)
- Node.js 18+ (para ejecución local de `web`)

## Configuración

Cree un archivo `.env` en la raíz del proyecto con las variables necesarias:

```env
# Base de datos
DB_NAME=compras
DB_USER=postgres
DB_PASSWORD=su_contraseña

# Django
SECRET_KEY=su_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
```

Cada módulo puede tener su propio `.env` para variables específicas (ver `.env` dentro de `forecast/` y `web/`).

## Ejecución con Docker

El `docker-compose.yml` en la raíz levanta todos los servicios de una vez:

```bash
docker compose up --build
```

| Servicio   | URL                        |
|------------|----------------------------|
| Frontend   | http://localhost:3000      |
| Backend    | http://localhost:5001      |
| PostgreSQL | localhost:5438             |

> El servicio `forecast` tiene su propio `docker-compose.yml` dentro de `forecast/` y puede iniciarse de forma independiente.

## Ejecución local (sin Docker)

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
# MLflow UI disponible en http://localhost:5002
```

### Frontend (web)

```bash
cd web
npm install
npm start
```

## Principales funcionalidades

- **Dashboard** — vista general de ventas e indicadores
- **Predicción de ventas** — proyección de demanda por producto y sucursal usando ML
- **Gestión de órdenes de compra** — creación, aprobación y seguimiento de OCs
- **Control de stock** — monitoreo por sucursal y proveedor
- **Gestión de ítems y proveedores**
- **Chatbot asistente** — consultas en lenguaje natural vía RAG
- **Notificaciones en tiempo real** — vía WebSocket
- **Administración de usuarios y grupos**

## Stack tecnológico

| Capa          | Tecnología                                      |
|---------------|-------------------------------------------------|
| Frontend      | React.js, CoreUI, AG Grid, Handsontable         |
| Backend       | Django 5, DRF, Daphne, Channels                 |
| ML / Forecast | Flask, Prophet, XGBoost, MLflow, scikit-learn   |
| Base de datos | PostgreSQL 15                                   |
| Caché         | Redis 7                                         |
| IA / Chatbot  | LangChain, ChromaDB, Groq                       |
| Contenedores  | Docker, Docker Compose                          |

## Licencia

MIT License
