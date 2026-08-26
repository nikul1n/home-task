# Базовый образ с Python 3.12
FROM python:3.12-slim

# Установка системных зависимостей (для uv и компиляции некоторых пакетов)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Рабочая директория
WORKDIR /app

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock ./

# Установка зависимостей
RUN uv sync --frozen --no-install-project --no-cache --no-dev

# Копируем исходный код
COPY . .

ENV PATH="/app/.venv/bin:$PATH" \
    PYTOHNPATH="/app/src"

# Открываем порт
EXPOSE 8000

# Команда запуска
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]