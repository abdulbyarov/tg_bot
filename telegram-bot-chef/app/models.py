from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    dietary_preferences = Column(JSON, default=[])
    allergies = Column(JSON, default=[])
    cooking_skill = Column(String(50), default="новичок")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FridgeItem(Base):
    __tablename__ = "fridge_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    ingredient_name = Column(String(100))
    quantity = Column(String(100))
    category = Column(String(50))
    expires_in = Column(Integer)

class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    title = Column(String(200))
    ingredients = Column(JSON)
    instructions = Column(Text)
    cooking_time = Column(Integer)
    difficulty = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())