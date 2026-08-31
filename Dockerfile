# Базовый образ с Python 3.12
FROM python:3.13-slim-bookworm

# Установка системных зависимостей (для uv и компиляции некоторых пакетов)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# Установка uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Рабочая директория
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy 

# Копируем файлы зависимостей
# Кэширование слоя зависимостей
COPY pyproject.toml uv.lock ./


# Установка зависимостей
# RUN uv sync --frozen --no-install-project --no-cache --no-dev
RUN uv sync --frozen --no-install-project --no-dev

# Копируем исходный код
COPY . .

# Синхронизация проекта
RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH" 
    # PYTOHNPATH="/app/src"

RUN mkdir -p /app/data

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]