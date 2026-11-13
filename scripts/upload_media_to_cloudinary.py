"""
Безопасная загрузка локальных файлов из media/ в Cloudinary.

public_id формируется так же, как в goods/cloudinary_storage.py:
путь относительно MEDIA_ROOT без расширения. Благодаря этому ссылки
в базе данных (goods/2026/05/10/file.jpg) продолжают работать.

Скрипт НЕ удаляет существующие ресурсы в Cloudinary,
НЕ меняет записи товаров и базу данных.
При повторном запуске с одинаковыми public_id используется overwrite=True —
существующий ресурс перезаписывается, дубликатов не создаётся.

Режимы работы:
  --check   Только предварительная проверка (без загрузки в Cloudinary)
  --dry-run То же, что --check (алIAS)
  без флагов — реальная загрузка в Cloudinary

Запуск:
  python scripts/upload_media_to_cloudinary.py --check
  python scripts/upload_media_to_cloudinary.py
"""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django

django.setup()

import cloudinary
import cloudinary.uploader
from django.conf import settings

IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'}
VIDEO_EXTENSIONS = {'mp4', 'webm', 'avi'}


def resource_type_for(path):
    ext = path.suffix.lower().lstrip('.')
    if ext in IMAGE_EXTENSIONS:
        return 'image'
    if ext in VIDEO_EXTENSIONS:
        return 'video'
    return 'raw'


def compute_public_id(relative_posix):
    """public_id: путь относительно MEDIA_ROOT без расширения."""
    return relative_posix.rsplit('.', 1)[0] if '.' in relative_posix else relative_posix


def public_id_matches_storage(relative_posix):
    """Проверяет, что public_id совпадает с тем, что формирует CloudinaryStorage."""
    from goods.cloudinary_storage import CloudinaryStorage
    storage = CloudinaryStorage()
    expected = storage._get_public_id(relative_posix)
    actual = compute_public_id(relative_posix)
    return expected == actual, expected, actual


def preflight_check(files, media_root):
    """Предварительная проверка перед загрузкой. Возвращает True, если всё ок."""
    errors = []

    # 1. Все три переменные Cloudinary
    missing = []
    if not settings.CLOUDINARY_CLOUD_NAME:
        missing.append('CLOUDINARY_CLOUD_NAME')
    if not settings.CLOUDINARY_API_KEY:
        missing.append('CLOUDINARY_API_KEY')
    if not settings.CLOUDINARY_API_SECRET:
        missing.append('CLOUDINARY_API_SECRET')
    if missing:
        errors.append(
            f'Не заданы переменные окружения: {", ".join(missing)}. '
            'Задайте их в панели DADA Cloud или в .env'
        )

    # 2. Существование MEDIA_ROOT
    if not media_root.exists():
        errors.append(f'Папка MEDIA_ROOT не найдена: {media_root}')
        return errors

    # 3. Есть ли файлы для загрузки
    if not files:
        errors.append(f'В {media_root} нет файлов для загрузки')
        return errors

    # 4. Соответствие путей и public_id
    for path in files:
        relative = path.relative_to(media_root).as_posix()
        if not path.exists():
            errors.append(f'Файл не найден: {relative}')
            continue
        ok, expected, actual = public_id_matches_storage(relative)
        if not ok:
            errors.append(
                f'Несоответствие public_id для {relative}: '
                f'скрипт={actual}, CloudinaryStorage={expected}'
            )

    return errors


def main():
    parser = argparse.ArgumentParser(
        description='Безопасная загрузка изображений из media/ в Cloudinary.'
    )
    parser.add_argument(
        '--check', '--dry-run', action='store_true',
        help='Только предварительная проверка без реальной загрузки в Cloudinary',
    )
    args = parser.parse_args()
    dry_run = args.check

    media_root = Path(settings.MEDIA_ROOT)

    # Собираем список файлов
    files = sorted(p for p in media_root.rglob('*') if p.is_file()) if media_root.exists() else []

    print('=== Предварительная проверка ===')
    print(f'MEDIA_ROOT: {media_root}')
    print(f'MEDIA_URL: {settings.MEDIA_URL}')
    print(f'Найдено файлов: {len(files)}')
    print()

    if files:
        print('Список файлов для загрузки:')
        for path in files:
            relative = path.relative_to(media_root).as_posix()
            public_id = compute_public_id(relative)
            resource_type = resource_type_for(path)
            print(f'  {relative}  ->  public_id={public_id}  resource_type={resource_type}')
        print()

    # Предварительная проверка
    errors = preflight_check(files, media_root)
    if errors:
        print('ОШИБКИ ПРОВЕРКИ:')
        for e in errors:
            print(f'  [ERR] {e}')
        print()
        sys.exit(1)

    print('Предварительная проверка пройдена успешно.')
    print()

    if dry_run:
        print('Режим --check: реальная загрузка не выполняется.')
        print('Чтобы начать загрузку, запустите скрипт без флага --check.')
        sys.exit(0)

    # Реальная загрузка
    print('=== Начало загрузки в Cloudinary ===')
    print()

    uploaded = 0
    failed = 0

    for path in files:
        relative = path.relative_to(media_root).as_posix()
        public_id = compute_public_id(relative)
        resource_type = resource_type_for(path)

        try:
            result = cloudinary.uploader.upload(
                str(path),
                public_id=public_id,
                overwrite=True,
                resource_type=resource_type,
            )
            uploaded += 1
            print(f'[OK] {relative} -> {result.get("secure_url")}')
        except Exception as exc:
            failed += 1
            print(f'[ERR] {relative}: {exc}')

    print()
    print(f'Готово: загружено {uploaded}, ошибок {failed}, всего файлов {len(files)}')
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main()
