# syntax=docker/dockerfile:1.4
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  POETRY_VERSION=1.8.2 \
  DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Sistema base y Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential gcc libpq-dev curl git netcat-openbsd && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
  ln -s /root/.local/bin/poetry /usr/local/bin/poetry
  
RUN poetry config virtualenvs.create false

# Instalar solo dependencias de producción
COPY core/backend/pyproject.toml core/backend/poetry.lock ./
RUN poetry install --only main --no-interaction --no-ansi

# Copiar todo el backend (incluyendo app/, run.py, alembic.ini, migrations/, etc.)
COPY core/backend/. .

EXPOSE 8000

ENTRYPOINT ["sh", "-c", "until nc -z -v -w30 postgres 5432; do echo 'Waiting for postgres...'; sleep 5; done; echo 'Postgres is up!'; uvicorn run:app --host 0.0.0.0 --port 8000 --reload"]
