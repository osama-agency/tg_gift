import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import CommandStart
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

from promo_db import (init_db, save_promocode, promocode_exists, 
                     count_subscriptions_period, get_total_users, get_hourly_stats, 
                     calculate_conversion, get_trend_analysis, get_recent_users, 
                     get_active_users_count, get_last_broadcast_date, 
                     get_promocode_stats, get_current_settings, create_csv_export,
                     get_subscribed_users_count, get_unsubscribed_users_count, 
                     get_user_by_id, create_admin_csv_export)

# Состояния для FSM
class BroadcastState(StatesGroup):
    waiting_message = State()

class UserSearchState(StatesGroup):
    waiting_user_id = State()

# Загрузка переменных среды
load_dotenv()
BOT_TOKEN = "7094351521:AAGGGNoq_4F1jjmMmJjMaMHp5jWFcuYQVkY"
CHANNEL_USERNAME = "@dsgcomplex"

# Проверка на наличие токена
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден. Укажите его в .env или прямо в коде.")

# Инициализация бота и диспетчера
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
logging.basicConfig(level=logging.INFO)

# Инициализация базы данных
init_db()
ADMINS = [125861752, 1506368833]

# Вспомогательные функции для клавиатур
def get_main_keyboard(is_admin=False):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔗 Подписаться", url="https://t.me/dsgcomplex"))
    keyboard.add(InlineKeyboardButton("🎁 Получить промокод", callback_data="get_promocode"))
    
    if is_admin:
        keyboard.add(InlineKeyboardButton("🔧 Админ-панель", callback_data="admin_panel"))
    
    return keyboard

def get_admin_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")
    )
    keyboard.add(
        InlineKeyboardButton("📨 Рассылка", callback_data="admin_broadcast"),
        InlineKeyboardButton("🎁 Промокоды", callback_data="admin_promocodes")
    )
    keyboard.add(
        InlineKeyboardButton("⚙️ Настройки", callback_data="admin_settings"),
        InlineKeyboardButton("📥 Экспорт", callback_data="admin_export")
    )
    keyboard.add(InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
    
    return keyboard

def get_back_keyboard(back_to="admin_panel"):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data=back_to))
    return keyboard

# Обработчик команды /start
@dp.message_handler(CommandStart())
async def start(message: types.Message):
    is_admin = message.from_user.id in ADMINS
    keyboard = get_main_keyboard(is_admin)

    # Отправляем картинку с приветствием
    try:
        with open("welcome_image.png", "rb") as photo:
            await message.answer_photo(
                photo,
                caption="🔥 <b>Добро пожаловать в DSG COMPLEX!</b>\n\n"
                        "🎁 Получите эксклюзивный промокод за подписку на наш канал!\n\n"
                        "👇 Нажмите, чтобы подписаться и получить промокод:",
                reply_markup=keyboard
            )
    except Exception as e:
        # Если картинка не найдена, отправляем обычное сообщение
        logging.error(f"Ошибка отправки картинки: {e}")
        await message.answer(
            "🔥 <b>Добро пожаловать в DSG COMPLEX!</b>\n\n"
            "🎁 Получите эксклюзивный промокод за подписку на наш канал!\n\n"
            "👇 Нажмите, чтобы подписаться и получить промокод:",
            reply_markup=keyboard
        ) @dp.message_handler(commands=['admin'])
