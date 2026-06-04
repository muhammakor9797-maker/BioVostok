#!/bin/bash
set -e

echo "========================================="
echo " Деплой furniture-shop на Timeweb VDS"
echo "========================================="

# Переменные (заполнить перед запуском)
SERVER_IP="ЗАМЕНИТЕ_НА_IP_СЕРВЕРА"
DOMAIN="ЗАМЕНИТЕ_НА_ДОМЕН_ИЛИ_IP"
GIT_REPO="https://github.com/Korneyyy/furniture-shop.git"
DJANGO_USER="django"
PROJECT_DIR="/home/$DJANGO_USER/furniture-shop"

# Обновление системы
echo "[1/8] Обновление системы..."
apt update && apt upgrade -y

# Установка зависимостей
echo "[2/8] Установка Python, Nginx, PostgreSQL, Git..."
apt install -y python3.12 python3.12-venv python3.12-dev libpq-dev nginx postgresql postgresql-contrib git curl

# Создание пользователя
echo "[3/8] Создание пользователя django..."
id -u $DJANGO_USER &>/dev/null || useradd -m -s /bin/bash $DJANGO_USER

# Настройка PostgreSQL
echo "[4/8] Настройка PostgreSQL..."
systemctl enable postgresql
systemctl start postgresql

sudo -u postgres psql -c "CREATE USER django_user WITH PASSWORD 'django_password';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE furniture_shop OWNER django_user;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE furniture_shop TO django_user;" 2>/dev/null || true

# Клонирование репозитория
echo "[5/8] Клонирование проекта..."
if [ -d "$PROJECT_DIR" ]; then
    cd $PROJECT_DIR && git pull
else
    git clone $GIT_REPO $PROJECT_DIR
fi

# Настройка окружения
echo "[6/8] Установка зависимостей Python..."
cd $PROJECT_DIR

# Генерация SECRET_KEY
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")

cat > .env << EOF
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
DATABASE_URL=postgres://django_user:django_password@localhost:5432/furniture_shop
CLOUDINARY_CLOUD_NAME=ЗАМЕНИТЕ
CLOUDINARY_API_KEY=ЗАМЕНИТЕ
CLOUDINARY_API_SECRET=ЗАМЕНИТЕ
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
EOF

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Миграции и статика
echo "[7/8] Миграции и статика..."
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py compilemessages --locale ru 2>/dev/null || true

# Создание superuser (опционально)
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'REMOVED') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell

chown -R $DJANGO_USER:$DJANGO_USER $PROJECT_DIR

# Настройка Gunicorn (systemd)
echo "[8/8] Настройка Gunicorn + Nginx..."

cat > /etc/systemd/system/furniture-shop.service << 'SERVICEFILE'
[Unit]
Description=furniture-shop gunicorn daemon
After=network.target postgresql.service

[Service]
User=django
Group=django
WorkingDirectory=/home/django/furniture-shop
ExecStart=/home/django/furniture-shop/venv/bin/gunicorn config.wsgi:application --workers 3 --bind unix:/home/django/furniture-shop/furniture-shop.sock
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICEFILE

systemctl daemon-reload
systemctl enable furniture-shop
systemctl start furniture-shop || systemctl restart furniture-shop

# Настройка Nginx
cat > /etc/nginx/sites-available/furniture-shop << 'NGINXFILE'
server {
    listen 80;
    server_name _;

    location /static/ {
        alias /home/django/furniture-shop/staticfiles/;
    }

    location /media/ {
        alias /home/django/furniture-shop/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/django/furniture-shop/furniture-shop.sock;
    }
}
NGINXFILE

ln -sf /etc/nginx/sites-available/furniture-shop /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# Открыть порты
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

echo ""
echo "========================================="
echo "✅ Деплой завершён!"
echo "========================================="
echo "Сайт: http://$DOMAIN"
echo "Админка: http://$DOMAIN/admin/"
echo "Логин: admin / Пароль: REMOVED"
echo ""
echo "⚠ Обязательно смените пароль админа!"
echo "⚠ Настройте CLOUDINARY в .env!"
echo "========================================="