# 🚀 ПОЛНОЕ РУКОВОДСТВО ПО ДЕПЛОЮ TELEGRAM БОТА DSG COMPLEX

## 🤖 Информация о боте
- **Username:** @dsgspb_bot
- **Ссылка:** https://t.me/dsgspb_bot
- **Функция:** Выдача промокодов за подписку на @dsgcomplex

---

## 📋 ВАРИАНТЫ ДЕПЛОЯ

### 🏠 **1. ЛОКАЛЬНЫЙ ЗАПУСК (для тестирования)**

**Самый простой способ:**
```bash
cd /Users/eldar/PycharmProjects/tgdsg
./start.sh
```

**Ручной запуск:**
```bash
cd /Users/eldar/PycharmProjects/tgdsg
source .venv/bin/activate
cd .venv
python bot.py
```

**Остановка:**
- Нажмите `Ctrl+C`

---

### 🖥️ **2. VPS СЕРВЕР (Рекомендуется для продакшн)**

**Преимущества:**
- ✅ Полный контроль
- ✅ Высокая надежность
- ✅ Автоматический перезапуск
- ✅ Логирование

**Требования:**
- Ubuntu/Debian сервер
- SSH доступ
- Python 3.9+

**Быстрый деплой:**
1. **Настройте файл `deploy.sh`:**
   ```bash
   nano deploy.sh
   # Измените SERVER_IP на ваш IP
   ```

2. **Запустите деплой:**
   ```bash
   ./deploy.sh
   ```

**Управление на сервере:**
```bash
# Статус
systemctl status tgdsg-bot

# Логи
journalctl -f -u tgdsg-bot

# Перезапуск
systemctl restart tgdsg-bot

# Остановка
systemctl stop tgdsg-bot
```

**Стоимость:** От $3-5/месяц (DigitalOcean, Linode, Vultr)

---

### ☁️ **3. HEROKU (Простой деплой)**

**Преимущества:**
- ✅ Простота деплоя
- ✅ Автоматическое масштабирование
- ✅ Git-based деплой

**Деплой:**
```bash
# 1. Установка Heroku CLI
brew tap heroku/brew && brew install heroku

# 2. Авторизация
heroku login

# 3. Создание приложения
cd /Users/eldar/PycharmProjects/tgdsg
heroku create dsg-complex-bot

# 4. Настройка переменных
heroku config:set BOT_TOKEN=7094351521:AAGGGNoq_4F1jjmMmJjMaMHp5jWFcuYQVkY
heroku config:set CHANNEL_USERNAME=@dsgcomplex
heroku config:set ADMIN_IDS=125861752,1506368833

# 5. Деплой
git init
git add .
git commit -m "Deploy bot"
git push heroku main

# 6. Запуск
heroku ps:scale worker=1
```

**Управление:**
```bash
heroku logs --tail        # Логи
heroku ps                 # Статус
heroku restart            # Перезапуск
heroku ps:scale worker=0  # Остановка
```

**Стоимость:** $7/месяц (Hobby план)

---

### 🚄 **4. RAILWAY (Современная платформа)**

**Преимущества:**
- ✅ Современный интерфейс
- ✅ GitHub интеграция
- ✅ Автоматический деплой

**Деплой через GitHub:**
1. **Загрузите код на GitHub:**
   ```bash
   # Создайте репозиторий на github.com
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/tgdsg-bot.git
   git push -u origin main
   ```

2. **Подключите к Railway:**
   - Войдите на https://railway.app
   - Нажмите "New Project"
   - Выберите "Deploy from GitHub repo"
   - Выберите ваш репозиторий

3. **Настройте переменные:**
   В панели Railway добавьте:
   ```
   BOT_TOKEN=7094351521:AAGGGNoq_4F1jjmMmJjMaMHp5jWFcuYQVkY
   CHANNEL_USERNAME=@dsgcomplex
   ADMIN_IDS=125861752,1506368833
   DEBUG=False
   ```

**Стоимость:** $5/месяц

---

## 🔥 **БЫСТРЫЙ СТАРТ (РЕКОМЕНДУЕТСЯ)**

### Для тестирования:
```bash
cd /Users/eldar/PycharmProjects/tgdsg
./start.sh
```

### Для продакшн (Heroku):
```bash
brew install heroku
heroku login
cd /Users/eldar/PycharmProjects/tgdsg
heroku create your-bot-name
heroku config:set BOT_TOKEN=7094351521:AAGGGNoq_4F1jjmMmJjMaMHp5jWFcuYQVkY
heroku config:set CHANNEL_USERNAME=@dsgcomplex
heroku config:set ADMIN_IDS=125861752,1506368833
git init
git add .
git commit -m "Deploy"
git push heroku main
heroku ps:scale worker=1
```

---

## 🔧 **ПРОБЛЕМЫ И РЕШЕНИЯ**

### Бот не отвечает:
```bash
# Проверка токена
curl "https://api.telegram.org/bot7094351521:AAGGGNoq_4F1jjmMmJjMaMHp5jWFcuYQVkY/getMe"

# Перезапуск
./start.sh  # Локально
heroku restart  # Heroku
systemctl restart tgdsg-bot  # VPS
```

### Ошибки с базой данных:
```bash
cd .venv
rm promocodes.db  # Удалить базу
python test_bot.py  # Пересоздать
```

### Проблемы с зависимостями:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 📊 **СРАВНЕНИЕ ПЛАТФОРМ**

| Платформа | Стоимость | Сложность | Надежность | Рекомендация |
|-----------|-----------|-----------|------------|--------------|
| **Локально** | Бесплатно | ⭐ | ⭐⭐ | Только для тестов |
| **VPS** | $3-5/мес | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ Лучший для продакшн |
| **Heroku** | $7/мес | ⭐⭐ | ⭐⭐⭐⭐ | ✅ Простота деплоя |
| **Railway** | $5/мес | ⭐ | ⭐⭐⭐⭐ | ✅ Современный UI |

---

## 🎯 **СЛЕДУЮЩИЕ ШАГИ**

1. **Выберите платформу** из списка выше
2. **Следуйте инструкциям** для выбранной платформы
3. **Протестируйте бота:** https://t.me/dsgspb_bot
4. **Добавьте бота в канал @dsgcomplex** с правами администратора
5. **Мониторьте логи** и статистику

---

## 🆘 **ПОДДЕРЖКА**

При возникновении проблем:
1. Проверьте логи платформы
2. Убедитесь в корректности токена
3. Проверьте права бота в канале
4. Используйте `./start.sh` для локального тестирования

**Ваш бот готов к деплою! 🚀** 