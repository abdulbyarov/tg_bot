from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from bot import bot, dp
from database import get_db, init_db
from models import User, Recipe
from config import config
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    print("🔄 Инициализация базы данных...")
    await init_db()
    print("✅ База данных готова!")
    
    print(" Запуск Telegram бота...")
    asyncio.create_task(start_bot())
    print("✅ Бот запущен!")
    
    yield  # Здесь приложение работает
    
    
    print("🛑 Остановка приложения...")

app = FastAPI(title="Chef Bot API", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Chef Bot API is running"}

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        "SELECT * FROM users WHERE telegram_id = :user_id", 
        {"user_id": user_id}
    )
    user = result.first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user)

@app.get("/users/{user_id}/recipes")
async def get_user_recipes(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        "SELECT * FROM recipes WHERE user_id = :user_id ORDER BY created_at DESC",
        {"user_id": user_id}
    )
    recipes = result.fetchall()
    return [dict(recipe) for recipe in recipes]

async def start_bot():
    print(" Бот запускается...")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )