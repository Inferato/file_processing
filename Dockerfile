# Використовуємо базовий образ Python
FROM python:3.12

# Встановлюємо системні залежності
RUN apt-get update && apt-get install -y \
    python3-dev \
    default-libmysqlclient-dev \
    libgl1-mesa-glx \ 
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо залежності Python
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Додаємо код додатку
COPY . /app

# Встановлюємо змінні середовища
ENV DJANGO_SETTINGS_MODULE=test_task.settings

# Запускаємо сервер Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
