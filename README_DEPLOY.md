# Деплой furniture-shop на Timeweb VDS

## 1. Что нужно знать (все данные в панели Timeweb)

| Данные | Где взять |
|--------|-----------|
| **IP сервера** | Панель Timeweb → Серверы → Ваш сервер (Witty Callisto) |
| **SSH логин/пароль** | Там же, в настройках сервера |
| **Cloudinary данные** | Ваш аккаунт cloudinary.com |

## 2. Подключиться к серверу

Откройте **Terminal** (командную строку) на вашем компьютере и выполните:

```bash
ssh root@IP_ВАШЕГО_СЕРВЕРА
```

Пароль вам покажет Timeweb в панели сервера.

## 3. Скопировать и запустить скрипт деплоя

После подключения к серверу, выполните по одной команде:

```bash
apt update && apt install -y git curl
```

```bash
curl -O https://raw.githubusercontent.com/Korneyyy/furniture-shop/main/deploy.sh
```

```bash
nano deploy.sh
```

**Замените в файле:**
- `SERVER_IP` → на IP вашего сервера
- `DOMAIN` → на IP вашего сервера (пока нет домена)
- `CLOUDINARY_CLOUD_NAME` → ваш cloud name
- `CLOUDINARY_API_KEY` → ваш api key
- `CLOUDINARY_API_SECRET` → ваш api secret

Сохраните файл (Ctrl+X, Y, Enter).

Затем запустите:

```bash
chmod +x deploy.sh && bash deploy.sh
```

Скрипт сделает всё сам.

## 4. После деплоя

Сайт будет доступен по IP вашего сервера в браузере:
```
http://IP_ВАШЕГО_СЕРВЕРА
```

Админка:
```
http://IP_ВАШЕГО_СЕРВЕРА/admin/
```
Логин: `admin`
Пароль: `REMOVED`

**Сразу смените пароль админа!**

## 5. Если что-то пошло не так

Напишите мне, я исправлю.

---

**Подготовлено для Timeweb VDS (Witty Callisto: 1 vCPU, 1 ГБ RAM, 15 ГБ NVMe)**