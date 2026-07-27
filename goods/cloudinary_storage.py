# -*- coding: utf-8 -*-
"""
Кастомное хранилище для Cloudinary.
Используется вместо django-cloudinary-storage для совместимости с Django 6.0.
Если Cloudinary не настроен — автоматически переключается на FileSystemStorage.
"""
import os
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import Storage, FileSystemStorage
from django.core.files.base import File
from django.utils.deconstruct import deconstructible

import cloudinary
import cloudinary.uploader
import cloudinary.api


def _is_cloudinary_configured():
    """Проверяет, настроен ли Cloudinary."""
    return all([
        settings.CLOUDINARY_CLOUD_NAME,
        settings.CLOUDINARY_API_KEY,
        settings.CLOUDINARY_API_SECRET,
    ])


@deconstructible
class CloudinaryStorage(Storage):
    """
    Django storage backend for Cloudinary.
    Загружает файлы в Cloudinary и возвращает URL для доступа к ним.
    Если Cloudinary не настроен — использует FileSystemStorage как fallback.
    """
    
    def __init__(self, folder=None):
        self.folder = folder or ''
        self._fallback = None
        if not _is_cloudinary_configured():
            self._fallback = FileSystemStorage(
                location=settings.MEDIA_ROOT,
                base_url=settings.MEDIA_URL,
            )

    def _get_fallback(self):
        if self._fallback is None:
            if not _is_cloudinary_configured():
                self._fallback = FileSystemStorage(
                    location=settings.MEDIA_ROOT,
                    base_url=settings.MEDIA_URL,
                )
        return self._fallback

    def _get_public_id(self, name):
        """Преобразует путь файла в public_id для Cloudinary."""
        # Убираем расширение файла
        name_without_ext = name.rsplit('.', 1)[0] if '.' in name else name
        if self.folder:
            return f'{self.folder}/{name_without_ext}'
        return name_without_ext

    def _save(self, name, content):
        """Сохраняет файл в Cloudinary или локально."""
        fallback = self._get_fallback()
        if fallback:
            return fallback._save(name, content)
        
        public_id = self._get_public_id(name)
        
        # Определяем тип ресурса по расширению
        ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
        resource_type = 'raw'
        if ext in ('jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'):
            resource_type = 'image'
        elif ext in ('mp4', 'webm', 'avi'):
            resource_type = 'video'
        
        result = cloudinary.uploader.upload(
            content,
            public_id=public_id,
            overwrite=True,
            resource_type=resource_type
        )
        
        # Возвращаем имя файла, которое Django сохранит в поле модели
        return result.get('public_id', name)

    def url(self, name):
        """Возвращает URL файла в Cloudinary или локально."""
        if not name:
            return ''
        
        fallback = self._get_fallback()
        if fallback:
            return fallback.url(name)
        
        # Если имя начинается с http - это уже полный URL
        if name.startswith('http://') or name.startswith('https://'):
            return name
        
        # Если это уже готовый URL Cloudinary
        cloud_name = cloudinary.config().cloud_name
        if cloud_name and f'res.cloudinary.com/{cloud_name}' in name:
            return name
        
        # Строим URL через cloudinary
        public_id = self._get_public_id(name)
        try:
            result = cloudinary.utils.cloudinary_url(public_id)
            if result and len(result) > 0:
                return result[0]
        except:
            pass
        
        # Fallback
        return name

    def exists(self, name):
        """Проверяет, существует ли файл."""
        fallback = self._get_fallback()
        if fallback:
            return fallback.exists(name)
        try:
            public_id = self._get_public_id(name)
            cloudinary.api.resource(public_id)
            return True
        except:
            return False

    def delete(self, name):
        """Удаляет файл."""
        fallback = self._get_fallback()
        if fallback:
            return fallback.delete(name)
        try:
            public_id = self._get_public_id(name)
            cloudinary.uploader.destroy(public_id)
        except:
            pass

    def listdir(self, path):
        """Список файлов в папке."""
        fallback = self._get_fallback()
        if fallback:
            return fallback.listdir(path)
        return [], []

    def size(self, name):
        """Размер файла."""
        fallback = self._get_fallback()
        if fallback:
            return fallback.size(name)
        return 0

    def get_accessed_time(self, name):
        """Время последнего доступа."""
        fallback = self._get_fallback()
        if fallback:
            return fallback.get_accessed_time(name)
        import datetime
        return datetime.datetime.now()

    def get_created_time(self, name):
        """Время создания."""
        fallback = self._get_fallback()
        if fallback:
            return fallback.get_created_time(name)
        import datetime
        return datetime.datetime.now()

    def get_modified_time(self, name):
        """Время изменения."""
        fallback = self._get_fallback()
        if fallback:
            return fallback.get_modified_time(name)
        import datetime
        return datetime.datetime.now()