async def admin_command(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("🚫 У вас нет прав доступа.")
        return
    
    # Получение статистики
    total_users = get_subscribed_users_count()
    new_24h = count_subscriptions_period(1)
    new_7d = count_subscriptions_period(7)
    unsubscribed = get_unsubscribed_users_count()
    
    stats_text = f"""📊 <b>Статистика бота</b>

👥 <b>Пользователи:</b>
• Всего с промокодами: {total_users}
• Новых за 24ч: {new_24h}
• Новых за 7 дней: {new_7d}
• Отписались: {unsubscribed}

⏰ Обновлено: только что"""
    
    keyboard = get_admin_main_keyboard()
    await message.answer(stats_text, reply_markup=keyboard)

@dp.message_handler(commands=['export'])
async def export_command(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("🚫 У вас нет прав доступа.")
        return
    
    try:
        csv_file = create_admin_csv_export()
        
        with open(csv_file, 'rb') as file:
            await message.answer_document(
                file,
                caption="📄 <b>Экспорт всех пользователей</b>\n\nФормат: user_id, username, first_name, promocode, subscribed_at, subscribed"
            )
        
        os.remove(csv_file)
        
    except Exception as e:
        logging.error(f"Ошибка экспорта: {e}")
        await message.answer("❌ Ошибка при создании файла экспорта.")

@dp.message_handler(commands=['check'])
async def check_user_command(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.answer("🚫 У вас нет прав доступа.")
        return
    
    # Извлекаем user_id из команды
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Укажите ID пользователя.\n\nПример: <code>/check 123456789</code>")
        return
    
    try:
        user_id = int(parts[1])
        user_data = get_user_by_id(user_id)
        
        if not user_data:
            await message.answer(f"❌ Пользователь с ID {user_id} не найден в базе данных.")
            return
        
        # Форматируем информацию о пользователе
        username = f"@{user_data['username']}" if user_data['username'] else "Не указан"
        subscribed_at = user_data['subscribed_at'] or "Не указано"
        subscribed_status = "✅ Да" if user_data['subscribed'] else "❌ Нет"
        
        user_info = f"""👤 <b>Информация о пользователе</b>

🆔 <b>ID:</b> <code>{user_data['user_id']}</code>
👤 <b>Имя:</b> {user_data['first_name']}
📝 <b>Username:</b> {username}
🎁 <b>Промокод:</b> <code>{user_data['promocode']}</code>
📅 <b>Дата подписки:</b> {subscribed_at}
✅ <b>Подписан:</b> {subscribed_status}"""
        
        await message.answer(user_info)
        
    except ValueError:
        await message.answer("❌ ID пользователя должен быть числом.")
    except Exception as e:
        logging.error(f"Ошибка проверки пользователя: {e}")
        await message.answer("❌ Ошибка при получении данных пользователя.")

# Обработчик получения промокода
@dp.callback_query_handler(lambda c: c.data == "get_promocode")
async def process_promocode(callback_query: types.CallbackQuery):
    await callback_query.answer()

    user = callback_query.from_user
    user_id = user.id

    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
    except Exception as e:
        logging.error(f"Ошибка проверки подписки для {user_id}: {e}")
        await callback_query.message.answer("❌ Не удалось проверить подписку. Попробуйте позже.")
        return

    if member.status not in ['member', 'creator', 'administrator']:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("🔗 Подписаться", url="https://t.me/dsgcomplex"))
        keyboard.add(InlineKeyboardButton("🔄 Проверить подписку", callback_data="get_promocode"))
        keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="main_menu"))
        
        await callback_query.message.edit_text(
            "❌ <b>Вы не подписались на канал!</b>\n\n"
            "🔗 Подпишитесь на канал <b>DSG COMPLEX</b> и получите эксклюзивный промокод!\n\n"
            "После подписки нажмите «Проверить подписку».",
            reply_markup=keyboard
        )
        return

    # Проверка, был ли уже выдан промокод
    existing_code = promocode_exists(user_id)
    if existing_code:
        promo = existing_code
    else:
        promo = f"DSG{user_id}"
        save_promocode(user_id, user.username or "", user.first_name or "", promo)

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
    
    await callback_query.message.edit_text(
        f"🎉 <b>Поздравляем!</b>\n\n"
        f"✅ Ваш промокод: <code>{promo}</code>\n\n"
        f"💰 Используйте его для получения скидки!",
        reply_markup=keyboard
    )

