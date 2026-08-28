from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime, timedelta
from typing import List, Optional
import models
import schemas


# ===== Продукты =====
def get_product_by_barcode(db: Session, barcode: str) -> Optional[models.Product]:
    """Найти продукт по штрихкоду"""
    return db.query(models.Product).filter(
        models.Product.barcode == barcode
    ).first()


def get_product_by_id(db: Session, product_id: int) -> Optional[models.Product]:
    """Найти продукт по ID"""
    return db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()


def search_products(db: Session, query: str, limit: int = 20) -> List[models.Product]:
    """Поиск продуктов по названию"""
    return db.query(models.Product).filter(
        models.Product.name.ilike(f"%{query}%")
    ).limit(limit).all()


def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    """Создать новый продукт"""
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_all_products(db: Session, limit: int = 100) -> List[models.Product]:
    """Получить все продукты"""
    return db.query(models.Product).limit(limit).all()


# ===== Дневник питания =====
def get_food_log_by_date(db: Session, target_date: date) -> List[models.FoodLog]:
    """Получить все записи питания за дату"""
    return db.query(models.FoodLog).filter(
        models.FoodLog.date == target_date
    ).order_by(models.FoodLog.created_at.desc()).all()


def get_food_log_stats(db: Session, start_date: date, end_date: date) -> List[schemas.FoodLogStats]:
    """Получить статистику питания за период (по дням)"""
    results = []
    current = start_date
    while current <= end_date:
        logs = db.query(models.FoodLog).filter(
            models.FoodLog.date == current
        ).all()
        
        stats = schemas.FoodLogStats(
            total_calories=sum(log.calories for log in logs),
            total_protein=sum(log.protein for log in logs),
            total_fat=sum(log.fat for log in logs),
            total_carbs=sum(log.carbs for log in logs),
            meals_count=len(logs)
        )
        results.append(stats)
        current += timedelta(days=1)
    
    return results


def create_food_log(db: Session, food_log: schemas.FoodLogCreate, product: models.Product) -> models.FoodLog:
    """Создать запись в дневнике питания с автоподсчётом КБЖУ"""
    # Рассчитываем КБЖУ исходя из граммовки
    multiplier = food_log.grams / 100.0
    
    db_food_log = models.FoodLog(
        product_id=food_log.product_id,
        date=food_log.date,
        meal_type=food_log.meal_type,
        grams=food_log.grams,
        calories=product.calories_per_100g * multiplier,
        protein=product.protein_per_100g * multiplier,
        fat=product.fat_per_100g * multiplier,
        carbs=product.carbs_per_100g * multiplier
    )
    db.add(db_food_log)
    db.commit()
    db.refresh(db_food_log)
    return db_food_log


def delete_food_log(db: Session, food_log_id: int) -> bool:
    """Удалить запись из дневника питания"""
    db_food_log = db.query(models.FoodLog).filter(
        models.FoodLog.id == food_log_id
    ).first()
    if db_food_log:
        db.delete(db_food_log)
        db.commit()
        return True
    return False


# ===== Упражнения =====
def get_exercises(db: Session) -> List[models.Exercise]:
    """Получить все упражнения"""
    return db.query(models.Exercise).order_by(models.Exercise.name).all()


def get_exercise_by_id(db: Session, exercise_id: int) -> Optional[models.Exercise]:
    """Найти упражнение по ID"""
    return db.query(models.Exercise).filter(
        models.Exercise.id == exercise_id
    ).first()


def create_exercise(db: Session, exercise: schemas.ExerciseCreate) -> models.Exercise:
    """Создать новое упражнение"""
    db_exercise = models.Exercise(**exercise.model_dump())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


def delete_exercise(db: Session, exercise_id: int) -> bool:
    """Удалить упражнение"""
    db_exercise = db.query(models.Exercise).filter(
        models.Exercise.id == exercise_id
    ).first()
    if db_exercise:
        db.delete(db_exercise)
        db.commit()
        return True
    return False


