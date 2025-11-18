# Telegram-бот "Шеф-помощник": Разработка кулинарного ассистента

## О проекте

Я разработал интеллектуального Telegram-бота "Шеф-помощник", который создает персонализированные рецепты на основе продуктов, имеющихся у пользователя в холодильнике. Бот сочетает в себе современные технологии искусственного интеллекта и классические подходы к разработке программного обеспечения.

## Технологический стек

### Python-библиотеки и фреймворки

**Основные зависимости:**
- `aiogram` - современный асинхронный фреймворк для Telegram Bot API
- `fastapi` - высокопроизводительный веб-фреймворк для создания API
- `uvicorn` - ASGI-сервер для запуска FastAPI приложений

**Работа с данными:**
- `sqlalchemy` - ORM для работы с базой данных
- `alembic` - инструмент для миграций базы данных
- `asyncpg` - асинхронный драйвер для PostgreSQL

**Интеграция с AI:**
- `gigachat` - официальная библиотека для работы с GigaChat API от Сбера
- `aiohttp` - асинхронные HTTP-запросы

**Вспомогательные:**
- `python-dotenv` - управление переменными окружения
- `python-multipart` - обработка multipart данных

## Архитектура базы данных

### Модели данных (SQLAlchemy)

Я реализовал реляционную структуру с использованием асинхронного SQLAlchemy:

```python
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
```
### Асинхронная работа с БД
Я использовал асинхронные возможности SQLAlchemy для максимальной производительности:
```python
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
```
## Интеграция GigaChat

### Аутентификация и инициализация:
```python
self.client = GigaChat(
    credentials=config.GIGACHAT_CLIENT_SECRET,
    scope=config.GIGACHAT_SCOPE,
    verify_ssl_certs=False,
    timeout=60
)
```
### Асинхронная обработка:
```python
# Асинхронный вызов GigaChat API
response = await asyncio.to_thread(self.client.chat, chat)
recipe_text = response.choices[0].message.content
```
### Алгоритм умного подбора
```python
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
```

## Архитектура приложения

### Многослойная структура

Presentation Layer (bot.py)

Business Logic Layer (agent.py)

AI Integration Layer (gigachat_client.py)

Data Access Layer (database.py, models.py)

Configuration Layer (config.py)
