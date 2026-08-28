from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from typing import List, Optional
import models
import schemas
import crud
import openfoodfacts
from database import engine, get_db

# Создаём таблицы БД при старте
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Calorie Tracker API",
    description="API для трекинга питания и тренировок",
    version="1.0.0"
)

# Разрешаем CORS для frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В production лучше указать конкретные origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Health check =====
@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ===== Продукты =====
@app.get("/api/products", response_model=List[schemas.Product])
async def get_products(barcode: Optional[str] = None, limit: int = 100, db: Session = Depends(get_db)):
    """Получить продукты (все или по штрихкоду)"""
    if barcode:
        product = crud.get_product_by_barcode(db, barcode)
        return [product] if product else []
    return crud.get_all_products(db, limit)


@app.get("/api/products/search", response_model=List[schemas.Product])
async def search_products(q: str, db: Session = Depends(get_db)):
    """Поиск продуктов по названию"""
    if len(q) < 2:
        return []
    return crud.search_products(db, q)


@app.post("/api/products", response_model=schemas.Product)
async def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Создать новый продукт вручную"""
    # Проверяем, нет ли уже продукта с таким штрихкодом
    existing = crud.get_product_by_barcode(db, product.barcode)
    if existing:
        raise HTTPException(status_code=400, detail="Product with this barcode already exists")
    return crud.create_product(db, product)


@app.get("/api/products/off/barcode/{barcode}")
async def get_product_from_off(barcode: str):
    """Получить продукт из Open Food Facts по штрихкоду"""
    if len(barcode) < 8 or len(barcode) > 13:
        raise HTTPException(status_code=400, detail="Invalid barcode length")
    
    product_data = await openfoodfacts.get_product_by_barcode(barcode)
    
    if not product_data:
        raise HTTPException(status_code=404, detail="Product not found in Open Food Facts")
    
    return product_data


@app.get("/api/products/off/search")
async def search_products_off(q: str, limit: int = 20):
    """Поиск продуктов в Open Food Facts по названию"""
    if len(q) < 2:
        return []
    return await openfoodfacts.search_products(q, limit)


# ===== Дневник питания =====
@app.get("/api/food-log", response_model=List[schemas.FoodLog])
async def get_food_log(
    date_str: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получить записи дневника питания за дату"""
    if date_str:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        target_date = date.today()
    
    return crud.get_food_log_by_date(db, target_date)


@app.get("/api/food-log/stats")
async def get_food_log_stats(
    start: str = Query(default_factory=lambda: (date.today() - timedelta(days=6)).isoformat()),
    end: str = Query(default_factory=lambda: date.today().isoformat()),
    db: Session = Depends(get_db)
):
    """Получить статистику питания за период"""
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    return crud.get_food_log_stats(db, start_date, end_date)


@app.post("/api/food-log", response_model=schemas.FoodLog)
async def create_food_log(food_log: schemas.FoodLogCreate, db: Session = Depends(get_db)):
    """Добавить запись в дневник питания"""
    product = crud.get_product_by_id(db, food_log.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return crud.create_food_log(db, food_log, product)


@app.delete("/api/food-log/{food_log_id}")
async def delete_food_log(food_log_id: int, db: Session = Depends(get_db)):
    """Удалить запись из дневника питания"""
    if not crud.delete_food_log(db, food_log_id):
        raise HTTPException(status_code=404, detail="Food log entry not found")
    return {"message": "Deleted successfully"}


# ===== Упражнения =====
@app.get("/api/exercises", response_model=List[schemas.Exercise])
async def get_exercises(db: Session = Depends(get_db)):
    """Получить все упражнения"""
    return crud.get_exercises(db)


@app.post("/api/exercises", response_model=schemas.Exercise)
async def create_exercise(exercise: schemas.ExerciseCreate, db: Session = Depends(get_db)):
    """Создать новое упражнение"""
    return crud.create_exercise(db, exercise)


@app.delete("/api/exercises/{exercise_id}")
async def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    """Удалить упражнение"""
    if not crud.delete_exercise(db, exercise_id):
        raise HTTPException(status_code=404, detail="Exercise not found")
    return {"message": "Deleted successfully"}


# ===== Тренировки =====
@app.get("/api/workouts", response_model=List[schemas.Workout])
async def get_workouts(
    start: Optional[str] = None,
    end: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получить тренировки за период"""
    if start and end:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    else:
        # По умолчанию за последние 30 дней
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
    
    return crud.get_workouts_in_range(db, start_date, end_date)


@app.post("/api/workouts", response_model=schemas.Workout)
async def create_workout(workout: schemas.WorkoutCreate, db: Session = Depends(get_db)):
    """Добавить запись о тренировке"""
    exercise = crud.get_exercise_by_id(db, workout.exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    return crud.create_workout(db, workout)


@app.put("/api/workouts/{workout_id}", response_model=schemas.Workout)
async def update_workout(
    workout_id: int,
    workout_update: schemas.WorkoutUpdate,
    db: Session = Depends(get_db)
):
    """Обновить запись о тренировке"""
    updated = crud.update_workout(db, workout_id, workout_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Workout not found")
    return updated


@app.delete("/api/workouts/{workout_id}")
async def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    """Удалить запись о тренировке"""
    if not crud.delete_workout(db, workout_id):
        raise HTTPException(status_code=404, detail="Workout not found")
    return {"message": "Deleted successfully"}


@app.get("/api/workouts/heatmap", response_model=List[schemas.HeatmapData])
async def get_heatmap(year: int = Query(default_factory=lambda: datetime.now().year), db: Session = Depends(get_db)):
    """Получить данные для heatmap календаря тренировок"""
    return crud.get_heatmap_data(db, year)


@app.get("/api/workouts/progress", response_model=List[schemas.ProgressData])
async def get_progress_data(
    start: str = Query(default_factory=lambda: (date.today() - timedelta(days=29)).isoformat()),
    end: str = Query(default_factory=lambda: date.today().isoformat()),
    db: Session = Depends(get_db)
):
    """Получить данные для графиков прогресса"""
    start_date = datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.strptime(end, "%Y-%m-%d").date()
    return crud.get_progress_data(db, start_date, end_date)
