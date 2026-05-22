# -*- coding: utf-8 -*-
import os
import sys
import json

# Исправляем вывод для Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Добавляем корень проекта в PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, '.env'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()
from goods.models import Product
import cloudinary.api

# Сохраняем результаты в файл
output_lines = []

products = Product.objects.exclude(image='')
output_lines.append(f"Товары с изображениями в БД: {products.count()}")
for p in products:
    output_lines.append(f"  ID:{p.id} {p.name} -> image: {p.image}")

output_lines.append("")
output_lines.append("Ресурсы в Cloudinary (goods/):")
try:
    result = cloudinary.api.resources(type='upload', prefix='goods/', max_results=50)
    for resource in result.get('resources', []):
        output_lines.append(f"  {resource['public_id']} -> {resource['secure_url']}")
    output_lines.append(f"\nВсего в Cloudinary: {len(result.get('resources', []))}")
except Exception as e:
    output_lines.append(f"Ошибка получения ресурсов: {e}")

# Записываем в файл
output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'check_result.txt')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"Результат сохранён в {output_path}")