# Главное меню
# Главное меню
@dp.callback_query_handler(lambda c: c.data == "main_menu")
async def main_menu(callback_query: types.CallbackQuery):
    is_admin = callback_query.from_user.id in ADMINS
    keyboard = get_main_keyboard(is_admin)
    
    # Отправляем картинку с приветствием  
    try:
        with open("welcome_image.png", "rb") as photo:
            await callback_query.message.answer_photo(
                photo,
                caption="🔥 <b>Добро пожаловать в DSG COMPLEX!</b>\n\n"
                        "🎁 Получите эксклюзивный промокод за подписку на наш канал!\n\n"
                        "👇 Нажмите, чтобы подписаться и получить промокод:",
                reply_markup=keyboard
            )
        # Удаляем предыдущее сообщение
        await callback_query.message.delete()
    except Exception as e:
        # Если картинка не найдена или ошибка, используем edit_text
        logging.error(f"Ошибка отправки картинки в main_menu: {e}")
        await callback_query.message.edit_text(
            "🔥 <b>Добро пожаловать в DSG COMPLEX!</b>\n\n"
            "🎁 Получите эксклюзивный промокод за подписку на наш канал!\n\n"
            "👇 Нажмите, чтобы подписаться и получить промокод:",
            reply_markup=keyboard
        )
    
    await callback_query.answer() 
# Админ панель
@dp.callback_query_handler(lambda c: c.data == "admin_panel")
async def admin_panel(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        await callback_query.answer("🚫 Нет доступа", show_alert=True)
        return
    
    keyboard = get_admin_main_keyboard()
    
    # Проверяем, есть ли текст в сообщении (может быть фото)
    try:
        await callback_query.message.edit_text(
            "🔧 <b>Панель администратора</b>\n\n"
            "Выберите нужный раздел для управления ботом:",
            reply_markup=keyboard
        )
    except Exception:
        # Если не удается отредактировать (например, сообщение с фото), отправляем новое
        await callback_query.message.answer(
            "🔧 <b>Панель администратора</b>\n\n"
            "Выберите нужный раздел для управления ботом:",
            reply_markup=keyboard
        )
    
    await callback_query.answer()

# Статистика админ
@dp.callback_query_handler(lambda c: c.data == "admin_stats")
async def admin_stats(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        return
    
    # Получение статистики
    total_users = get_subscribed_users_count()
    new_24h = count_subscriptions_period(1)
    new_7d = count_subscriptions_period(7)
    unsubscribed = get_unsubscribed_users_count()
    
    # Дополнительная статистика
    today_count = count_subscriptions_period(1)
    week_count = count_subscriptions_period(7)
    month_count = count_subscriptions_period(30)
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("📈 Подробно", callback_data="admin_stats_detailed"),
        InlineKeyboardButton("📊 График", callback_data="admin_stats_chart")
    )
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="admin_panel"))
    
    stats_text = f"""📊 <b>Статистика бота</b>

👥 <b>Пользователи:</b>
• Всего с промокодами: {total_users}
• Новых за 24ч: {new_24h}
• Новых за 7 дней: {new_7d}
• Отписались: {unsubscribed}

📈 <b>По периодам:</b>
• Сегодня: {today_count}
• За неделю: {week_count}
• За месяц: {month_count}

💹 <b>Конверсия:</b> {calculate_conversion()}%

⏰ Обновлено: только что"""
    
    await callback_query.message.edit_text(stats_text, reply_markup=keyboard)
    await callback_query.answer()

# Управление пользователями
@dp.callback_query_handler(lambda c: c.data == "admin_users")
async def admin_users(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        return
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("🔍 Поиск пользователя", callback_data="admin_search_user"),
        InlineKeyboardButton("📋 Последние", callback_data="admin_recent_users")
    )
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="admin_panel"))
    
    recent_users = get_recent_users(5)
    if recent_users:
        users_text = "\n".join([f"• {u['name']} (@{u['username'] or 'нет'}) - {u['date']}" for u in recent_users])
    else:
        users_text = "Нет данных"
    
    await callback_query.message.edit_text(
        f"👥 <b>Управление пользователями</b>\n\n"
        f"🆕 <b>Последние регистрации:</b>\n{users_text}",
        reply_markup=keyboard
    )
    await callback_query.answer()

