#!/bin/sh
echo "Aguardando o banco de dados em $DB_HOST:$DB_PORT..."
MAX_ATTEMPTS=30
ATTEMPTS_LEFT=$MAX_ATTEMPTS

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 2
  ATTEMPTS_LEFT=$((ATTEMPTS_LEFT-1))
  if [ $ATTEMPTS_LEFT -eq 0 ]; then
    echo "Erro: Banco de dados não respondeu após $MAX_ATTEMPTS tentativas."
    exit 1
  fi
done

echo "Banco de dados está disponível!"

echo "Executando migrations..."
python manage.py migrate --noinput

echo "Coletando arquivos estáticos (verbose)..."
python manage.py collectstatic --noinput -v 2

# python manage.py collectstatic --noinput

exec "$@"
