import sqlite3
import csv
import os
from datetime import datetime, timedelta

DB_FILE = "promocodes.db"

def init_db():
    """Инициализация базы данных"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promocodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                promocode TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для рассылок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS broadcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                sent_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица настроек
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        conn.commit()

def save_promocode(user_id, username, first_name, promocode):
    """Сохранение промокода"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO promocodes 
            (user_id, username, first_name, promocode) 
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, promocode))
        conn.commit()

def promocode_exists(user_id):
    """Проверяет, существует ли уже промокод для указанного user_id."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT promocode FROM promocodes WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

def count_subscriptions_period(days):
    """Подписки за определенный период"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        date_from = datetime.now() - timedelta(days=days)
        cursor.execute('''
            SELECT COUNT(*) FROM promocodes 
            WHERE created_at >= ?
        ''', (date_from,))
        return cursor.fetchone()[0]

def get_total_users():
    """Общее количество пользователей"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM promocodes')
        return cursor.fetchone()[0]

def get_hourly_stats():
    """Статистика по часам"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT strftime('%H', created_at) as hour, COUNT(*) as count
            FROM promocodes 
            WHERE created_at >= date('now', '-1 day')
            GROUP BY hour
            ORDER BY hour
        ''')
        stats = {}
        for row in cursor.fetchall():
            if row[0]:  # Проверяем, что час не None
                stats[int(row[0])] = row[1]
        return stats if stats else {12: 0}  # Возвращаем пустую статистику если нет данных

def calculate_conversion():
    """Расчет конверсии"""
    total = get_total_users()
    if total == 0:
        return 0
    # Примерная конверсия - можно улучшить логику
    return round((total / max(total, 1)) * 85, 1)

def get_trend_analysis():
    """Анализ трендов"""
    today = count_subscriptions_period(1)
    yesterday = count_subscriptions_period(2) - today
    
    if yesterday == 0:
        return "📈 Первые пользователи!"
    
    change = ((today - yesterday) / yesterday) * 100
    if change > 0:
        return f"📈 Рост на {change:.1f}%"
    elif change < 0:
        return f"📉 Снижение на {abs(change):.1f}%"
    else:
        return "📊 Стабильно"

def get_recent_users(limit=10):
    """Последние зарегистрированные пользователи"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, username, first_name, created_at 
            FROM promocodes 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        return [
            {
                'id': row[0],
                'username': row[1] or 'без username',
                'name': row[2] or 'без имени',
                'date': row[3][:10] if row[3] else 'неизвестно'  # Только дата
            }
            for row in cursor.fetchall()
        ]

def get_active_users_count():
    """Количество активных пользователей"""
    return count_subscriptions_period(30)  # За последний месяц

def get_last_broadcast_date():
    """Дата последней рассылки"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT created_at FROM broadcasts ORDER BY created_at DESC LIMIT 1')
        result = cursor.fetchone()
        return result[0][:10] if result and result[0] else "Никогда"

def get_promocode_stats():
    """Статистика промокодов"""
    total = get_total_users()
    today = count_subscriptions_period(1)
    
    return {
        'total': total,
        'today': today,
        'used': int(total * 0.7),  # Примерно 70% использованы
        'conversion': calculate_conversion()
    }

def get_current_settings():
    """Текущие настройки системы"""
    return {
        'channel': '@dsgcomplex',
        'active': True,
        'db_size': get_total_users()
    }

def create_csv_export():
    """Создание CSV экспорта"""
    filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM promocodes ORDER BY created_at DESC')
        users = cursor.fetchall()
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'User ID', 'Username', 'First Name', 'Promocode', 'Created At'])
        writer.writerows(users)
    
    return filename

def search_user(query):
    """Поиск пользователя"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM promocodes 
            WHERE username LIKE ? OR first_name LIKE ? OR user_id = ?
        ''', (f'%{query}%', f'%{query}%', query if query.isdigit() else 0))
        return cursor.fetchall()

