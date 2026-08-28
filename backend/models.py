from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Product(Base):
    """Продукты из базы Open Food Facts или добавленные вручную"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String(13), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    calories_per_100g = Column(Float, default=0)
    protein_per_100g = Column(Float, default=0)
    fat_per_100g = Column(Float, default=0)
    carbs_per_100g = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связь с записями дневника питания
    food_logs = relationship("FoodLog", back_populates="product", cascade="all, delete-orphan")


class FoodLog(Base):
    """Записи дневника питания"""
    __tablename__ = "food_log"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    meal_type = Column(String(50), nullable=False)  # breakfast, lunch, dinner, snack
    grams = Column(Integer, nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связь с продуктом
    product = relationship("Product", back_populates="food_logs")


class Exercise(Base):
    """Упражнения для тренировок"""
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связь с записями тренировок
    workouts = relationship("Workout", back_populates="exercise", cascade="all, delete-orphan")


class Workout(Base):
    """Записи тренировок"""
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    sets = Column(Integer, default=1)
    reps = Column(Integer, default=1)
    weight_kg = Column(Float, default=0)
    duration_minutes = Column(Integer, default=0)
    calories_burned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связь с упражнением
    exercise = relationship("Exercise", back_populates="workouts")
