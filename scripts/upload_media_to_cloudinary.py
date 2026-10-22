"""
Загружает локальные файлы из media/ в Cloudinary.

public_id формируется так же, как в goods/cloudinary_storage.py:
путь относительно MEDIA_ROOT без расширения. Благодаря этому ссылки
в базе данных (goods/2026/05/10/file.jpg) продолжают работать.

Запуск: python scripts/upload_media_to_cloudinary.py
"""
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


def main():
    if not all([
        settings.CLOUDINARY_CLOUD_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ]):
        raise SystemExit('Cloudinary не настроен: проверьте CLOUDINARY_* в .env')

    media_root = Path(settings.MEDIA_ROOT)
    if not media_root.exists():
        raise SystemExit(f'Папка не найдена: {media_root}')

    files = sorted(p for p in media_root.rglob('*') if p.is_file())
    if not files:
        raise SystemExit(f'В {media_root} нет файлов')

    uploaded = 0
    failed = 0

    for path in files:
        relative = path.relative_to(media_root).as_posix()
        public_id = relative.rsplit('.', 1)[0]
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

    print(f'Готово: загружено {uploaded}, ошибок {failed}, всего файлов {len(files)}')
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main()
