import os
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Готовит приложение к запуску на продакшене (DADA Cloud / Amvera): миграции БД, начальные товары, суперпользователь, статика'

    def handle(self, *args, **options):
        self.stdout.write('=== Deploy init started ===')

        # 1. Миграции — идемпотентны, безопасно запускать повторно.
        # Применяются ВСЕГДА: на пустой БД создают схему с нуля, на существующей —
        # доводят до актуального состояния. Любая ошибка прерывает выполнение
        # команды, и запуск сценария (Procfile / amvera.yml: set -eux ... && exec gunicorn)
        # не дойдёт до gunicorn — приложение не стартует при неудачных миграциях.
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

        # 3. Суперпользователь — только если заданы все BIOVOSTOK_ADMIN_* переменные.
        # Идемпотентно: существующего пользователя не трогаем.
        username = os.environ.get('BIOVOSTOK_ADMIN_USERNAME', '').strip()
        email = os.environ.get('BIOVOSTOK_ADMIN_EMAIL', '').strip()
        password = os.environ.get('BIOVOSTOK_ADMIN_PASSWORD', '').strip()

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                'BIOVOSTOK_ADMIN_USERNAME или BIOVOSTOK_ADMIN_PASSWORD не заданы — '
                'суперпользователь не создан'
            ))
        else:
            from django.contrib.auth import get_user_model
            from django.core.exceptions import ValidationError
            from django.contrib.auth.password_validation import validate_password

            User = get_user_model()

            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    f'Суперпользователь с username="{username}" уже существует — пропускаю'
                )
            else:
                # Валидация пароля через встроенные Django валидаторы
                try:
                    validate_password(password)
                except ValidationError as exc:
                    self.stdout.write(self.style.ERROR(
                        f'Пароль для "{username}" не прошёл валидацию: '
                        f'{exc.messages[0]} — суперпользователь не создан'
                    ))
                else:
                    User.objects.create_superuser(
                        username=username,
                        email=email or '',
                        password=password,
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f'Суперпользователь "{username}" создан'
                    ))

        # 4. Статика.
        self.stdout.write('Собираю статические файлы (collectstatic)...')
        call_command('collectstatic', interactive=False, verbosity=1)
        self.stdout.write(self.style.SUCCESS('Статика собрана'))

        self.stdout.write(self.style.SUCCESS('=== Deploy init completed ==='))
