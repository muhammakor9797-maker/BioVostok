"""Безопасная диагностика подключения к базе данных (без вывода секретов)."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path, override=False)

DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
has_url = bool(DATABASE_URL)

print(f'DATABASE_URL задан: {has_url}')
if has_url:
    from urllib.parse import urlparse
    import dj_database_url

    parsed = urlparse(DATABASE_URL)
    print(f'Хост: {parsed.hostname}')
    print(f'Порт: {parsed.port or 5432}')
    print(f'Имя БД: {parsed.path.lstrip("/") if parsed.path else "(не указан)"}')
    print(f'Пользователь: {parsed.username or "(не указан)"}')
    print(f'Пароль: {"***SET***" if parsed.password else "(не задан)"}')
    print(f'Схема: {parsed.scheme}')
    print(f'Query параметры: {parsed.query or "(нет)"}')

    db = dj_database_url.parse(DATABASE_URL, conn_max_age=600, conn_health_checks=True)
    db.setdefault('OPTIONS', {})
    db['OPTIONS'].setdefault('sslmode', 'require')
    print(f'ENGINE: {db["ENGINE"]}')
    print(f'OPTIONS: {db.get("OPTIONS", {})}')
else:
    print('DATABASE_URL не задан — будет использован SQLite (локальная разработка)')

# Проверка подключения (без вывода данных)
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
    print(f'Подключение к БД: OK (SELECT 1 = {result[0]})')
except Exception as e:
    print(f'Подключение к БД: ОШИБКА — {type(e).__name__}')
    # Не выводим текст ошибки, чтобы не раскрыть секреты