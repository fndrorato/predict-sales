#!/bin/bash
# start_docker.sh

set -e

echo "🚀 Iniciando Forecast System (Flask + MLflow)..."
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ==========================================
# 1. VERIFICAR DOCKER
# ==========================================
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker não está rodando!${NC}"
    echo "   Inicie o Docker Desktop e tente novamente."
    exit 1
fi

# ==========================================
# 2. VERIFICAR .env
# ==========================================
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado!${NC}"
    echo "   Criando template..."
    cat > .env << 'EOF'
# PostgreSQL LOCAL
POSTGRES_CONNECTION_STRING=postgresql://postgres:postgres@host.docker.internal:5432/boxcompras

# SQL Server (AJUSTE AQUI!)
SQLSERVER_CONNECTION_STRING=DRIVER={FreeTDS};SERVER=SEU_IP;PORT=1433;DATABASE=pegasus;UID=usuario;PWD=senha;TDS_Version=8.0;

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000

# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5002
FLASK_DEBUG=True
EOF
    echo -e "${RED}   ⚠️  EDITE o arquivo .env com suas credenciais!${NC}"
    echo "   nano .env"
    exit 1
fi

# ==========================================
# 3. VERIFICAR POSTGRESQL LOCAL
# ==========================================
echo -e "${YELLOW}🔍 Verificando PostgreSQL local...${NC}"
if psql -U postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL rodando localmente${NC}"
else
    echo -e "${RED}❌ PostgreSQL não está rodando!${NC}"
    echo ""
    echo "   Iniciar PostgreSQL:"
    echo "   $ brew services start postgresql@14"
    echo ""
    exit 1
fi

# Verificar se database existe
if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw boxcompras; then
    echo -e "${GREEN}✅ Database 'boxcompras' existe${NC}"
else
    echo -e "${YELLOW}⚠️  Database 'boxcompras' não existe. Criando...${NC}"
    psql -U postgres -c "CREATE DATABASE boxcompras;"
    echo -e "${GREEN}✅ Database criado${NC}"
fi

# ==========================================
# 4. LIMPAR CONTAINERS ANTIGOS
# ==========================================
echo ""
echo -e "${YELLOW}🧹 Limpando containers antigos...${NC}"
docker-compose down 2>/dev/null || true

# ==========================================
# 5. BUILD
# ==========================================
echo ""
echo -e "${GREEN}📦 Building imagem Flask...${NC}"
docker-compose build

# ==========================================
# 6. START
# ==========================================
echo ""
echo -e "${GREEN}🚀 Iniciando serviços...${NC}"
docker-compose up -d

# ==========================================
# 7. AGUARDAR SERVIÇOS
# ==========================================
echo ""
echo -e "${YELLOW}⏳ Aguardando serviços iniciarem...${NC}"

# Aguardar MLflow
echo -n "   MLflow"
for i in {1..30}; do
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        echo -e " ${GREEN}✅${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Aguardar Flask
echo -n "   Flask "
for i in {1..30}; do
    if curl -s http://localhost:5002 > /dev/null 2>&1; then
        echo -e " ${GREEN}✅${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# ==========================================
# 8. TESTAR CONEXÕES
# ==========================================
echo ""
echo -e "${YELLOW}🔍 Testando conexões dentro do container...${NC}"

# Testar PostgreSQL
docker exec forecast_flask python << 'EOF' 2>/dev/null
import psycopg2
try:
    conn = psycopg2.connect("postgresql://postgres:postgres@host.docker.internal:5432/boxcompras", connect_timeout=5)
    conn.close()
    print("   PostgreSQL ✅")
except Exception as e:
    print(f"   PostgreSQL ❌ ({e})")
EOF

# Testar SQL Server
docker exec forecast_flask python << 'EOF' 2>/dev/null
import pyodbc
from app.config import Config
try:
    conn = pyodbc.connect(Config.SQLSERVER_CONNECTION_STRING, timeout=5)
    conn.close()
    print("   SQL Server ✅")
except Exception as e:
    print(f"   SQL Server ⚠️  (verifique credenciais no .env)")
EOF

# ==========================================
# 9. STATUS
# ==========================================
echo ""
echo "📊 Status dos containers:"
docker-compose ps

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Sistema iniciado com sucesso!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📱 Interfaces disponíveis:"
echo "   🌐 Flask:  http://localhost:5002"
echo "   📊 MLflow: http://localhost:5001"
echo ""
echo "📝 Comandos úteis:"
echo "   Ver logs:        docker-compose logs -f"
echo "   Ver logs Flask:  docker-compose logs -f flask-app"
echo "   Entrar no Flask: docker exec -it forecast_flask bash"
echo "   Parar tudo:      docker-compose down"
echo ""