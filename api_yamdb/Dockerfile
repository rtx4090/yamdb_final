
FROM python:3.7-slim

# Создать директорию вашего приложения.
WORKDIR /app

# Скопировать с локального компьютера файл зависимостей
# в директорию /app.
COPY api_yamdb/requirements.txt .

# Выполнить установку зависимостей внутри контейнера.
RUN pip3 install -r requirements.txt --no-cache-dir

COPY api_yamdb .

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ]