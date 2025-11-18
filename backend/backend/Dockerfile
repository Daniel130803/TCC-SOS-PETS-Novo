# Multi-stage build: reduz tamanho da imagem final
# Stage 1: Builder (instala dependências)
FROM python:3.13-slim as builder

# Metadados
LABEL maintainer="Daniel130803"
LABEL description="S.O.S Pets Backend - Django REST API"

# Variáveis de ambiente para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependências do sistema necessárias para mysqlclient e Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copia apenas requirements para aproveitar cache do Docker
COPY requirements.txt .

# Instala dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 2: Runtime (imagem final enxuta)
FROM python:3.13-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=backend.settings

# Dependências runtime mínimas (apenas bibliotecas necessárias)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    libjpeg62-turbo \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root para segurança
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/media /app/staticfiles && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copia dependências instaladas do builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copia código da aplicação
COPY --chown=appuser:appuser . .

# Muda para usuário não-root
USER appuser

# Expõe porta 8000
EXPOSE 8000

# Healthcheck: verifica se o servidor está respondendo
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/schema/').read()" || exit 1

# Script de entrada (executará migrações e coletará estáticos antes de subir)
COPY --chown=appuser:appuser docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Comando padrão: Gunicorn (servidor WSGI para produção)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "backend.wsgi:application"]
