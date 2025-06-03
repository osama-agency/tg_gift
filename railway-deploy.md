# 🚀 Деплой на Railway

## 📋 Подготовка

1. **Зарегистрируйтесь на Railway:**
   - Перейдите на https://railway.app
   - Войдите через GitHub

2. **Подготовка проекта:**
   ```bash
   cd /Users/eldar/PycharmProjects/tgdsg
   git init
   git add .
   git commit -m "Initial commit"
   ```

## 🚀 Деплой

### Способ 1: Через GitHub

1. **Загрузите код на GitHub:**
   ```bash
   # Создайте репозиторий на github.com
   git remote add origin https://github.com/your-username/tgdsg-bot.git
   git branch -M main
   git push -u origin main
   ```

2. **Подключите к Railway:**
   - Войдите на railway.app
   - Нажмите "New Project"
   - Выберите "Deploy from GitHub repo"
   - Выберите ваш репозиторий

### Способ 2: Через Railway CLI

1. **Установите Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Авторизация:**
   ```bash
   railway login
   ```

3. **Деплой:**
   ```bash
   railway deploy
   ```

## ⚙️ Настройка переменных

В панели Railway добавьте переменные:

```
BOT_TOKEN=7094351521:AAGGGNoq_4F1jjmMmJjMaMHp5jWFcuYQVkY
CHANNEL_USERNAME=@dsgcomplex
ADMIN_IDS=125861752,1506368833
DEBUG=False
```

## 🔍 Управление

- **Логи:** В панели Railway → Deployments → Logs
- **Перезапуск:** Railway панель → Redeploy
- **Переменные:** Railway панель → Variables

## 💰 Стоимость

- **$5/месяц** - включает 512MB RAM, безлимитный трафик
- **Hobby Plan** - бесплатно до определенных лимитов 