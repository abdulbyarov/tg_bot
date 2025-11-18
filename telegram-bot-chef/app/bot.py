import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import text

from models import User, FridgeItem, Recipe

from config import config
from agent import chef_agent
from database import get_db, init_db


bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Клавиатуры
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍴 Создать рецепт"), KeyboardButton(text="🥕 Мой холодильник")],
        [KeyboardButton(text="📖 Мои рецепты")]  
    ],
    resize_keyboard=True
)

fridge_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить продукт"), KeyboardButton(text="📋 Список продуктов")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)

class FridgeState(StatesGroup):
    waiting_for_ingredient = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    print(f"🔔 Получена команда /start от пользователя {message.from_user.id}")
    
    async for session in get_db():
        # Регистрируем пользователя
        result = await session.execute(
            text("SELECT * FROM users WHERE telegram_id = :user_id"),
            {"user_id": message.from_user.id}
        )
        user = result.first()
        
        if not user:
            print(f"👤 Создаем нового пользователя: {message.from_user.id}")
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            session.add(user)
            await session.commit()
            print(f"✅ Пользователь создан: {message.from_user.id}")
        else:
            print(f"✅ Пользователь уже существует: {message.from_user.id}")
    
    welcome_text = """
👨‍🍳 Привет! Я твой личный шеф-повар!

Я могу:
• Создать рецепт из того, что есть в холодильнике
• Учитывать твои диетические предпочтения
• Сохранять твои любимые рецепты

Выбери действие ниже!
"""
    print(f"📤 Отправляю приветствие пользователю {message.from_user.id}")
    await message.answer(welcome_text, reply_markup=main_keyboard)

@dp.message(F.text == "🍴 Создать рецепт")
async def create_recipe(message: types.Message):
    """Создание рецепта"""
    print(f"🔔 Пользователь {message.from_user.id} запросил создание рецепта")
    async for session in get_db():
        try:
            response = await chef_agent.process_user_request(
                session, 
                message.from_user.id, 
                "создай рецепт"
            )
            await message.answer(response, reply_markup=main_keyboard, parse_mode="Markdown")
        except Exception as e:
            print(f"❌ Ошибка при создании рецепта: {e}")
            await message.answer("😔 Произошла ошибка при создании рецепта. Попробуйте снова.", reply_markup=main_keyboard)

@dp.message(F.text == "🥕 Мой холодильник")
async def my_fridge(message: types.Message):
    print(f"🔔 Пользователь {message.from_user.id} открыл холодильник")
    await message.answer(
        "Управляй содержимым своего холодильника:",
        reply_markup=fridge_keyboard
    )

@dp.message(F.text == "📋 Список продуктов")
async def list_fridge_items(message: types.Message):
    print(f"🔔 Пользователь {message.from_user.id} запросил список продуктов")
    async for session in get_db():
        try:
            items = await chef_agent.analyze_fridge(session, message.from_user.id)
            
            if items:
                response = "🥕 В вашем холодильнике:\n" + "\n".join(f"• {item}" for item in items)
            else:
                response = "😔 Холодильник пуст. Добавьте продукты!"
            
            await message.answer(response, reply_markup=fridge_keyboard)
        except Exception as e:
            print(f"❌ Ошибка при получении списка продуктов: {e}")
            await message.answer("😔 Произошла ошибка при загрузке списка продуктов.", reply_markup=fridge_keyboard)