# ===== Тренировки =====
def get_workouts_in_range(db: Session, start_date: datetime, end_date: datetime) -> List[models.Workout]:
    """Получить тренировки за период"""
    return db.query(models.Workout).filter(
        and_(
            models.Workout.date >= start_date,
            models.Workout.date <= end_date
        )
    ).order_by(models.Workout.date.desc()).all()


def get_workout_by_id(db: Session, workout_id: int) -> Optional[models.Workout]:
    """Найти тренировку по ID"""
    return db.query(models.Workout).filter(
        models.Workout.id == workout_id
    ).first()


def create_workout(db: Session, workout: schemas.WorkoutCreate) -> models.Workout:
    """Создать запись о тренировке"""
    db_workout = models.Workout(**workout.model_dump())
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


def update_workout(db: Session, workout_id: int, workout_update: schemas.WorkoutUpdate) -> Optional[models.Workout]:
    """Обновить запись о тренировке"""
    db_workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id
    ).first()
    if db_workout:
        update_data = workout_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_workout, key, value)
        db.commit()
        db.refresh(db_workout)
    return db_workout


def delete_workout(db: Session, workout_id: int) -> bool:
    """Удалить запись о тренировке"""
    db_workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id
    ).first()
    if db_workout:
        db.delete(db_workout)
        db.commit()
        return True
    return False


def get_heatmap_data(db: Session, year: int) -> List[schemas.HeatmapData]:
    """Получить данные для heatmap за год"""
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)
    
    # Группируем тренировки по дням и считаем объём (длительность + подходы*повторения*вес)
    workouts = db.query(
        func.date(models.Workout.date).label('workout_date'),
        func.sum(models.Workout.duration_minutes).label('total_duration'),
        func.sum(models.Workout.sets * models.Workout.reps * models.Workout.weight_kg).label('total_volume')
    ).filter(
        and_(
            models.Workout.date >= start_date,
            models.Workout.date <= end_date
        )
    ).group_by(
        func.date(models.Workout.date)
    ).all()
    
    heatmap_data = []
    for workout in workouts:
        workout_date = str(workout.workout_date)
        # Комбинируем длительность и объём для определения интенсивности
        value = int(workout.total_duration or 0) + int(workout.total_volume or 0) / 100
        
        # Определяем уровень закрашивания (0-4)
        if value == 0:
            level = 0
        elif value < 30:
            level = 1
        elif value < 60:
            level = 2
        elif value < 120:
            level = 3
        else:
            level = 4
        
        heatmap_data.append(schemas.HeatmapData(
            date=workout_date,
            value=int(value),
            level=level
        ))
    
    return heatmap_data


def get_progress_data(db: Session, start_date: date, end_date: date) -> List[schemas.ProgressData]:
    """Получить данные для графиков прогресса"""
    results = []
    current = start_date
    
    while current <= end_date:
        # Получаем данные о питании за день
        food_logs = db.query(models.FoodLog).filter(
            models.FoodLog.date == current
        ).all()
        
        # Получаем данные о тренировках за день
        workouts = db.query(models.Workout).filter(
            func.date(models.Workout.date) == current
        ).all()
        
        progress = schemas.ProgressData(
            date=str(current),
            calories=sum(log.calories for log in food_logs) if food_logs else None,
            protein=sum(log.protein for log in food_logs) if food_logs else None,
            fat=sum(log.fat for log in food_logs) if food_logs else None,
            carbs=sum(log.carbs for log in food_logs) if food_logs else None,
            workout_duration=sum(w.duration_minutes for w in workouts) if workouts else None,
            workout_volume=sum(w.sets * w.reps * w.weight_kg for w in workouts) if workouts else None
        )
        
        # Добавляем только если есть данные
        if any([progress.calories, progress.workout_duration, progress.workout_volume]):
            results.append(progress)
        
        current += timedelta(days=1)
    
    return results
