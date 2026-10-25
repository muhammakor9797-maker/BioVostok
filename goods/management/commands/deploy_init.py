import os
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Подготавливает приложение к запуску на Amvera'

    def handle(self, *args, **options):
        call_command('migrate', interactive=False, verbosity=1)

        from goods.models import Product

        fixture = Path('/data/initial_data.json')
        if fixture.exists() and not Product.objects.exists():
            self.stdout.write(f'Загружаю данные из {fixture}')
            call_command('loaddata', str(fixture), verbosity=1)

        if os.environ.get('ADMIN_PASSWORD'):
            call_command('ensuresuperuser')

        call_command('collectstatic', interactive=False, verbosity=0)

        self.stdout.write(self.style.SUCCESS('Deploy init completed'))