# Поиск пользователя
@dp.callback_query_handler(lambda c: c.data == "admin_search_user")
async def admin_search_user(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.from_user.id not in ADMINS:
        return
    
    keyboard = get_back_keyboard("admin_users")
    
    await callback_query.message.edit_text(
        "🔍 <b>Поиск пользователя</b>\n\n"
        "Отправьте ID пользователя для поиска:",
        reply_markup=keyboard
    )
    
    await UserSearchState.waiting_user_id.set()
    await callback_query.answer()

@dp.message_handler(state=UserSearchState.waiting_user_id)
async def process_user_search(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        return
    
    try:
        user_id = int(message.text.strip())
        user_data = get_user_by_id(user_id)
        
        if not user_data:
            await message.answer(f"❌ Пользователь с ID {user_id} не найден.")
            return
        
        username = f"@{user_data['username']}" if user_data['username'] else "Не указан"
        subscribed_at = user_data['subscribed_at'] or "Не указано"
        subscribed_status = "✅ Да" if user_data['subscribed'] else "❌ Нет"
        
        user_info = f"""👤 <b>Найден пользователь</b>

🆔 <b>ID:</b> <code>{user_data['user_id']}</code>
👤 <b>Имя:</b> {user_data['first_name']}
📝 <b>Username:</b> {username}
🎁 <b>Промокод:</b> <code>{user_data['promocode']}</code>
📅 <b>Дата подписки:</b> {subscribed_at}
✅ <b>Подписан:</b> {subscribed_status}"""
        
        keyboard = get_back_keyboard("admin_users")
        await message.answer(user_info, reply_markup=keyboard)
        
    except ValueError:
        await message.answer("❌ ID должен быть числом.")
    except Exception as e:
        logging.error(f"Ошибка поиска пользователя: {e}")
        await message.answer("❌ Ошибка при поиске.")
    
    await state.finish()

# Экспорт данных
@dp.callback_query_handler(lambda c: c.data == "admin_export")
async def admin_export(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        return
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("📄 Скачать CSV", callback_data="export_csv"),
        InlineKeyboardButton("📊 Отчет", callback_data="export_report")
    )
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="admin_panel"))
    
    await callback_query.message.edit_text(
        "📥 <b>Экспорт данных</b>\n\n"
        "Выберите формат для экспорта данных о пользователях:\n\n"
        "📄 <b>CSV</b> - все данные пользователей\n"
        "📊 <b>Отчет</b> - сводная статистика",
        reply_markup=keyboard
    )
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "export_csv")
async def export_csv(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        return
    
    try:
        await callback_query.answer("⏳ Создание файла...")
        
        csv_file = create_admin_csv_export()
        
        with open(csv_file, 'rb') as file:
            await bot.send_document(
                callback_query.from_user.id,
                file,
                caption="📄 <b>Экспорт пользователей</b>\n\nФормат: user_id, username, first_name, promocode, subscribed_at, subscribed"
            )
        
        os.remove(csv_file)
        await callback_query.message.answer("✅ Файл отправлен!")
        
    except Exception as e:
        logging.error(f"Ошибка экспорта CSV: {e}")
        await callback_query.answer("❌ Ошибка при создании файла", show_alert=True)

# Заглушки для других функций
@dp.callback_query_handler(lambda c: c.data in ["admin_broadcast", "admin_promocodes", "admin_settings", "export_report", "admin_stats_detailed", "admin_stats_chart", "admin_recent_users"])
async def admin_placeholder(callback_query: types.CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        return
    
    functions_names = {
        "admin_broadcast": "📨 Рассылка",
        "admin_promocodes": "🎁 Управление промокодами", 
        "admin_settings": "⚙️ Настройки",
        "export_report": "📊 Отчет",
        "admin_stats_detailed": "📈 Подробная статистика",
        "admin_stats_chart": "📊 График статистики",
        "admin_recent_users": "📋 Список пользователей"
    }
    
    function_name = functions_names.get(callback_query.data, "Функция")
    
    await callback_query.answer(f"🚧 {function_name} - в разработке", show_alert=True)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True) 