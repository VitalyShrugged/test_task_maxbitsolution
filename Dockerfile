# Этап сборки зависимостей
FROM python:3.12-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем системные зависимости
RUN apt-get update && \
    apt-get install -y libpq-dev gcc

# Обновляем pip и устанавливаем зависимости в виде wheels
RUN python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Финальный этап
FROM python:3.12-slim

WORKDIR /app

# Устанавливаем системные зависимости для работы с PostgreSQL
RUN apt-get update && \
    apt-get install -y libpq-dev

# Копируем сгенерированные wheels и устанавливаем их
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Копируем исходный код приложения
COPY . .

# Указываем команду для запуска
CMD ["python", "main.py"]
