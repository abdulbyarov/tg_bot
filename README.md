# tg_bot
Я разработал интеллектуального Telegram-бота "Шеф-помощник", который создает персонализированные рецепты на основе продуктов, имеющихся у пользователя в холодильнике. Бот сочетает в себе современные технологии искусственного интеллекта и классические подходы к разработке программного обеспечения.
Telegram-бот "Шеф-помощник": Разработка кулинарного ассистента
 
 О проекте
Технологический стек
Python-библиотеки и фреймворки
Основные зависимости:
•	aiogram - современный асинхронный фреймворк для Telegram Bot API
•	fastapi - высокопроизводительный веб-фреймворк для создания API
•	uvicorn - ASGI-сервер для запуска FastAPI приложений
Работа с данными:
•	sqlalchemy - ORM для работы с базой данных
•	alembic - инструмент для миграций базы данных
•	asyncpg - асинхронный драйвер для PostgreSQL
Интеграция с AI:
•	gigachat - официальная библиотека для работы с GigaChat API от Сбера
•	aiohttp - асинхронные HTTP-запросы
Вспомогательные:
•	python-dotenv - управление переменными окружения
•	python-multipart - обработка multipart данных

Архитектура базы данных
Модели данных (SQLAlchemy)
Я реализовал реляционную структуру с использованием асинхронного SQLAlchemy:

# Модель продуктов в холодильнике
class FridgeItem(Base):
    user_id = Column(Integer, index=True)
    ingredient_name = Column(String(100))
    quantity = Column(String(100))
    category = Column(String(50))
# Модель рецептов
class Recipe(Base):
    user_id = Column(Integer, index=True)
    title = Column(String(200))
    ingredients = Column(JSON)
    instructions = Column(Text)
    cooking_time = Column(Integer)
Асинхронная работа с БД
Я использовал асинхронные возможности SQLAlchemy для максимальной производительности:
# Инициализация асинхронного движка
engine = create_async_engine(config.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Асинхронное получение сессии
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
Интеграция GigaChat

Аутентификация и инициализация:
self.client = GigaChat(
    credentials=config.GIGACHAT_CLIENT_SECRET,
    scope=config.GIGACHAT_SCOPE,
    verify_ssl_certs=False,
    timeout=60
)
Умный промпт-инжиниринг:
Я разработал строгий шаблон промпта, который гарантирует, что GigaChat использует только доступные ингредиенты:
def _create_strict_recipe_prompt(self, ingredients: list, user_preferences: dict) -> str:
    prompt = f"""
ЗАДАЧА: СОЗДАТЬ РЕЦЕПТ ИСКЛЮЧИТЕЛЬНО ИЗ УКАЗАННЫХ ИНГРЕДИЕНТОВ

ДОСТУПНЫЕ ИНГРЕДИЕНТЫ (ЭТО ВСЕ, ЧТО ЕСТЬ):
{formatted_ingredients}

ЗАПРЕЩЕНО:
- Добавлять любые другие ингредиенты, кроме указанных выше
- Предлагать продукты, которых нет в списке
"""
Асинхронная обработка:
# Асинхронный вызов GigaChat API
response = await asyncio.to_thread(self.client.chat, chat)
recipe_text = response.choices[0].message.content
Алгоритм умного подбора
def _select_ingredients_for_recipe(self, all_ingredients: List[str]) -> List[str]:
    # Автоматическая категоризация продуктов
    categories = {
        "белки": [], "овощи": [], "гарниры": [], 
        "молочные": [], "бакалея": []
    }
    
    # Логика комбинирования: белок + овощи + гарнир
    selected_ingredients = []
    if categories["белки"]:
        protein = random.choice(categories["белки"])
        selected_ingredients.append(protein)
Архитектура приложения
Многослойная структура
1.	Presentation Layer (bot.py)
2.	Business Logic Layer (agent.py)
3.	AI Integration Layer (gigachat_client.py)
4.	Data Access Layer (database.py, models.py)
5.	Configuration Layer (config.py)


