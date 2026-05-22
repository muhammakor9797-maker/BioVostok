# -*- coding: utf-8 -*-
"""
Management command для автоматического создания суперпользователя.
Запускается при каждом деплое на Render.
Использует переменные окружения ADMIN_USERNAME и ADMIN_PASSWORD.

Если переменные не заданы - использует значения по умолчанию.
Если пользователь уже существует - обновляет пароль.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Создаёт или обновляет суперпользователя из переменных окружения'

    def handle(self, *args, **options):
        import os
        
        User = get_user_model()
        
        # Берём данные из переменных окружения или используем значения по умолчанию
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        password = os.environ.get('ADMIN_PASSWORD', 'REMOVED')
        email = os.environ.get('ADMIN_EMAIL', 'admin@admin.com')
        
        if User.objects.filter(username=username).exists():
            # Обновляем существующего пользователя
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'SUPERUSER UPDATED: {username}')
            )
        else:
            # Создаём нового суперпользователя
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'SUPERUSER CREATED: {username}')
            )
        
        self.stdout.write(f'Login: {username}')