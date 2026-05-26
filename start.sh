#!/bin/bash
set -e

python manage.py migrate --noinput
python manage.py ensure_superusers
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT