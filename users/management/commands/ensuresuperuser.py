# -*- coding: utf-8 -*-
"""
Management command для создания/сброса паролей суперпользователей.
Запуск: python manage.py ensuresuperuser

Использует переменные окружения (обязательно для паролей):
  ADMIN_USERNAME / ADMIN_PASSWORD / ADMIN_EMAIL
  ADMIN2_USERNAME / ADMIN2_PASSWORD / ADMIN2_EMAIL

Пароли без значений по умолчанию — команда пропускает пользователей,
для которых они не заданы.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Создаёт или обновляет суперпользователей из переменных окружения'

    def handle(self, *args, **options):
        import os

        User = get_user_model()

        users_data = [
            {
                'username': os.environ.get('ADMIN_USERNAME', 'admin'),
                'email': os.environ.get('ADMIN_EMAIL', ''),
                'password': os.environ.get('ADMIN_PASSWORD'),
            },
            {
                'username': os.environ.get('ADMIN2_USERNAME'),
                'email': os.environ.get('ADMIN2_EMAIL', ''),
                'password': os.environ.get('ADMIN2_PASSWORD'),
            },
        ]

        for data in users_data:
            username = data['username']
            email = data['email']
            password = data['password']

            if not username or not password:
                continue

            if User.objects.filter(username=username).exists():
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
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(f'SUPERUSER CREATED: {username}')
                )

        self.stdout.write('Все пользователи обработаны')
