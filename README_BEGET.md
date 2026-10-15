# Деплой BioVostok на Beget

Проект: Django + MySQL, точка входа — `passenger_wsgi.py`.

## 1. Купить хостинг

1. Зайдите на **beget.com**
2. Нажмите **"Заказать хостинг"** и выберите тариф с поддержкой Python и MySQL
3. Зарегистрируйтесь и оплатите (российские карты, СБП, ЮMoney)
4. После оплаты получите **домен 3-го уровня** (например `ваш-логин.beget.tech`) — свой домен можно подключить отдельно

## 2. Создать базу данных MySQL

1. Панель управления → **Базы данных** → **Создать базу**
2. Тип: **MySQL**; придумайте имя БД и пользователя, задайте пароль
3. Строка подключения будет вида:

```
mysql://пользователь:пароль@localhost:3306/имя_бд?charset=utf8
```

## 3. Подключить домен ( biovostok.shop )

В панели Beget: **Сайты** → **Домены** → добавить домен и указать NS-серверы Beget
(или A-запись на IP хостинга, если домен куплен у другого регистратора).

## 4. Загрузить проект

### Вариант A — через Git (проще)

1. Панель Beget → **Сайты** → напротив домена **"Управление"** → включите **доступ по SSH**
2. Подключитесь по данным из панели:

```bash
ssh ваш_логин@ваш_логин.beget.tech
```

3. Выполните:

```bash
cd ~/ваш_домен/public_html
git clone https://github.com/Korneyyy/furniture-shop.git .
```

### Вариант B — через FTP

1. Панель Beget → **FTP** → создайте FTP-аккаунт
2. Скачайте FileZilla и подключитесь (логин/пароль из панели)
3. Скопируйте файлы проекта (кроме `venv/`, `__pycache__`, `data_dump.json`,
   `.env.example*` — нужен только `.env`) в папку `public_html`

## 5. Настроить окружение

Создайте файл `public_html/.env` (шаблон — [`.env.example_beget`](.env.example_beget)):

```env
SECRET_KEY=<сгенерируйте: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=False
ALLOWED_HOSTS=biovostok.shop,www.biovostok.shop
CSRF_TRUSTED_ORIGINS=https://biovostok.shop,https://www.biovostok.shop
DATABASE_URL=mysql://пользователь:пароль@localhost:3306/имя_бд?charset=utf8
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<надёжный пароль>
```

> ⚠️ `.env` никогда не коммитьтся в git (см. `.gitignore`).

## 6. Настроить Python в Beget

Панель Beget → **Сайты** → **"Управление"** → раздел **Python**:

1. Включите **"Поддержка Python"**
2. Версия Python: **3.12**
3. Точка входа: **passenger_wsgi.py** (файл уже в проекте)
4. Путь к `requirements.txt`: `requirements.txt`
5. Нажмите **"Сохранить"**

## 7. Миграции, данные, статика, администратор

По SSH из `public_html`:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python scripts/create_superuser.py
```

`create_superuser.py` читает `ADMIN_USERNAME` / `ADMIN_PASSWORD` из `.env`
и создаёт (или сбрасывает пароль) суперпользователя.

Если нужно перенести данные со старого сайта — залейте файл дампа на сервер
(локально, не через git) и выполните:

```bash
python manage.py loaddata data_dump.json
```

После переноса **смените пароли всех администраторов** через `changepassword`
или `scripts/create_superuser.py` с новыми значениями.

## 8. SSL-сертификат

Панель Beget → **Сайты** → **"Управление"** → **SSL** → выпустить бесплатный
Let's Encrypt для `biovostok.shop` и `www.biovostok.shop`.

Пока сертификат не выпущен, в `.env` должно быть `SECURE_SSL_REDIRECT=False`,
иначе — `True` (перенаправление http → https).

## 9. Перезапустить сайт

Панель Beget → **Сайты** → **"Перезапустить"**, подождите 1–2 минуты,
откройте `https://biovostok.shop`.

## 10. Если сайт не работает

1. Панель Beget → **Сайты** → **Логи ошибок** — посмотрите текст
2. Проверьте `.env` (нет опечаток, `DEBUG=False` не сломан)
3. Убедитесь, что в панели указаны Python 3.12 и `passenger_wsgi.py`
