# Берем официальный Python-образ. slim — облегченная Linux-версия без лишнего мусора.
FROM python:3.13-slim

# Не создаем .pyc-файлы внутри контейнера.
ENV PYTHONDONTWRITEBYTECODE=1

# Логи Python сразу выводятся в консоль Docker, без буферизации.
ENV PYTHONUNBUFFERED=1

# Рабочая папка внутри контейнера.
WORKDIR /app

# Сначала копируем зависимости отдельно, чтобы Docker мог кешировать pip install.
COPY requirements.txt .

# Устанавливаем Python-зависимости backend-а и бота.
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект внутрь контейнера.
COPY . .

# Переходим в папку Django-проекта, где лежит manage.py.
WORKDIR /app/japanese_sword

# Команда по умолчанию: запускаем Django через Gunicorn.
CMD ["gunicorn", "japanese_sword.wsgi:application", "--bind", "0.0.0.0:8000"]