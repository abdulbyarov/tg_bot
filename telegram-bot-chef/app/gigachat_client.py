import asyncio
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
from config import config

class GigaChatClient:
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        try:
            if not config.GIGACHAT_CLIENT_SECRET:
                print("❌ GIGACHAT_CLIENT_SECRET не установлен в .env файле")
                return
            
            print("🔄 Инициализация GigaChat клиента...")
            
            self.client = GigaChat(
                credentials=config.GIGACHAT_CLIENT_SECRET,
                scope=config.GIGACHAT_SCOPE,
                verify_ssl_certs=False,
                timeout=60
            )
            
            # Проверяем подключение
            print("✅ GigaChat клиент инициализирован")
            
        except Exception as e:
            print(f"❌ Ошибка инициализации GigaChat: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        #Проверяет, доступен ли GigaChat
        return self.client is not None and config.GIGACHAT_CLIENT_SECRET is not None
    
    async def generate_recipe(self, ingredients: list, user_preferences: dict) -> str:
        
        if not self.is_available():
            print("❌ GigaChat клиент не доступен")
            return None
        
        prompt = self._create_strict_recipe_prompt(ingredients, user_preferences)
        
        try:
            print(f"🔄 Генерируем рецепт для ингредиентов: {ingredients}")
            
            system_message = """Ты - профессиональный шеф-повар. Твоя задача - создавать рецепты ИСКЛЮЧИТЕЛЬНО из указанных пользователем ингредиентов.

СТРОГИЕ ПРАВИЛА:
1. Используй ТОЛЬКО те ингредиенты, которые указал пользователь
2. Можешь добавить только базовые специи: соль, перец, растительное масло, сахар, вода
3. НИКОГДА не добавляй дополнительные ингредиенты, которых нет у пользователя
4. Если ингредиентов недостаточно - предложи максимально простой вариант
5. Всегда отвечай на русском языке
6. Строго соблюдай указанный формат ответа"""

            messages = [
                Messages(role=MessagesRole.SYSTEM, content=system_message),
                Messages(role=MessagesRole.USER, content=prompt)
            ]
            
            chat = Chat(
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Асинхронный вызов с таймаутом
            print(" Отправляем запрос к GigaChat...")
            response = await asyncio.to_thread(self.client.chat, chat)
            
            if not response or not response.choices:
                print("❌ Пустой ответ от GigaChat")
                return None
            
            recipe_text = response.choices[0].message.content
            print("✅ Рецепт успешно сгенерирован GigaChat")
            print(f" Длина ответа: {len(recipe_text)} символов")
            
            return recipe_text
            
        except asyncio.TimeoutError:
            print("❌ Таймаут при запросе к GigaChat")
            return None
        except Exception as e:
            print(f"❌ Ошибка GigaChat: {str(e)}")
            return None
    
    def _create_strict_recipe_prompt(self, ingredients: list, user_preferences: dict) -> str:
        
        # Форматируем ингредиенты для лучшего восприятия
        formatted_ingredients = "\n".join([f"- {ing}" for ing in ingredients])
        
        prompt = f"""
ЗАДАЧА: СОЗДАТЬ КУЛИНАРНЫЙ РЕЦЕПТ ИСКЛЮЧИТЕЛЬНО ИЗ УКАЗАННЫХ ИНГРЕДИЕНТОВ

ДОСТУПНЫЕ ИНГРЕДИЕНТЫ (ЭТО ВСЕ, ЧТО ЕСТЬ):
{formatted_ingredients}

РАЗРЕШЕННЫЕ ДОПОЛНЕНИЯ (только если нужны):
- соль
- перец  
- растительное масло
- сахар
- вода

ЗАПРЕЩЕНО:
- Добавлять любые другие ингредиенты, кроме указанных выше
- Предлагать продукты, которых нет в списке
- Использовать ингредиенты, которых у пользователя нет

ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ:
- Уровень кулинарных навыков: {user_preferences.get('cooking_skill', 'новичок')}
- Диетические предпочтения: {', '.join(user_preferences.get('dietary_preferences', [])) or 'нет'}
- Аллергии: {', '.join(user_preferences.get('allergies', [])) or 'нет'}

ТРЕБОВАНИЯ К РЕЦЕПТУ:
1. Используй ТОЛЬКО доступные ингредиенты из списка выше
2. Учитывай уровень навыков пользователя
3. Сделай рецепт практичным и выполнимым
4. Укажи точное время приготовления
5. Оцени сложность приготовления

ФОРМАТ ОТВЕТА (ОБЯЗАТЕЛЬНО СОБЛЮДАЙ!):

НАЗВАНИЕ РЕЦЕПТА (с эмодзи)

ИНГРЕДИЕНТЫ:
- ингредиент 1 - количество (только из списка выше)
- ингредиент 2 - количество (только из списка выше)
...

ПРИГОТОВЛЕНИЕ:
1. Шаг 1 приготовления
2. Шаг 2 приготовления
...

ВРЕМЯ ПРИГОТОВЛЕНИЯ: X минут
СЛОЖНОСТЬ: легко/средне/сложно

ПОВТОРЯЮ: НЕ ДОБАВЛЯЙ НИКАКИХ ДРУГИХ ИНГРЕДИЕНТОВ, КРОМЕ ТЕХ, ЧТО В СПИСКЕ!
"""

        return prompt

    async def test_connection(self) -> bool:
        """Тестирует подключение к GigaChat"""
        if not self.is_available():
            return False
        
        try:
            test_messages = [
                Messages(role=MessagesRole.SYSTEM, content="Ты - помощник. Ответь коротко 'Тест пройден'"),
                Messages(role=MessagesRole.USER, content="Тестовое сообщение")
            ]
            
            chat = Chat(messages=test_messages)
            response = await asyncio.to_thread(self.client.chat, chat)
            
            if response and response.choices:
                print("✅ Тест подключения к GigaChat пройден")
                return True
            else:
                print("❌ Тест подключения к GigaChat не пройден")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка тестирования подключения: {e}")
            return False

# Создаем глобальный экземпляр клиента
gigachat_client = GigaChatClient()

# Функция для тестирования модуля
async def test_gigachat_module():
    print("\n Тестирование модуля GigaChat...")
    
    if not gigachat_client.is_available():
        print("❌ GigaChat не доступен. Проверьте настройки в .env файле:")
        print(f"   - GIGACHAT_CLIENT_SECRET: {'установлен' if config.GIGACHAT_CLIENT_SECRET else 'НЕ УСТАНОВЛЕН'}")
        print(f"   - GIGACHAT_SCOPE: {config.GIGACHAT_SCOPE}")
        return False
    
    # Тестируем подключение
    connection_ok = await gigachat_client.test_connection()
    if not connection_ok:
        print("❌ Не удалось подключиться к GigaChat")
        return False
    
    
    test_ingredients = ["помидоры 2 шт", "яйца 3 шт", "лук 1 шт"]
    test_preferences = {
        "cooking_skill": "новичок",
        "dietary_preferences": [],
        "allergies": []
    }
    
    print(f" Тестовые ингредиенты: {test_ingredients}")
    recipe = await gigachat_client.generate_recipe(test_ingredients, test_preferences)
    
    if recipe:
        print("✅ Генерация рецепта успешна!")
        print(f" Рецепт:\n{recipe}")
        return True
    else:
        print("❌ Не удалось сгенерировать рецепт")
        return False

if __name__ == "__main__":
    # Запуск теста при прямом выполнении файла
    import asyncio
    result = asyncio.run(test_gigachat_module())
    if result:
        print("\n Модуль GigaChat работает корректно!")
    else:
        print("\n Требуется настройка GigaChat. Проверьте:")
        print("   - Файл .env с GIGACHAT_CLIENT_SECRET")
        print("   - Интернет-подключение")
        print("   - Доступность сервиса GigaChat")