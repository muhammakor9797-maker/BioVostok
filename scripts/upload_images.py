# -*- coding: utf-8 -*-
"""Скрипт для загрузки старых изображений в Cloudinary."""
import os
import sys

# Добавляем корень проекта в PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

# Явно конфигурируем Cloudinary (на случай, если django-cloudinary-storage не подцепил)
import cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

import cloudinary.uploader
import cloudinary.api
from goods.models import Product
from pathlib import Path

BASE_DIR = Path(project_root)
MEDIA_ROOT = BASE_DIR / 'media'
LOG_FILE = BASE_DIR / 'cloudinary_upload_log.txt'

log_lines = []

def log(msg):
    log_lines.append(msg)
    print(msg)

log(f"Cloudinary upload script")
log(f"=======================")
log(f"Cloud name: {cloudinary.config().cloud_name}")
log(f"")

# Загружаем изображения товаров
products = Product.objects.exclude(image='')
total = products.count()
success = 0
failed = 0

for product in products:
    try:
        local_path = MEDIA_ROOT / product.image.name
        log(f"[{product.id}] {product.name} -> looking for {local_path}")
        
        if not local_path.exists():
            log(f"  -> FILE NOT FOUND!")
            failed += 1
            continue
        
        with open(local_path, 'rb') as f:
            result = cloudinary.uploader.upload(
                f,
                public_id=f'goods/{product.id}_{product.slug}',
                overwrite=True,
                resource_type='image'
            )
        
        log(f"  -> OK: {result['secure_url']}")
        success += 1
    except Exception as e:
        log(f"  -> ERR: [{type(e).__name__}] {e}")
        failed += 1

log(f"")
log(f"Done. Success: {success}, Failed: {failed}, Total: {total}")

# Проверяем, что загрузилось в Cloudinary
log(f"")
log(f"Checking Cloudinary resources:")
try:
    result = cloudinary.api.resources(type='upload', prefix='goods/', max_results=50)
    resources = result.get('resources', [])
    log(f"  Found {len(resources)} resources:")
    for r in resources:
        log(f"    - {r['public_id']}: {r['secure_url']}")
except Exception as e:
    log(f"  Error checking: {e}")

# Сохраняем лог
with open(LOG_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))

log(f"")
log(f"Log saved to: {LOG_FILE}")