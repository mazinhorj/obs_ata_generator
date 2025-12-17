# Use uma imagem base oficial do Python 3.10 (Necessário para Streamlit novo)
FROM python:3.10-slim

# Variáveis de ambiente para o Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Diretório de trabalho
WORKDIR /app

# 1. Copiar apenas os arquivos de definição de dependência primeiro
COPY pyproject.toml poetry.lock* /app/

# 2. Instalar dependências
# --no-root: Não tenta instalar o projeto atual (pois o código ainda não foi copiado)
RUN rm -f poetry.lock && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# 3. Copiar o restante do código da aplicação
COPY . /app

# Expor a porta do Streamlit
EXPOSE 8501

# Comando para rodar a aplicação
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]