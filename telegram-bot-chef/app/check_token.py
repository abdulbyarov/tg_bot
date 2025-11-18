import asyncio
import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def check_bot():
    try:
        print(" Проверка конфигурации...")
        
        
        from config import config
        print(f" Токен бота: {config.BOT_TOKEN}")
        print(f" Длина токена: {len(config.BOT_TOKEN)}")
        print(f"  Database URL: {config.DATABASE_URL}")
        
        print("\n Проверка подключения к боту...")
        
        
        from bot import bot
        bot_info = await bot.get_me()
        print(f"✅ Бот работает: {bot_info.first_name} (@{bot_info.username})")
        print(f" ID бота: {bot_info.id}")
        
        print("\n Все проверки пройдены успешно!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Проверьте структуру файлов в папке app")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    print(" Запуск проверки бота...")
    result = asyncio.run(check_bot())
    
    if result:
        print("\n✅ Токен корректен! Проблема в другом.")
        print(" Проверьте логи основного приложения когда отправляете /start")
    else:
        print("\n Возможно, проблема с токеном. Проверьте его в @BotFather")
    
    input("\nНажмите Enter для выхода...")