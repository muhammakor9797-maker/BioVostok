import os
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Подготавливает приложение к запуску на Amvera: миграции, начальные товары, админ, статика'

    def handle(self, *args, **options):
        self.stdout.write('=== Deploy init started ===')

        # 1. Миграции — идемпотентны, безопасно запускать повторно.
        self.stdout.write('Применяю миграции базы данных...')
        call_command('migrate', interactive=False, verbosity=1)
        self.stdout.write(self.style.SUCCESS('Миграции применены'))

        # 2. Начальные товары только если база пустая — существующие данные не трогаем.
        from goods.models import Product

        if Product.objects.exists():
            self.stdout.write('Товары уже есть в базе — загрузку initial_data пропускаю')
        else:
            fixture_candidates = [
                Path('/data/initial_data.json'),
                Path(settings.BASE_DIR) / 'goods' / 'fixtures' / 'initial_goods.json',
            ]
            fixture = next((f for f in fixture_candidates if f.exists()), None)
            if fixture is None:
                self.stdout.write(self.style.WARNING(
                    'Фикстура с начальными товарами не найдена (ни /data/initial_data.json, '
                    'ни goods/fixtures/initial_goods.json) — пропускаю'
                ))
            else:
                self.stdout.write(f'Загружаю начальные товары из {fixture}')
                call_command('loaddata', str(fixture), verbosity=1)
                self.stdout.write(self.style.SUCCESS('Начальные товары загружены'))

        # 3. Суперпользователь — только если задан пароль, иначе пропускаем.
        if os.environ.get('ADMIN_PASSWORD'):
            self.stdout.write('Создаю/обновляю суперпользователя...')
            call_command('ensuresuperuser')
            self.stdout.write(self.style.SUCCESS('Суперпользователь обработан'))
        else:
            self.stdout.write(self.style.WARNING(
                'ADMIN_PASSWORD не задан — суперпользователь не создан'
            ))

        # 4. Статика.
        self.stdout.write('Собираю статические файлы (collectstatic)...')
        call_command('collectstatic', interactive=False, verbosity=1)
        self.stdout.write(self.style.SUCCESS('Статика собрана'))

        self.stdout.write(self.style.SUCCESS('=== Deploy init completed ==='))
