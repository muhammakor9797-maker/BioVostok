# -*- coding: utf-8 -*-
"""Deploy initialization command for Amvera deployment.
Сначала выполняются миграции, затем собираются статические файлы.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Инициализация для деплоя: запуск миграций и сбор статических файлов'

    def handle(self, *args, **options):
        self.stdout.write("Запуск миграций базы данных...")
        from django.core.management import call_command
        call_command('migrate', verbosity=1)

        self.stdout.write("Сбор статических файлов...")
        call_command('collectstatic', verbosity=1, '--noinput')

        self.stdout.write(
            self.style.SUCCESS('Успешная инициализация деплоя!')
        )