@dp.message(F.text == "➕ Добавить продукт")
async def add_ingredient_start(message: types.Message, state: FSMContext):
    print(f"🔔 Пользователь {message.from_user.id} добавляет продукт")
    await message.answer(
        "Напишите продукт в формате: 'Название количество'\n\n"
        "Например:\n"
        "• помидоры 3 шт\n"
        "• куриное филе 400г\n"
        "• яйца 5 шт",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(FridgeState.waiting_for_ingredient)

@dp.message(FridgeState.waiting_for_ingredient)
async def add_ingredient_finish(message: types.Message, state: FSMContext):
    print(f"🔔 Пользователь {message.from_user.id} добавил продукт: {message.text}")
    
    if not message.text or len(message.text.strip()) == 0:
        await message.answer("❌ Пожалуйста, введите название продукта.", reply_markup=fridge_keyboard)
        await state.clear()
        return
    
    async for session in get_db():
        try:
            # Простая обработка ввода
            ingredient_text = message.text.strip()
            
            fridge_item = FridgeItem(
                user_id=message.from_user.id,
                ingredient_name=ingredient_text,
                quantity="",
                category="другое"
            )
            session.add(fridge_item)
            await session.commit()
            
            await message.answer(
                f"✅ Добавлено: {ingredient_text}",
                reply_markup=fridge_keyboard
            )
            print(f"✅ Продукт добавлен в БД: {ingredient_text}")
            
        except Exception as e:
            print(f"❌ Ошибка при добавлении продукта: {e}")
            await message.answer(
                "❌ Произошла ошибка при добавлении продукта. Попробуйте снова.",
                reply_markup=fridge_keyboard
            )
    
    await state.clear()

@dp.message(F.text == "🔙 Назад")
async def back_to_main(message: types.Message):
    print(f"🔔 Пользователь {message.from_user.id} вернулся в главное меню")
    await message.answer("Главное меню:", reply_markup=main_keyboard)

@dp.message(F.text == "📖 Мои рецепты")
async def my_recipes(message: types.Message):
    print(f"🔔 Пользователь {message.from_user.id} запросил свои рецепты")
    async for session in get_db():
        try:
            result = await session.execute(
                text("SELECT * FROM recipes WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 5"),
                {"user_id": message.from_user.id}
            )
            recipes = result.fetchall()
            
            if recipes:
                response = "📖 Ваши последние рецепты:\n\n"
                for recipe in recipes:
                    response += f"• {recipe.title} (#{recipe.id})\n"
            else:
                response = "📝 У вас пока нет сохраненных рецептов. Создайте первый через меню '🍴 Создать рецепт'!"
            
            await message.answer(response, reply_markup=main_keyboard)
        except Exception as e:
            print(f"❌ Ошибка при получении рецептов: {e}")
            await message.answer("😔 Произошла ошибка при загрузке рецептов.", reply_markup=main_keyboard)

#пока нет
@dp.message(F.text == "👤 Мой профиль")
async def my_profile(message: types.Message):
    print(f"🔔 Пользователь {message.from_user.id} запросил профиль")
    
    async for session in get_db():
        try:
            result = await session.execute(
                text("SELECT * FROM users WHERE telegram_id = :user_id"),
                {"user_id": message.from_user.id}
            )
            user = result.first()
            
            if user:
                response = f"👤 *Ваш профиль:*\n\n"
                response += f"🆔 ID: {user.telegram_id}\n"
                response += f"👤 Имя: {user.first_name or 'Не указано'}\n"
                response += f"📛 Фамилия: {user.last_name or 'Не указана'}\n"
                response += f"📱 Username: @{user.username or 'Не указан'}\n"
                response += f"🍽️ Предпочтения: {', '.join(user.dietary_preferences) if user.dietary_preferences else 'Не указаны'}\n"
                response += f"🚫 Аллергии: {', '.join(user.allergies) if user.allergies else 'Нет'}\n"
                response += f"👨‍🍳 Уровень: {user.cooking_skill}\n"
                response += f"📅 Зарегистрирован: {user.created_at.strftime('%d.%m.%Y') if user.created_at else 'Неизвестно'}\n\n"
                response += "⚙️ *Настройки профиля скоро будут доступны*"
            else:
                response = "❌ Профиль не найден. Отправьте /start"
            
            await message.answer(response, reply_markup=main_keyboard, parse_mode="Markdown")
            
        except Exception as e:
            print(f"❌ Ошибка при получении профиля: {e}")
            await message.answer("😔 Произошла ошибка при загрузке профиля.", reply_markup=main_keyboard)

# Обработчик для всех остальных сообщений
@dp.message()
async def handle_other_messages(message: types.Message):
    
    print(f"🔔 Получено сообщение от {message.from_user.id}: '{message.text}'")
    
    # Игнорируем команды, которые уже обрабатываются
    if message.text in ["🍴 Создать рецепт", "🥕 Мой холодильник", "📖 Мои рецепты", "🔙 Назад", "➕ Добавить продукт", "📋 Список продуктов"]:
        return
    
    # Отвечаем на произвольные сообщения
    await message.answer(
        "🤖 Я ваш шеф-помощник! Используйте кнопки ниже для навигации:\n\n"
        "• 🍴 Создать рецепт - создать рецепт из продуктов в холодильнике\n"
        "• 🥕 Мой холодильник - управление продуктами\n"
        "• 📖 Мои рецепты - просмотр сохраненных рецептов",
        reply_markup=main_keyboard
    )

async def start_bot():
    print("Бот запускается...")
    try:
        # Отключаем вебхук на всякий случай
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Вебхук отключен")
        
        # Выводим отладочную информацию
        bot_info = await bot.get_me()
        print(f"✅ Бот авторизован: {bot_info.first_name} (@{bot_info.username})")
        
        print("🔄 Начинаем обработку сообщений...")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")