# -*- coding: utf-8 -*-
"""
Кастомное хранилище для Cloudinary.
Используется вместо django-cloudinary-storage для совместимости с Django 6.0.
"""
import os
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.storage import Storage
from django.core.files.base import File
from django.utils.deconstruct import deconstructible

import cloudinary
import cloudinary.uploader
import cloudinary.api


@deconstructible
class CloudinaryStorage(Storage):
    """
    Django storage backend for Cloudinary.
    Загружает файлы в Cloudinary и возвращает URL для доступа к ним.
    """
    
    def __init__(self, folder=None):
        self.folder = folder or ''

    def _get_public_id(self, name):
        """Преобразует путь файла в public_id для Cloudinary."""
        # Убираем расширение файла
        name_without_ext = name.rsplit('.', 1)[0] if '.' in name else name
        if self.folder:
            return f'{self.folder}/{name_without_ext}'
        return name_without_ext

    def _save(self, name, content):
        """Сохраняет файл в Cloudinary."""
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
        """Возвращает URL файла в Cloudinary."""
        if not name:
            return ''
        
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
        """Проверяет, существует ли файл в Cloudinary."""
        try:
            public_id = self._get_public_id(name)
            cloudinary.api.resource(public_id)
            return True
        except:
            return False

    def delete(self, name):
        """Удаляет файл из Cloudinary."""
        try:
            public_id = self._get_public_id(name)
            cloudinary.uploader.destroy(public_id)
        except:
            pass

    def listdir(self, path):
        """Список файлов в папке (не реализовано)."""
        return [], []

    def size(self, name):
        """Размер файла (не реализовано)."""
        return 0

    def get_accessed_time(self, name):
        """Время последнего доступа (не реализовано)."""
        import datetime
        return datetime.datetime.now()

    def get_created_time(self, name):
        """Время создания (не реализовано)."""
        import datetime
        return datetime.datetime.now()

    def get_modified_time(self, name):
        """Время изменения (не реализовано)."""
        import datetime
        return datetime.datetime.now()