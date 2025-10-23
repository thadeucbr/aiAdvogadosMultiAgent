# ==========================================
# DOCKERFILE - BACKEND PLATAFORMA JURÍDICA MULTI-AGENT
# ==========================================
# 
# Este Dockerfile cria uma imagem otimizada para o backend FastAPI
# usando Python 3.12 para garantir compatibilidade com todas as dependências.
#
# IMPORTANTE: Usamos Python 3.12 ao invés de 3.13 porque algumas bibliotecas
# (especialmente tiktoken/PyO3) ainda não têm suporte completo para 3.13.
# ==========================================

# ===== ESTÁGIO 1: Build =====
# Usamos multi-stage build para otimizar o tamanho da imagem final
FROM python:3.12-slim as builder

# Metadados da imagem
LABEL maintainer="Plataforma Jurídica Multi-Agent"
LABEL description="Backend FastAPI com suporte a RAG e ChromaDB"

# Variáveis de ambiente para otimização do Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema necessárias para build
# - build-essential: compiladores C/C++ para pacotes que precisam compilação
# - curl: para download de dependências
# - tesseract-ocr: OCR para extração de texto de PDFs escaneados
# - poppler-utils: ferramentas para conversão de PDF para imagem
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar apenas requirements.txt primeiro (cache layer)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ===== ESTÁGIO 2: Runtime =====
FROM python:3.12-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Instalar apenas dependências de runtime (mais leve)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/dados/chroma_db /app/dados/uploads_temp /app/logs && \
    chown -R appuser:appuser /app

# Definir diretório de trabalho
WORKDIR /app

# Copiar dependências Python do estágio de build
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código da aplicação
COPY --chown=appuser:appuser . .

# Mudar para usuário não-root
USER appuser

# Expor porta da aplicação
EXPOSE 8000

# Healthcheck para monitoramento
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para iniciar a aplicação
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
