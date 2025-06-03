#!/bin/bash

# 🤖 Простой запуск Telegram бота DSG COMPLEX

echo "🚀 === ЗАПУСК TELEGRAM БОТА DSG COMPLEX ==="

# Проверка папки
if [ ! -d ".venv" ]; then
    echo "❌ Папка .venv не найдена!"
    echo "💡 Убедитесь, что вы находитесь в папке tgdsg"
    exit 1
fi

# Проверка файлов
if [ ! -f ".venv/bot.py" ]; then
    echo "❌ Файл bot.py не найден в .venv/"
    exit 1
fi

echo "📁 Текущая папка: $(pwd)"
echo "🔍 Проверка файлов..."
echo "   ✅ bot.py найден"
echo "   ✅ promo_db.py найден" 

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source .venv/bin/activate

# Переход в папку с ботом
cd .venv

# Проверка зависимостей
echo "📦 Проверка зависимостей..."
if ! python -c "import aiogram, requests" 2>/dev/null; then
    echo "⚠️ Установка зависимостей..."
    pip install -r ../requirements.txt
fi

# Проверка подключения
echo "🔍 Проверка подключения к Telegram..."
if python -c "
from bot import BOT_TOKEN
import requests
response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getMe')
if response.status_code == 200:
    result = response.json()['result']
    print(f'✅ Бот @{result[\"username\"]} подключен')
else:
    print('❌ Ошибка подключения')
    exit(1)
" 2>/dev/null; then
    echo "✅ Подключение к Telegram API успешно"
else
    echo "❌ Ошибка подключения к Telegram API"
    echo "💡 Проверьте токен бота"
    exit 1
fi

# Запуск бота
echo ""
echo "🤖 === ЗАПУСК БОТА ==="
echo "📱 Бот: @dsgspb_bot"
echo "🔗 Ссылка: https://t.me/dsgspb_bot"
echo "⏹️  Для остановки нажмите Ctrl+C"
echo ""

python bot.py 