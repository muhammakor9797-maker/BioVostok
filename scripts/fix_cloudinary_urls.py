# -*- coding: utf-8 -*-
"""
Скрипт перезагружает изображения в Cloudinary с правильными public_id,
которые соответствуют тому, что Django ожидает от ImageField.
"""
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

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
LOG_FILE = BASE_DIR / 'fix_cloudinary_log.txt'

log_lines = []

def log(msg):
    log_lines.append(msg)
    print(msg)

# 1. Проверяем, какие изображения есть в БД
log("=== 1. Товары и их image поля ===")
products = Product.objects.exclude(image='')
for p in products:
    log(f"ID:{p.id} | image: {p.image} | slug: {p.slug}")

# 2. Удаляем старые неправильные изображения из Cloudinary
log("")
log("=== 2. Удаляем старые изображения из Cloudinary ===")
try:
    result = cloudinary.api.resources(type='upload', prefix='goods/', max_results=50)
    for r in result.get('resources', []):
        log(f"Удаляю: {r['public_id']}")
        cloudinary.uploader.destroy(r['public_id'], invalidate=True)
except Exception as e:
    log(f"Ошибка при получении/удалении: {e}")

# 3. Загружаем с правильным public_id (как в БД)
log("")
log("=== 3. Загружаем с правильными именами ===")

for product in products:
    try:
        local_path = MEDIA_ROOT / product.image.name
        if not local_path.exists():
            log(f"[{product.id}] ФАЙЛ НЕ НАЙДЕН: {local_path}")
            continue
        
        # public_id должен совпадать с image.name без расширения
        # Например: goods/2026/05/16/5890910051965717754
        public_id = product.image.name.rsplit('.', 1)[0]
        
        with open(local_path, 'rb') as f:
            result = cloudinary.uploader.upload(
                f,
                public_id=public_id,
                overwrite=True,
                resource_type='image'
            )
        log(f"[{product.id}] {product.name}")
        log(f"     public_id: {public_id}")
        log(f"     URL: {result['secure_url']}")
    except Exception as e:
        log(f"[{product.id}] ОШИБКА: {type(e).__name__}: {e}")

# 4. Проверяем результат
log("")
log("=== 4. Ресурсы в Cloudinary ===")
try:
    result = cloudinary.api.resources(type='upload', prefix='goods/', max_results=50)
    for r in result.get('resources', []):
        log(f"  {r['public_id']} -> {r['secure_url']}")
    log(f"  Всего: {len(result.get('resources', []))}")
except Exception as e:
    log(f"Ошибка: {e}")

# Сохраняем лог
with open(LOG_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))

log("")
log(f"Лог сохранён: {LOG_FILE}")