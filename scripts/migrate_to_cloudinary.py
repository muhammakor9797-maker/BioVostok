"""
Скрипт для переноса существующих изображений из media/goods/ в Cloudinary.
Запуск: python scripts/migrate_to_cloudinary.py
"""
import os
import sys
import django

# Настраиваем Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Загружаем .env вручную
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path)
print('Loaded .env from', dotenv_path)

django.setup()

from goods.models import Product
import cloudinary
import cloudinary.uploader
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = BASE_DIR / 'media'


def test_connection():
    """Проверяет подключение к Cloudinary."""
    print()
    print('Проверка подключения к Cloudinary...')
    try:
        # Пробуем загрузить тестовое изображение (1x1 пиксель)
        result = cloudinary.uploader.upload(
            'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
            public_id='_test_connection',
            overwrite=True
        )
        print('  [OK] Подключение к Cloudinary работает!')
        print('  Cloud Name:', os.environ.get('CLOUDINARY_CLOUD_NAME', 'не указан'))
        print('  Test URL:', result['secure_url'])

        # Удаляем тестовое изображение
        cloudinary.uploader.destroy('_test_connection')
        print('  Тестовое изображение удалено')
        return True
    except Exception as e:
        print('  [ERR] Ошибка подключения к Cloudinary:', e)
        print('  Проверьте CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET в .env')
        return False


def migrate_images():
    """Переносит все изображения товаров в Cloudinary."""
    products = Product.objects.all()
    total = products.count()
    success = 0
    failed = 0
    
    print()
    print('Найдено товаров:', total)
    print('=' * 60)
    
    for product in products:
        try:
            # Проверяем, есть ли у товара изображение
            if not product.image:
                print(f'[{product.id}] {product.name} - нет изображения, пропускаю')
                continue
            
            # Получаем путь к файлу
            local_path = MEDIA_ROOT / product.image.name
            
            if not local_path.exists():
                print(f'[{product.id}] {product.name} - файл не найден: {local_path}')
                failed += 1
                continue
            
            # Открываем файл и загружаем в Cloudinary
            sys.stdout.write(f'[{product.id}] {product.name} - загружаю {local_path.name}... ')
            sys.stdout.flush()
            
            with open(local_path, 'rb') as f:
                # Загружаем в Cloudinary
                result = cloudinary.uploader.upload(
                    f,
                    public_id=f'goods/{product.id}_{product.slug}',
                    overwrite=True,
                    resource_type='image'
                )
            
            print('[OK] Cloudinary URL:', result['secure_url'][:60] + '...')
            success += 1
            
        except Exception as e:
            print(f'[ERR] {e}')
            failed += 1
    
    print()
    print('=' * 60)
    print(f'Готово! Загружено: {success}, Ошибок: {failed}')
    print(f'Всего товаров: {total}')


if __name__ == '__main__':
    print('Миграция изображений в Cloudinary')
    print('=' * 60)
    print()
    
    # Сначала проверяем подключение
    if not test_connection():
        sys.exit(1)
    
    # Спрашиваем подтверждение
    print()
    response = input('Начать перенос изображений? (y/n): ')
    if response.lower() == 'y':
        migrate_images()
    else:
        print('Отменено.')