import random
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

try:
    from gigachat_client import gigachat_client
except ImportError:
    # Создаем заглушку если модуль не доступен
    class GigaChatClient:
        def __init__(self):
            self.client = None
        
        def is_available(self):
            return False
        
        async def generate_recipe(self, ingredients, preferences):
            return None
    
    gigachat_client = GigaChatClient()

class ChefAgent:
    def __init__(self):
        self.recipes_db = self._initialize_recipes()
        
    def _initialize_recipes(self) -> Dict[str, List[Dict]]:
        """Инициализация базы готовых рецептов"""
        return {
            "яйца_овощи": [
                {
                    "title": "🍳 Омлет с помидорами",
                    "ingredients": ["Яйца - 3 шт", "Помидоры - 2 шт", "Лук - 0.5 шт", "Соль - по вкусу", "Масло - 1 ст.л."],
                    "instructions": [
                        "1. Нарежьте помидоры и лук",
                        "2. Взбейте яйца с солью",
                        "3. Обжарьте лук до прозрачности",
                        "4. Добавьте помидоры, затем яичную смесь",
                        "5. Готовьте под крышкой 7 минут"
                    ],
                    "cooking_time": 15,
                    "difficulty": "легко"
                }
            ],
            "курица_овощи": [
                {
                    "title": "🍗 Курица с овощами",
                    "ingredients": ["Куриное филе - 300г", "Помидоры - 2 шт", "Лук - 1 шт", "Соль - по вкусу", "Масло - 2 ст.л."],
                    "instructions": [
                        "1. Нарежьте курицу и овощи",
                        "2. Обжарьте курицу до золотистой корочки",
                        "3. Добавьте овощи и тушите 15 минут",
                        "4. Посолите и поперчите по вкусу"
                    ],
                    "cooking_time": 25,
                    "difficulty": "легко"
                }
            ],
            "мясо_гарнир": [
                {
                    "title": "🍖 Мясо с гарниром",
                    "ingredients": ["Мясо - 400г", "Рис - 150г", "Лук - 1 шт", "Соль - по вкусу", "Масло - 2 ст.л."],
                    "instructions": [
                        "1. Нарежьте мясо и обжарьте с луком",
                        "2. Отварите рис отдельно",
                        "3. Подавайте мясо с рисом"
                    ],
                    "cooking_time": 30,
                    "difficulty": "средне"
                }
            ]
        }
    
    async def analyze_fridge(self, db: AsyncSession, user_id: int) -> List[str]:
        """Анализирует содержимое холодильника"""
        try:
            result = await db.execute(
                text("SELECT ingredient_name FROM fridge_items WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            items = result.fetchall()
            return [item.ingredient_name for item in items]
        except Exception as e:
            print(f"❌ Ошибка при анализе холодильника: {e}")
            return []
    
    async def get_user_preferences(self, db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """Получает предпочтения пользователя"""
        try:
            result = await db.execute(
                text("SELECT dietary_preferences, allergies, cooking_skill FROM users WHERE telegram_id = :user_id"),
                {"user_id": user_id}
            )
            user = result.first()
            return {
                "dietary_preferences": user.dietary_preferences if user else [],
                "allergies": user.allergies if user else [],
                "cooking_skill": user.cooking_skill if user else "новичок"
            }
        except Exception as e:
            print(f"❌ Ошибка при получении предпочтений: {e}")
            return {
                "dietary_preferences": [],
                "allergies": [],
                "cooking_skill": "новичок"
            }
    
    def _select_ingredients_for_recipe(self, all_ingredients: List[str]) -> List[str]:
        """Умно выбирает подходящие комбинации ингредиентов для рецепта"""
        print(f"🔄 Выбираем ингредиенты из: {all_ingredients}")
        
        # Парсим ингредиенты для анализа
        parsed_ingredients = []
        for ing in all_ingredients:
            if " " in ing:
                name = ing.split(" ")[0].lower()
                parsed_ingredients.append(name)
            else:
                parsed_ingredients.append(ing.lower())
        
        # Группируем ингредиенты по категориям
        categories = {
            "белки": [],
            "овощи": [],
            "гарниры": [],
            "молочные": [],
            "бакалея": []
        }
        
        for ing in parsed_ingredients:
            if any(protein in ing for protein in ["куриц", "филе", "мясо", "говядин", "свинин", "рыба", "яйц"]):
                categories["белки"].append(ing)
            elif any(veggie in ing for veggie in ["помидор", "огурец", "морковь", "лук", "перец", "баклажан", "кабачок", "картош", "капуст"]):
                categories["овощи"].append(ing)
            elif any(carb in ing for carb in ["рис", "паста", "спагетти", "макарон", "греч", "пшено"]):
                categories["гарниры"].append(ing)
            elif any(dairy in ing for dairy in ["молоко", "сыр", "сметан", "творог", "йогурт", "кефир"]):
                categories["молочные"].append(ing)
            else:
                categories["бакалея"].append(ing)
        
        print(f"📊 Сгруппированные ингредиенты: {categories}")
        
        # Выбираем логичные комбинации
        selected_ingredients = []
        
        # Всегда берем 1 белок (если есть)
        if categories["белки"]:
            protein = random.choice(categories["белки"])
            # Находим полное название с количеством
            full_protein = next((ing for ing in all_ingredients if protein in ing.lower()), protein)
            selected_ingredients.append(full_protein)
        
        # Берем 1-2 овоща (если есть)
        if categories["овощи"]:
            veggies = random.sample(categories["овощи"], min(2, len(categories["овощи"])))
            for veggie in veggies:
                full_veggie = next((ing for ing in all_ingredients if veggie in ing.lower()), veggie)
                selected_ingredients.append(full_veggie)
        
        # Берем 1 гарнир (если есть и если выбран белок)
        if categories["гарниры"] and categories["белки"]:
            carb = random.choice(categories["гарниры"])
            full_carb = next((ing for ing in all_ingredients if carb in ing.lower()), carb)
            selected_ingredients.append(full_carb)
        
        # Берем 1 молочный продукт (только для определенных комбинаций)
        if categories["молочные"] and any(dairy in selected_ingredients for dairy in ["яйц", "творог"]):
            dairy = random.choice(categories["молочные"])
            full_dairy = next((ing for ing in all_ingredients if dairy in ing.lower()), dairy)
            selected_ingredients.append(full_dairy)
        
        # Если выбрано слишком мало, добавляем еще овощей
        if len(selected_ingredients) < 2 and categories["овощи"]:
            extra_veggies = [v for v in categories["овощи"] if v not in selected_ingredients]
            if extra_veggies:
                extra = random.choice(extra_veggies)
                full_extra = next((ing for ing in all_ingredients if extra in ing.lower()), extra)
                selected_ingredients.append(full_extra)
        
        print(f"✅ Выбраны ингредиенты: {selected_ingredients}")
        return selected_ingredients
    
    async def create_recipe(self, ingredients: List[str], preferences: Dict) -> Dict[str, Any]:
        """Создает рецепт на основе выбранных ингредиентов"""
        
        print(f"🔄 Создание рецепта из всех ингредиентов: {ingredients}")
        
        # Умно выбираем подходящие ингредиенты для одного рецепта
        selected_ingredients = self._select_ingredients_for_recipe(ingredients)
        
        if not selected_ingredients:
            print("❌ Не удалось выбрать подходящие ингредиенты")
            return self._get_fallback_recipe(ingredients)
        
        # В первую очередь пытаемся использовать GigaChat
        if gigachat_client.is_available():
            try:
                print(f"🎯 Используем GigaChat для выбранных ингредиентов: {selected_ingredients}")
                recipe_text = await gigachat_client.generate_recipe(selected_ingredients, preferences)
                
                if recipe_text:
                    print("✅ Получен ответ от GigaChat, парсим...")
                    parsed_recipe = self._parse_gigachat_response(recipe_text, selected_ingredients)
                    if parsed_recipe:
                        print("✅ Успешно использован рецепт от GigaChat")
                        return parsed_recipe
                    else:
                        print("❌ Не удалось распарсить ответ GigaChat")
                else:
                    print("❌ GigaChat не вернул рецепт")
                    
            except Exception as e:
                print(f"❌ Ошибка GigaChat: {e}")
        
        # Резервный вариант - локальная база на основе выбранных ингредиентов
        print("🔄 Используем адаптированный рецепт на основе выбранных продуктов")
        return self._get_adapted_recipe(selected_ingredients)
    
    def _get_adapted_recipe(self, ingredients: List[str]) -> Dict[str, Any]:
        """Создает адаптированный рецепт на основе выбранных ингредиентов"""
        # Создаем список ингредиентов для рецепта
        adapted_ingredients = []
        for ing in ingredients:
            # Парсим количество из исходного формата
            if " " in ing:
                parts = ing.split(" ")
                if len(parts) >= 2:
                    name = parts[0]
                    quantity = " ".join(parts[1:])
                    adapted_ingredients.append(f"{name} - {quantity}")
                else:
                    adapted_ingredients.append(f"{ing} - по вкусу")
            else:
                adapted_ingredients.append(f"{ing} - по вкусу")
        
        # Добавляем базовые специи
        adapted_ingredients.extend(["Соль - по вкусу", "Перец - по вкусу", "Растительное масло - 2 ст.л."])
        
        # Определяем тип блюда по выбранным ингредиентам
        ingredient_text = " ".join(ingredients).lower()
        
        if any(word in ingredient_text for word in ["яйц", "омлет"]):
            title = "🍳 Омлет с выбранными ингредиентами"
            instructions = [
                "1. Подготовьте и нарежьте ингредиенты",
                "2. Взбейте яйца с солью",
                "3. Обжарьте основные компоненты",
                "4. Залейте яичной смесью",
                "5. Готовьте под крышкой на среднем огне 7-10 минут"
            ]
        elif any(word in ingredient_text for word in ["куриц", "филе", "мясо"]):
            if any(word in ingredient_text for word in ["рис", "паста", "греч"]):
                title = "🍗 Мясо с гарниром"
                instructions = [
                    "1. Нарежьте мясо и обжарьте до готовности",
                    "2. Приготовьте гарнир отдельно",
                    "3. Подавайте мясо с гарниром"
                ]
            else:
                title = "🍖 Мясное блюдо с овощами"
                instructions = [
                    "1. Нарежьте мясо и овощи",
                    "2. Обжарьте мясо до золотистой корочки",
                    "3. Добавьте овощи и тушите 15-20 минут",
                    "4. Добавьте специи по вкусу"
                ]
        else:
            title = "🍲 Овощное блюдо"
            instructions = [
                "1. Подготовьте и нарежьте овощи",
                "2. Обжарьте на среднем огне до мягкости",
                "3. Добавьте специи по вкусу",
                "4. Тушите под крышкой 10-15 минут"
            ]
        
        return {
            "title": title,
            "ingredients": adapted_ingredients,
            "instructions": instructions,
            "cooking_time": 25,
            "difficulty": "легко"
        }
    
    def _parse_gigachat_response(self, response: str, original_ingredients: List[str]) -> Dict[str, Any]:
        """Парсит ответ от GigaChat в структурированный рецепт"""
        try:
            print(f"📝 Парсим ответ GigaChat: {response[:200]}...")
            
            lines = response.split('\n')
            title = ""
            ingredients = []
            instructions = []
            cooking_time = 20
            difficulty = "средне"
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Определяем заголовок (ищем первую значимую строку)
                if not title and line and not any(keyword in line.lower() for keyword in ["ингредиенты", "приготовление", "время", "сложность"]):
                    title = line
                    continue
                    
                # Определяем секции
                if "ингредиенты" in line.lower():
                    current_section = "ingredients"
                    continue
                elif "приготовление" in line.lower():
                    current_section = "instructions"
                    continue
                elif "время" in line.lower() and "приготовления" in line.lower():
                    # Парсим время
                    for word in line.split():
                        if word.isdigit():
                            cooking_time = int(word)
                            break
                    continue
                elif "сложность" in line.lower():
                    difficulty_parts = line.split(':')
                    if len(difficulty_parts) > 1:
                        difficulty = difficulty_parts[1].strip().lower()
                    continue
                
                # Парсим содержимое секций
                if current_section == "ingredients":
                    if line.startswith('-') or line.startswith('•'):
                        ingredients.append(line[1:].strip())
                    elif line and not line[0].isdigit():
                        ingredients.append(line)
                elif current_section == "instructions":
                    if (line.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9', '0')) and 
                        ('.' in line or ')' in line or ' ' in line)):
                        instructions.append(line)
                    elif line and not any(keyword in line.lower() for keyword in ["время", "сложность"]):
                        instructions.append(line)
            
            # Если заголовок не найден, создаем свой
            if not title:
                title = "🍳 Рецепт от GigaChat"
            
            # Если ингредиенты не распарсились, используем оригинальные
            if not ingredients:
                ingredients = [f"{ing} - по вкусу" for ing in original_ingredients]
                ingredients.extend(["Соль - по вкусу", "Перец - по вкусу"])
            
            # Если инструкции не распарсились, создаем базовые
            if not instructions:
                instructions = [
                    "1. Подготовьте все ингредиенты",
                    "2. Следуйте общей логике приготовления",
                    "3. Готовьте до готовности основных компонентов",
                    "4. Добавьте специи по вкусу",
                    "5. Подавайте горячим"
                ]
            
            print(f"✅ Успешно распарсен рецепт: {title}")
            
            return {
                "title": title,
                "ingredients": ingredients,
                "instructions": instructions,
                "cooking_time": cooking_time,
                "difficulty": difficulty
            }
            
        except Exception as e:
            print(f"❌ Ошибка парсинга ответа GigaChat: {e}")
            return None
    
    def _get_fallback_recipe(self, ingredients: List[str]) -> Dict[str, Any]:
        """Резервный рецепт"""
        return {
            "title": "🍳 Простое блюдо из доступных ингредиентов",
            "ingredients": [f"{ing} - по вкусу" for ing in ingredients] + ["Соль - по вкусу", "Перец - по вкусу", "Растительное масло - 2 ст.л."],
            "instructions": [
                "1. Подготовьте все ингредиенты",
                "2. Обжарьте основные компоненты на среднем огне",
                "3. Добавьте специи по вкусу",
                "4. Готовьте до готовности",
                "5. Подавайте горячим"
            ],
            "cooking_time": 20,
            "difficulty": "легко"
        }
    
    async def save_recipe(self, db: AsyncSession, user_id: int, recipe_data: Dict) -> int:
        """Сохраняет рецепт в базу данных"""
        try:
            from models import Recipe
            recipe = Recipe(
                user_id=user_id,
                title=recipe_data["title"],
                ingredients=recipe_data["ingredients"],
                instructions="\n".join(recipe_data["instructions"]),
                cooking_time=recipe_data["cooking_time"],
                difficulty=recipe_data["difficulty"]
            )
            db.add(recipe)
            await db.commit()
            await db.refresh(recipe)
            return recipe.id
        except Exception as e:
            print(f"❌ Ошибка при сохранении рецепта: {e}")
            return 0
    
    async def process_user_request(self, db: AsyncSession, user_id: int, message: str) -> str:
        """Основной метод обработки запросов"""
        try:
            fridge_items = await self.analyze_fridge(db, user_id)
            
            if not fridge_items:
                return "😔 Ваш холодильник пуст. Добавьте продукты через меню '🥕 Мой холодильник'!"
            
            preferences = await self.get_user_preferences(db, user_id)
            recipe = await self.create_recipe(fridge_items, preferences)
            recipe_id = await self.save_recipe(db, user_id, recipe)
            
            response = f"🍴 *{recipe['title']}*\n\n"
            response += "🥕 *Ингредиенты:*\n" + "\n".join(f"• {ing}" for ing in recipe['ingredients']) + "\n\n"
            response += "👨‍🍳 *Приготовление:*\n" + "\n".join(recipe['instructions']) + "\n\n"
            response += f"⏱ *Время:* {recipe['cooking_time']} мин\n"
            response += f"📊 *Сложность:* {recipe['difficulty']}\n"
            
            if recipe_id:
                response += f"\n📝 Рецепт сохранен под номером #{recipe_id}"
            
            return response
            
        except Exception as e:
            print(f"❌ Ошибка в process_user_request: {e}")
            return f"🍳 Извините, произошла ошибка: {str(e)}"

chef_agent = ChefAgent()