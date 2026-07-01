# Deploy

## Production схема

Проект разворачивается через Docker Compose:

- `db` — PostgreSQL
- `backend` — Django + Gunicorn
- `bot` — Telegram bot на aiogram
- `frontend` — сборка Vue-приложения
- `caddy` — веб-сервер, HTTPS, раздача frontend/static/media и проксирование API/admin

## Переменные окружения

На сервере нужно создать файл `.env` на основе `.env.production.example`.

Важные отличия production `.env`:

```env
DJANGO_DEBUG=False
DB_HOST=db
DOMAIN=example.com
TELEGRAM_WEB_APP_URL=https://example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
```

## Первый запуск на сервере

```bash
docker compose -p japanese_sword_crm -f docker-compose.prod.yml up -d --build
docker compose -p japanese_sword_crm -f docker-compose.prod.yml exec backend python manage.py migrate
docker compose -p japanese_sword_crm -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
docker compose -p japanese_sword_crm -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

## Обновление проекта

```bash
git pull
docker compose -p japanese_sword_crm -f docker-compose.prod.yml up -d --build
docker compose -p japanese_sword_crm -f docker-compose.prod.yml exec backend python manage.py migrate
docker compose -p japanese_sword_crm -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

## Проверка

```bash
docker compose -p japanese_sword_crm -f docker-compose.prod.yml ps
docker compose -p japanese_sword_crm -f docker-compose.prod.yml logs --tail=100 backend
docker compose -p japanese_sword_crm -f docker-compose.prod.yml logs --tail=100 bot
docker compose -p japanese_sword_crm -f docker-compose.prod.yml logs --tail=100 caddy
```

Проверить в браузере:

- `https://example.com`
- `https://example.com/api/products/`
- `https://example.com/admin/`

## Backup PostgreSQL

Перед опасными действиями сделать дамп базы:

```bash
docker compose -p japanese_sword_crm -f docker-compose.prod.yml exec db pg_dump -U japanese_sword japanese_sword > backup.sql
```

Не выполнять на production без необходимости:

```bash
docker compose -p japanese_sword_crm -f docker-compose.prod.yml down -v
```

`-v` удаляет volumes, включая volume PostgreSQL.