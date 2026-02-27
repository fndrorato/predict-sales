# mlflow_start.sh (criar na raiz do projeto)
#!/bin/sh

# Desabilitar validação de host
export GUNICORN_CMD_ARGS="--timeout 120 --forwarded-allow-ips='*' --access-logfile - --error-logfile - --log-level info"

# Iniciar MLflow
exec mlflow server \
  --backend-store-uri file:///mlflow/mlruns \
  --default-artifact-root /mlflow/artifacts \
  --host 0.0.0.0 \
  --port 5000