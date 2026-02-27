# ---------- STAGE 1: builder ----------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# deps do sistema só para build de wheels (adicione o que sua stack exigir)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências de Python em um venv
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
# prefer-binary evita compilar quando existir wheel pronta
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --prefer-binary -r requirements.txt

# ---------- STAGE 2: runtime ----------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Instalar e gerar locale pt_BR.UTF-8
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    locales \
 && sed -i 's/# *pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen \
 && locale-gen pt_BR.UTF-8 \
 && rm -rf /var/lib/apt/lists/*

# Exportar variáveis de locale
ENV LANG=pt_BR.UTF-8 \
    LANGUAGE=pt_BR:pt \
    LC_ALL=pt_BR.UTF-8

WORKDIR /app

# Copia somente o venv pronto do builder
COPY --from=builder /opt/venv /opt/venv

# Copia o projeto (agora limpo graças ao .dockerignore)
COPY . .

# Entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "app.wsgi:application", "-b", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
    