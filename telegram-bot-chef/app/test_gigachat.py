import asyncio
import sys
import os

sys.path.append(os.path.dirname(__file__))

from gigachat_client import gigachat_client

async def test_gigachat():
    print(" Тестируем GigaChat...")
    
    if not gigachat_client.is_available():
        print("❌ GigaChat не доступен")
        return False
    
    ingredients = ["помидоры 3 шт", "яйца 5 шт"]
    preferences = {"cooking_skill": "новичок", "dietary_preferences": [], "allergies": []}
    
    print(f" Тестовые ингредиенты: {ingredients}")
    recipe = await gigachat_client.generate_recipe(ingredients, preferences)
    
    if recipe:
        print("✅ GigaChat работает!")
        print(f" Ответ:\n{recipe}")
        return True
    else:
        print("❌ GigaChat не вернул рецепт")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_gigachat())
    if result:
        print("\n GigaChat настроен правильно!")
    else:
        print("\n Проверьте настройки GigaChat в .env файле")