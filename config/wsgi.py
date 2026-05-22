"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Автоматическое создание суперпользователя при старте сервера
# Использует переменные окружения ADMIN_USERNAME и ADMIN_PASSWORD (настройка Render)
_admin_username = os.environ.get('ADMIN_USERNAME', '')
_admin_password = os.environ.get('ADMIN_PASSWORD', '')
if _admin_username and _admin_password:
    try:
        from django.contrib.auth import get_user_model
        _User = get_user_model()
        if _User.objects.filter(username=_admin_username).exists():
            _user = _User.objects.get(username=_admin_username)
            _user.set_password(_admin_password)
            _user.is_superuser = True
            _user.is_staff = True
            _user.is_active = True
            _user.save()
            print(f'[wsgi] ADMIN "{_admin_username}" UPDATED')
        else:
            _User.objects.create_superuser(
                username=_admin_username,
                email=os.environ.get('ADMIN_EMAIL', 'admin@admin.com'),
                password=_admin_password
            )
            print(f'[wsgi] ADMIN "{_admin_username}" CREATED')
    except Exception as _e:
        print(f'[wsgi] ADMIN ERROR: {_e}')
