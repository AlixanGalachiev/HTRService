# Базовый образ с Python
FROM python:3.11-slim

# Рабочая директория
WORKDIR /app

# Устанавливаем зависимости для opencv
RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements (если есть)
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Запуск сервиса
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
