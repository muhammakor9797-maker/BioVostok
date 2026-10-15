# -*- coding: utf-8 -*-
"""
Скрипт для создания/сброса паролей суперпользователей (Beget).
Логины и пароли задаются через переменные окружения:

ADMIN_USERNAME / ADMIN_PASSWORD
ADMIN2_USERNAME / ADMIN2_PASSWORD

Запуск на сервере:
  ADMIN_USERNAME=admin ADMIN_PASSWORD='...' ADMIN2_USERNAME=ayrat \
  ADMIN2_PASSWORD='...' python scripts/create_superuser.py
"""
import os
import sys

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()


def ensure_superuser(username, password, email=''):
    """Создаёт суперпользователя или сбрасывает ему пароль."""
    if not username or not password:
        print(f'SKIP: не задан username или password ({username!r})')
        return

    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f'SUCCESS: пользователь "{username}" обновлён (пароль сброшен)')
    else:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f'SUCCESS: суперпользователь "{username}" создан')


ensure_superuser(
    os.environ.get('ADMIN_USERNAME'),
    os.environ.get('ADMIN_PASSWORD'),
    os.environ.get('ADMIN_EMAIL', ''),
)
ensure_superuser(
    os.environ.get('ADMIN2_USERNAME'),
    os.environ.get('ADMIN2_PASSWORD'),
    os.environ.get('ADMIN2_EMAIL', ''),
)

print('Готово. Вход в админку: /admin/')
