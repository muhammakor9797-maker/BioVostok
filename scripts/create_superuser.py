# -*- coding: utf-8 -*-
"""
Скрипт для создания суперпользователя на сервере Render.
Запуск на Render: python scripts/create_superuser.py
"""
import os
import sys

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Данные суперпользователя
ADMIN_USERNAME = 'admin'
ADMIN_EMAIL = 'admin@admin.com'
ADMIN_PASSWORD = 'REMOVED'

# Проверяем, существует ли уже такой пользователь
if User.objects.filter(username=ADMIN_USERNAME).exists():
    # Если существует — просто обновляем пароль
    user = User.objects.get(username=ADMIN_USERNAME)
    user.set_password(ADMIN_PASSWORD)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f'SUCCESS: Пользователь "{ADMIN_USERNAME}" обновлён (пароль сброшен)')
else:
    # Создаём нового суперпользователя
    user = User.objects.create_superuser(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD
    )
    print(f'SUCCESS: Суперпользователь "{ADMIN_USERNAME}" создан')

print(f'Логин: {ADMIN_USERNAME}')
print(f'Пароль: {ADMIN_PASSWORD}')
print(f'Вход: https://biovostok.onrender.com/admin/')