# 🪑 BioVostok — Интернет-магазин натуральных товаров для здоровья

[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![Cloudinary](https://img.shields.io/badge/Cloudinary-4285F4?style=flat-square&logo=cloudinary)](https://cloudinary.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**BioVostok** — это полнофункциональный интернет-магазин на Django с мультиязычностью (русский, английский, арабский), корзиной покупок, системой отзывов, административной панелью и интеграцией с Cloudinary для хранения изображений.

---

## ✨ Возможности

| Функция | Описание |
|---------|----------|
| 🌍 **Мультиязычность** | Поддержка 3 языков: русский, английский, арабский (через `modeltranslation`) |
| 🛒 **Корзина покупок** | Полноценная корзина с сессионным хранением, добавлением/удалением товаров |
| 📦 **Оформление заказов** | Форма заказа с интеграцией Telegram-уведомлений |
| ⭐ **Отзывы и рейтинг** | Пользователи могут оставлять отзывы с оценками от 1 до 5 |
| 🖼️ **Облачное хранение** | Изображения товаров загружаются в Cloudinary |
| 🔐 **Аутентификация** | Регистрация, вход, управление профилем пользователя |
| 🏷️ **Категории товаров** | Гибкая система категорий с эмодзи-иконками и сортировкой |
| 📱 **Адаптивный дизайн** | Bootstrap 5, мобильная вёрстка |
| 🌐 **SEO-оптимизация** | Open Graph, Twitter Cards, мета-теги |
| 🔧 **Админ-панель** | Полноценная Django Admin с кастомными настройками |

---

## 🛠️ Технологический стек

### Backend
- **Python 3.12**
- **Django 4.2** — основной фреймворк
- **Django Modeltranslation** — мультиязычность моделей
- **Django REST Framework** *(опционально)*
- **Cloudinary** — хранение и оптимизация изображений
- **MySQL / SQLite** — база данных

### Frontend
- **HTML5 / CSS3**
- **Bootstrap 5** — адаптивная сетка
- **JavaScript (vanilla)**
- **Font Awesome** — иконки

### DevOps & Инструменты
- **Git / GitHub** — контроль версий
- **Beget** — хостинг и деплой
- **Passenger** — WSGI-сервер

---

## 📸 Скриншоты

> *Добавьте сюда скриншоты вашего сайта. Рекомендуется:*
> - Главная страница
> - Страница товара
> - Корзина
> - Админ-панель

<!--
![Главная страница](screenshots/main.png)
![Страница товара](screenshots/product.png)
![Корзина](screenshots/cart.png)
--><img width="1919" height="878" alt="cart" src="https://github.com/user-attachments/assets/64a172af-9ca1-46d9-a90c-1ef7b81ca22c" />
<img width="1919" height="877" alt="cart (2)" src="https://github.com/user-attachments/assets/4aa9f4be-034a-4146-a907-1d986281bfbf" />
<img width="1919" height="875" alt="admin-panel" src="https://github.com/user-attachments/assets/f22c55a0-fe8a-4671-b27a-20ca88acc4d9" />
<img width="1919" height="879" alt="product-page2" src="https://github.com/user-attachments/assets/5c8d5d27-83a8-4b78-b855-2561ea3be5ab" />
<img width="1919" height="873" alt="product-page" src="https://github.com/user-attachments/assets/a156a445-df9a-4c2c-8321-21eb4594ebf4" />
<img width="1919" height="880" alt="main-page2" src="https://github.com/user-attachments/assets/4249bf02-258a-437e-b852-22928dfc4389" />
<img width="1919" height="882" alt="main-page" src="https://github.com/user-attachments/assets/1568d6ae-a019-4026-9e7a-41e1ff611cfc" />


---

## 🚀 Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Korneyyy/furniture-shop.git
cd furniture-shop
```

### 2. Создать виртуальное окружение и установить зависимости

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### 3. Настроить переменные окружения

Скопируйте `.env.example` в `.env` и заполните значения:

```bash
cp .env.example .env
```

Параметры в `.env`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3  # или mysql://user:pass@localhost:3306/dbname
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
TELEGRAM_BOT_TOKEN=your_bot_token       # для уведомлений о заказах
TELEGRAM_CHAT_ID=your_chat_id
```

### 4. Выполнить миграции и создать администратора

```bash
python manage.py migrate
python manage.py createsuperuser           # создание админа
```

### 5. Запустить сервер

```bash
python manage.py runserver
```

Откройте [http://127.0.0.1:8000](http://127.0.0.1:8000) в браузере.

### 6. Админ-панель

Админка доступна по адресу [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🌐 Деплой

Проект деплоится на хостинг **Beget** ( Passenger). Файлы конфигурации:

- [`passenger_wsgi.py`](passenger_wsgi.py) — точка входа для Beget
- [`runtime.txt`](runtime.txt) — версия Python

Подробная пошаговая инструкция — в [`README_BEGET.md`](README_BEGET.md).

Все секреты (`SECRET_KEY`, `DATABASE_URL`, пароли, ключи Cloudinary/Telegram/почты)
задаются через `.env` на сервере и в git не хранятся.

---

## 📁 Структура проекта

```
BioVostok/
├── config/              # Настройки Django (settings, urls, wsgi)
├── goods/               # Приложение товаров (модели, формы, админка)
├── carts/               # Приложение корзины
├── orders/              # Приложение заказов
├── users/               # Приложение пользователей
├── scripts/             # Утилиты (создание суперпользователей, миграция на Cloudinary)
├── media/               # Медиафайлы (изображения товаров)
├── static/              # Статические файлы (css, js, изображения)
├── locale/              # Файлы переводов (ru, en, ar)
├── templates/           # HTML-шаблоны
├── requirements.txt     # Зависимости Python
├── passenger_wsgi.py    # Точка входа для Beget
└── .env.example         # Шаблон переменных окружения (скопировать в .env)
```

---

## 🧪 Тестирование

В проекте есть тесты для всех приложений:

```bash
python manage.py test goods carts orders users
```

---

## 🤝 Вклад в проект

Предложения и pull request'ы приветствуются!  
Если нашли баг или есть идея улучшения — создайте [Issue](https://github.com/Korneyyy/furniture-shop/issues).

---

## 📄 Лицензия

Распространяется под лицензией MIT. Подробнее — в файле [LICENSE](LICENSE).

---

## 👤 Автор

**Korneyyy** — Fullstack-разработчик

- GitHub: [@Korneyyy](https://github.com/Korneyyy)
- Проект: [BioVostok](https://github.com/Korneyyy/furniture-shop)

---

> ⭐️ **Если проект показался вам интересным, поставьте звезду на GitHub — это помогает другим разработчикам найти его!**
