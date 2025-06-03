# 🚀 Деплой на Heroku

## 📋 Подготовка

1. **Установите Heroku CLI:**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Windows
   # Скачайте с https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Авторизация в Heroku:**
   ```bash
   heroku login
   ```

## 🚀 Деплой

1. **Создание приложения:**
   ```bash
   cd /Users/eldar/PycharmProjects/tgdsg
   heroku create dsg-complex-bot
   ```

2. **Настройка переменных окружения:**
   ```bash
   heroku config:set BOT_TOKEN=7094351521:AAGGGNoq_4F1jjmMmJjMaMHp5jWFcuYQVkY
   heroku config:set CHANNEL_USERNAME=@dsgcomplex
   heroku config:set ADMIN_IDS=125861752,1506368833
   heroku config:set DEBUG=False
   ```

3. **Инициализация Git (если не сделано):**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

4. **Деплой:**
   ```bash
   git push heroku main
   ```

5. **Запуск worker:**
   ```bash
   heroku ps:scale worker=1
   ```

## 🔍 Управление

- **Логи:** `heroku logs --tail`
- **Статус:** `heroku ps`
- **Перезапуск:** `heroku restart`
- **Остановка:** `heroku ps:scale worker=0`

## 💰 Стоимость

- **Бесплатно** - до 550 часов в месяц
- **Hobby Plan** - $7/месяц за безлимитную работу 