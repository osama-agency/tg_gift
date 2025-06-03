#!/bin/bash

# 🚀 Скрипт деплоя Telegram бота DSG COMPLEX на VPS

echo "🚀 === ДЕПЛОЙ TELEGRAM БОТА DSG COMPLEX ==="

# Настройки сервера (ИЗМЕНИТЕ НА СВОИ)
SERVER_IP="your-server-ip"
SERVER_USER="root"
SERVER_PATH="/opt/tgdsg-bot"
BOT_SERVICE="tgdsg-bot"

echo "📋 Настройки деплоя:"
echo "🖥️  Сервер: $SERVER_USER@$SERVER_IP"
echo "📁 Путь: $SERVER_PATH"
echo "🔧 Сервис: $BOT_SERVICE"
echo ""

# Проверка SSH подключения
echo "🔍 Проверка подключения к серверу..."
if ! ssh -o ConnectTimeout=5 $SERVER_USER@$SERVER_IP "echo 'Подключение успешно'"; then
    echo "❌ Не удается подключиться к серверу $SERVER_IP"
    echo "💡 Проверьте:"
    echo "   • IP адрес сервера"
    echo "   • SSH ключи"
    echo "   • Настройки фаервола"
    exit 1
fi

# Создание архива
echo "📦 Создание архива проекта..."
tar -czf tgdsg-bot.tar.gz \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='promocodes.db' \
    .venv/bot.py \
    .venv/promo_db.py \
    requirements.txt \
    README.md

echo "✅ Архив создан: tgdsg-bot.tar.gz"

# Загрузка на сервер
echo "⬆️ Загрузка на сервер..."
scp tgdsg-bot.tar.gz $SERVER_USER@$SERVER_IP:/tmp/

# Установка на сервере
echo "🔧 Установка на сервере..."
ssh $SERVER_USER@$SERVER_IP << 'EOF'
    # Остановка старого сервиса
    systemctl stop tgdsg-bot || true
    
    # Создание директории
    mkdir -p /opt/tgdsg-bot
    cd /opt/tgdsg-bot
    
    # Распаковка
    tar -xzf /tmp/tgdsg-bot.tar.gz
    
    # Установка Python и зависимостей
    apt update
    apt install -y python3 python3-pip python3-venv
    
    # Создание виртуального окружения
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Создание .env файла
    cat > .env << 'ENV_EOF'
BOT_TOKEN=7094351521:AAGGGNoq_4F1jjmMmJjMaMHp5jWFcuYQVkY
CHANNEL_USERNAME=@dsgcomplex
ADMIN_IDS=125861752,1506368833
DEBUG=False
ENV_EOF
    
    # Создание systemd сервиса
    cat > /etc/systemd/system/tgdsg-bot.service << 'SERVICE_EOF'
[Unit]
Description=Telegram Bot DSG COMPLEX
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/tgdsg-bot
Environment=PATH=/opt/tgdsg-bot/venv/bin
ExecStart=/opt/tgdsg-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_EOF
    
    # Запуск сервиса
    systemctl daemon-reload
    systemctl enable tgdsg-bot
    systemctl start tgdsg-bot
    
    echo "✅ Бот установлен и запущен как сервис!"
EOF

# Проверка статуса
echo "🔍 Проверка статуса бота на сервере..."
ssh $SERVER_USER@$SERVER_IP "systemctl status tgdsg-bot --no-pager"

# Очистка
rm tgdsg-bot.tar.gz

echo ""
echo "🎉 === ДЕПЛОЙ ЗАВЕРШЕН ==="
echo "🔧 Управление ботом:"
echo "   • Статус:    ssh $SERVER_USER@$SERVER_IP 'systemctl status tgdsg-bot'"
echo "   • Логи:      ssh $SERVER_USER@$SERVER_IP 'journalctl -f -u tgdsg-bot'"
echo "   • Перезапуск: ssh $SERVER_USER@$SERVER_IP 'systemctl restart tgdsg-bot'"
echo "   • Остановка: ssh $SERVER_USER@$SERVER_IP 'systemctl stop tgdsg-bot'"
echo ""
echo "🤖 Ваш бот теперь работает на сервере!"
echo "📱 Проверьте: https://t.me/dsgspb_bot" 