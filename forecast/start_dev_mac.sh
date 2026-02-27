#!/bin/bash
# start_dev_mac.sh
# Script para iniciar o ambiente de desenvolvimento no Mac

set -e  # Parar se houver erro

echo "🚀 Iniciando ambiente de desenvolvimento no Mac..."
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ========================================
# 1. TESTAR CONEXÕES COM BANCOS DE DADOS
# ========================================
echo -e "${YELLOW}Testando conexões com bancos de dados...${NC}"

# Criar script Python temporário para testes
cat > test_connections.py << 'PYTHON_SCRIPT'
import sys
import os

def test_sqlserver():
    """Testa conexão com SQL Server"""
    try:
        import pyodbc
        from app.config import Config
        
        print("  → Testando SQL Server...", end=" ")
        conn = pyodbc.connect(Config.SQLSERVER_CONNECTION_STRING, timeout=5)
        conn.close()
        print("✅")
        return True
    except ImportError:
        print("❌ (pyodbc não instalado)")
        return False
    except Exception as e:
        print(f"❌")
        print(f"    Erro: {str(e)[:100]}")
        return False

def test_postgresql():
    """Testa conexão com PostgreSQL"""
    try:
        import psycopg2
        from app.config import Config
        
        print("  → Testando PostgreSQL...", end=" ")
        conn = psycopg2.connect(Config.POSTGRES_CONNECTION_STRING, connect_timeout=5)
        conn.close()
        print("✅")
        return True
    except ImportError:
        print("❌ (psycopg2 não instalado)")
        return False
    except Exception as e:
        print(f"❌")
        print(f"    Erro: {str(e)[:100]}")
        return False

if __name__ == "__main__":
    print("\n🔍 Verificando conexões:")
    
    sqlserver_ok = test_sqlserver()
    postgresql_ok = test_postgresql()
    
    print("")
    
    if not sqlserver_ok or not postgresql_ok:
        print("❌ Falha na conexão com banco(s) de dados!")
        print("\n💡 Dicas:")
        if not sqlserver_ok:
            print("   - Verifique SQLSERVER_CONNECTION_STRING no .env ou app/config.py")
            print("   - Confirme se o servidor SQL Server está acessível")
            print("   - Instale: pip install pyodbc")
        if not postgresql_ok:
            print("   - Verifique POSTGRES_CONNECTION_STRING no .env ou app/config.py")
            print("   - Confirme se PostgreSQL está rodando (psql -U postgres)")
            print("   - Instale: pip install psycopg2-binary")
        print("")
        sys.exit(1)
    
    print("✅ Todas as conexões OK!")
    sys.exit(0)
PYTHON_SCRIPT

# Executar teste de conexões
if ! python test_connections.py; then
    echo -e "${RED}Não é possível continuar sem conexões com bancos de dados.${NC}"
    rm test_connections.py
    exit 1
fi

# Limpar script temporário
rm test_connections.py
echo ""

# ========================================
# 2. VERIFICAR SE MLFLOW ESTÁ INSTALADO
# ========================================
if ! command -v mlflow &> /dev/null
then
    echo -e "${YELLOW}MLflow não encontrado. Instalando...${NC}"
    pip install mlflow scikit-learn
fi

# ========================================
# 3. CRIAR DIRETÓRIOS NECESSÁRIOS
# ========================================
mkdir -p mlruns
mkdir -p logs

# ========================================
# 4. VERIFICAR SE PORTA 5001 ESTÁ LIVRE
# ========================================
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Porta 5001 já está em uso!${NC}"
    echo "Processos usando a porta 5001:"
    lsof -i :5001
    echo ""
    echo "Sugestão: pkill -f mlflow"
    exit 1
fi

# ========================================
# 5. INICIAR MLFLOW EM BACKGROUND
# ========================================
echo -e "${GREEN}Iniciando MLflow na porta 5001...${NC}"
mlflow server \
    --backend-store-uri sqlite:///mlflow.db \
    --default-artifact-root ./mlruns \
    --host 0.0.0.0 \
    --port 5001 \
    > logs/mlflow.log 2>&1 &

MLFLOW_PID=$!
echo "MLflow PID: $MLFLOW_PID"

# ========================================
# 6. AGUARDAR MLFLOW INICIAR
# ========================================
echo "Aguardando MLflow inicializar..."
MAX_WAIT=30
COUNTER=0
while [ $COUNTER -lt $MAX_WAIT ]; do
    if curl -s http://localhost:5001/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ MLflow rodando em http://localhost:5001${NC}"
        break
    fi
    COUNTER=$((COUNTER + 1))
    sleep 1
    echo -n "."
done

if [ $COUNTER -eq $MAX_WAIT ]; then
    echo -e "\n${YELLOW}⚠️  MLflow pode não ter iniciado. Verifique logs/mlflow.log${NC}"
    tail -20 logs/mlflow.log
fi

# ========================================
# 7. VERIFICAR SE PORTA 5002 ESTÁ LIVRE
# ========================================
if lsof -Pi :5002 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Porta 5002 já está em uso!${NC}"
    echo "Processos usando a porta 5002:"
    lsof -i :5002
    kill $MLFLOW_PID 2>/dev/null
    exit 1
fi

# ========================================
# 8. INICIAR FLASK NA PORTA 5002
# ========================================
echo ""
echo -e "${GREEN}Iniciando Flask na porta 5002...${NC}"
echo -e "${GREEN}Dashboard: http://localhost:5002${NC}"
echo -e "${GREEN}MLflow UI:  http://localhost:5001${NC}"
echo ""
echo "Para parar os serviços, pressione CTRL+C"
echo ""

export FLASK_APP=run.py
export FLASK_ENV=development
python run.py

# ========================================
# 9. CLEANUP AO ENCERRAR
# ========================================
trap "echo 'Encerrando serviços...'; kill $MLFLOW_PID 2>/dev/null; exit 0" EXIT SIGINT SIGTERM