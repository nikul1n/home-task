# Базовый образ с Python 3.12
FROM python:3.12-slim

# Установка системных зависимостей (для uv и компиляции некоторых пакетов)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
ENV UV_VERSION=0.5.4
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Рабочая директория
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей
RUN uv sync --frozen --no-cache --no-dev

# Копируем исходный код
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]