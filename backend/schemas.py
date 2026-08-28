from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


# ===== Продукты =====
class ProductBase(BaseModel):
    barcode: str = Field(..., max_length=13)
    name: str
    calories_per_100g: float = 0
    protein_per_100g: float = 0
    fat_per_100g: float = 0
    carbs_per_100g: float = 0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    calories_per_100g: Optional[float] = None
    protein_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None
    carbs_per_100g: Optional[float] = None


class Product(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Дневник питания =====
class FoodLogBase(BaseModel):
    product_id: int
    date: date
    meal_type: str  # breakfast, lunch, dinner, snack
    grams: int


class FoodLogCreate(FoodLogBase):
    pass


class FoodLog(FoodLogBase):
    id: int
    calories: float
    protein: float
    fat: float
    carbs: float
    created_at: datetime
    product: Optional[Product] = None

    class Config:
        from_attributes = True


class FoodLogStats(BaseModel):
    total_calories: float = 0
    total_protein: float = 0
    total_fat: float = 0
    total_carbs: float = 0
    meals_count: int = 0


# ===== Упражнения =====
class ExerciseBase(BaseModel):
    name: str


class ExerciseCreate(ExerciseBase):
    pass


class Exercise(ExerciseBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Тренировки =====
class WorkoutBase(BaseModel):
    exercise_id: int
    date: datetime
    sets: int = 1
    reps: int = 1
    weight_kg: float = 0
    duration_minutes: int = 0
    calories_burned: int = 0


class WorkoutCreate(WorkoutBase):
    pass


class WorkoutUpdate(BaseModel):
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_minutes: Optional[int] = None
    calories_burned: Optional[int] = None


class Workout(WorkoutBase):
    id: int
    created_at: datetime
    exercise: Optional[Exercise] = None

    class Config:
        from_attributes = True


class HeatmapData(BaseModel):
    """Данные для heatmap календаря"""
    date: str  # YYYY-MM-DD
    value: int  # Интенсивность (длительность или объём тренировки)
    level: int  # Уровень закрашивания (0-4)


class ProgressData(BaseModel):
    """Данные для графиков прогресса"""
    date: str
    calories: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbs: Optional[float] = None
    workout_duration: Optional[int] = None
    workout_volume: Optional[float] = None  # sum(sets * reps * weight)


# ===== Open Food Facts Response =====
class OFFProduct(BaseModel):
    """Структура ответа от Open Food Facts API"""
    barcode: str
    product_name: Optional[str] = None
    energy_100g: Optional[float] = None  # в кДж, нужно конвертировать в ккал
    nutriments: Optional[dict] = {}