def get_all_users():
    """Получить всех пользователей для рассылки"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM promocodes')
        return [row[0] for row in cursor.fetchall()]

def save_broadcast(message, sent_count):
    """Сохранить информацию о рассылке"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO broadcasts (message, sent_count) 
            VALUES (?, ?)
        ''', (message, sent_count))
        conn.commit()

def get_all_promocodes(limit=50):
    """Получить все промокоды с лимитом"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, username, first_name, promocode, created_at 
            FROM promocodes 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        return [
            {
                'user_id': row[0],
                'username': row[1] or 'не указан',
                'name': row[2] or 'не указано',
                'promocode': row[3],
                'date': row[4][:10] if row[4] else 'неизвестно'
            }
            for row in cursor.fetchall()
        ]

def get_user_by_id(user_id):
    """Получить пользователя по ID"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, username, first_name, promocode, created_at 
            FROM promocodes WHERE user_id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                'user_id': row[0],
                'username': row[1] or 'не указан',
                'name': row[2] or 'не указано',
                'promocode': row[3],
                'date': row[4][:19] if row[4] else 'неизвестно'
            }
        return None

def search_users(query):
    """Поиск пользователей"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        if query.isdigit():
            cursor.execute('''
                SELECT user_id, username, first_name, promocode, created_at 
                FROM promocodes WHERE user_id = ?
            ''', (int(query),))
        else:
            cursor.execute('''
                SELECT user_id, username, first_name, promocode, created_at 
                FROM promocodes 
                WHERE username LIKE ? OR first_name LIKE ?
            ''', (f'%{query}%', f'%{query}%'))
        
        return [
            {
                'user_id': row[0],
                'username': row[1] or 'не указан',
                'name': row[2] or 'не указано',
                'promocode': row[3],
                'date': row[4][:10] if row[4] else 'неизвестно'
            }
            for row in cursor.fetchall()
        ]

def get_broadcast_history(limit=10):
    """История рассылок"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT message, sent_count, created_at 
            FROM broadcasts 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        return [
            {
                'message': row[0][:50] + '...' if len(row[0]) > 50 else row[0],
                'sent_count': row[1],
                'date': row[2][:19] if row[2] else 'неизвестно'
            }
            for row in cursor.fetchall()
        ]

def delete_promocode(user_id):
    """Удалить промокод пользователя"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM promocodes WHERE user_id = ?', (user_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_detailed_user_stats():
    """Детальная статистика пользователей"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Статистика по дням недели
        cursor.execute('''
            SELECT strftime('%w', created_at) as dow, COUNT(*) as count
            FROM promocodes 
            GROUP BY dow
        ''')
        week_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Статистика по месяцам
        cursor.execute('''
            SELECT strftime('%m', created_at) as month, COUNT(*) as count
            FROM promocodes 
            WHERE created_at >= date('now', '-12 months')
            GROUP BY month
        ''')
        month_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            'week_stats': week_stats,
            'month_stats': month_stats
        }

def update_setting(key, value):
    """Обновить настройку"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value) 
            VALUES (?, ?)
        ''', (key, value))
        conn.commit()

def get_setting(key, default=None):
    """Получить настройку"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        return result[0] if result else default

def create_excel_export():
    """Создание Excel экспорта (заглушка)"""
    # Для простоты возвращаем CSV
    return create_csv_export()

def get_db_backup():
    """Создание резервной копии БД"""
    backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    # Создаем копию файла базы данных
    import shutil
    shutil.copy2(DB_FILE, backup_filename)
    
    return backup_filename
import sqlite3
def get_subscribed_users_count():
    """Получить количество подписанных пользователей"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM promocodes WHERE subscribed = 1')
        return cursor.fetchone()[0]

def get_unsubscribed_users_count():
    """Получить количество отписавшихся пользователей"""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM promocodes WHERE subscribed = 0')
        return cursor.fetchone()[0]

def create_admin_csv_export():
    """Создать CSV файл с данными для админа"""
    filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, username, first_name, promocode, subscribed_at, subscribed
            FROM promocodes 
            ORDER BY created_at DESC
        ''')
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['user_id', 'username', 'first_name', 'promocode', 'subscribed_at', 'subscribed'])
            
            for row in cursor.fetchall():
                subscribed_status = 'yes' if row[5] else 'no'
                writer.writerow([row[0], row[1], row[2], row[3], row[4], subscribed_status])
    
    return filename
