# Imagem de execução isolada do TaskAnalyzer (Fase 3 — Bootcamp III).
# Base leve e imutável: python:3.11-slim. Comando padrão: Test Harness completo.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependências primeiro: aproveita o cache de camadas do Docker.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Apenas o necessário para executar e validar o módulo.
COPY conftest.py .
COPY src/ ./src/
COPY tests/ ./tests/

# Execução sem privilégios de root.
RUN useradd --create-home --uid 1000 appuser
USER appuser

CMD ["pytest", "tests/test_harness.py", "-v", "-p", "no:cacheprovider"]
