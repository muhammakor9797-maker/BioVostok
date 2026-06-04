"""
passenger_wsgi.py — точка входа для Beget (Passenger)
Этот файл должен лежать в корне проекта (рядом с manage.py)
"""

import os
import sys

# Путь к проекту
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

# Загрузка .env файла если есть
env_file = os.path.join(PROJECT_DIR, '.env')
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, _, value = line.partition('=')
                os.environ.setdefault(key.strip(), value.strip())

# Указываем Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ.setdefault('ALLOWED_HOSTS', '*')

# Активация виртуального окружения если есть
venv_path = os.path.join(PROJECT_DIR, 'venv')
if os.path.exists(venv_path):
    activate_this = os.path.join(venv_path, 'bin', 'activate_this.py')
    if os.path.exists(activate_this):
        with open(activate_this) as f:
            exec(f.read(), {'__file__': activate_this})

# Запуск Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()