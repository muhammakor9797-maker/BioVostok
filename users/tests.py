import os
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password


User = get_user_model()


def _create_superuser_from_env():
    """Реплика логики создания суперпользователя из deploy_init для тестирования."""
    username = os.environ.get('BIOVOSTOK_ADMIN_USERNAME', '').strip()
    email = os.environ.get('BIOVOSTOK_ADMIN_EMAIL', '').strip()
    password = os.environ.get('BIOVOSTOK_ADMIN_PASSWORD', '').strip()

    if not username or not password:
        return 'skipped_no_env'

    if User.objects.filter(username=username).exists():
        return 'skipped_exists'

    validate_password(password)  # может выбросить ValidationError

    User.objects.create_superuser(
        username=username,
        email=email or '',
        password=password,
    )
    return 'created'


class DeployInitSuperuserTests(TestCase):
    """Тесты идемпотентного создания суперпользователя при деплое."""

    def setUp(self):
        # Очищаем пользователей перед каждым тестом
        User.objects.all().delete()

    def _set_env(self, username='admin', email='admin@example.com', password='Str0ng!Pass123'):
        os.environ['BIOVOSTOK_ADMIN_USERNAME'] = username
        os.environ['BIOVOSTOK_ADMIN_EMAIL'] = email
        os.environ['BIOVOSTOK_ADMIN_PASSWORD'] = password

    def _clear_env(self):
        for key in ('BIOVOSTOK_ADMIN_USERNAME', 'BIOVOSTOK_ADMIN_EMAIL', 'BIOVOSTOK_ADMIN_PASSWORD'):
            os.environ.pop(key, None)

    def tearDown(self):
        self._clear_env()
        User.objects.all().delete()

    # --- сценарий 1: создание при первом запуске ---
    @patch('sys.stdout')  # подавляем вывод в тестах
    def test_create_superuser_when_env_vars_set(self, _mock_stdout):
        self._set_env()
        result = _create_superuser_from_env()

        self.assertEqual(result, 'created')
        self.assertTrue(User.objects.filter(username='admin').exists())
        user = User.objects.get(username='admin')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertEqual(user.email, 'admin@example.com')

    # --- сценарий 2: идемпотентность — повторный запуск не меняет пользователя ---
    @patch('sys.stdout')
    def test_idempotent_no_changes_on_repeat(self, _mock_stdout):
        self._set_env(password='Str0ng!Pass123')

        # Первый запуск — создаём
        result1 = _create_superuser_from_env()
        self.assertEqual(result1, 'created')
        user = User.objects.get(username='admin')
        original_password = user.password
        original_is_superuser = user.is_superuser
        original_is_staff = user.is_staff
        original_is_active = user.is_active

        # Второй запуск — пользователь уже существует, ничего не меняется
        result2 = _create_superuser_from_env()
        self.assertEqual(result2, 'skipped_exists')

        user.refresh_from_db()
        self.assertEqual(user.password, original_password)
        self.assertEqual(user.is_superuser, original_is_superuser)
        self.assertEqual(user.is_staff, original_is_staff)
        self.assertEqual(user.is_active, original_is_active)

    # --- сценарий 3: пропуск при отсутствии переменных ---
    @patch('sys.stdout')
    def test_skip_when_env_vars_missing(self, _mock_stdout):
        self._clear_env()
        result = _create_superuser_from_env()
        self.assertEqual(result, 'skipped_no_env')
        self.assertFalse(User.objects.filter(username='admin').exists())

    # --- сценарий 4: пропуск при отсутствии только пароля ---
    @patch('sys.stdout')
    def test_skip_when_password_missing(self, _mock_stdout):
        os.environ['BIOVOSTOK_ADMIN_USERNAME'] = 'admin'
        os.environ['BIOVOSTOK_ADMIN_EMAIL'] = 'admin@example.com'
        # BIOVOSTOK_ADMIN_PASSWORD не задан
        result = _create_superuser_from_env()
        self.assertEqual(result, 'skipped_no_env')
        self.assertFalse(User.objects.filter(username='admin').exists())

    # --- сценарий 5: отказ от слабого пароля ---
    @patch('sys.stdout')
    def test_reject_weak_password(self, _mock_stdout):
        self._set_env(password='123')  # слишком короткий и простой
        with self.assertRaises(ValidationError):
            _create_superuser_from_env()
        self.assertFalse(User.objects.filter(username='admin').exists())

    # --- сценарий 6: пустой пароль не создаёт пользователя ---
    @patch('sys.stdout')
    def test_reject_empty_password(self, _mock_stdout):
        self._set_env(password='')
        result = _create_superuser_from_env()
        self.assertEqual(result, 'skipped_no_env')
        self.assertFalse(User.objects.filter(username='admin').exists())

    # --- сценарий 7: существующий обычный пользователь не становится суперпользователем ---
    @patch('sys.stdout')
    def test_existing_regular_user_not_modified(self, _mock_stdout):
        # Создаём обычного пользователя с тем же username
        User.objects.create_user(username='admin', email='old@example.com', password='OldPass123!')
        self._set_env()
        result = _create_superuser_from_env()
        self.assertEqual(result, 'skipped_exists')
        user = User.objects.get(username='admin')
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    # --- сценарий 8: валидация пароля через Django валидаторы ---
    @patch('sys.stdout')
    def test_password_validation_runs(self, _mock_stdout):
        self._set_env(password='password')  # слишком распространённый пароль
        with self.assertRaises(ValidationError):
            validate_password('password')
        self.assertFalse(User.objects.filter(username='admin').exists())
