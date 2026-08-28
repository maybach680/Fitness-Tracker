# Self-hosted Calorie & Workout Tracker

Полностью автономный веб-сервис для трекинга питания и тренировок с поддержкой PWA.

## Возможности

### Питание
- 📱 Сканирование штрихкодов через камеру телефона
- 🔍 Поиск продуктов в базе Open Food Facts (поддерживает российские штрихкоды)
- ➕ Ручное добавление продуктов
- 📊 Дневник питания с автоподсчётом КБЖУ
- 💾 Локальное кеширование продуктов

### Тренировки
- 🏋️ Логирование упражнений (подходы, повторения, вес, длительность)
- 📅 Heatmap-календарь в стиле GitHub
- 📈 Графики прогресса (вес, калории, объём тренировок)

## Быстрый старт

```bash
cd calorie-tracker
docker-compose up -d
```

Сервис будет доступен по адресу: `http://localhost:8080`

## Структура проекта

```
calorie-tracker/
├── docker-compose.yml      # Оркестрация контейнеров
├── README.md               # Этот файл
├── backend/                # FastAPI сервер
│   ├── Dockerfile
│   ├── main.py            # Точки входа API
│   ├── database.py        # Настройки БД
│   ├── models.py          # SQLAlchemy модели
│   ├── schemas.py         # Pydantic схемы
│   ├── crud.py            # Операции с БД
│   └── openfoodfacts.py   # Интеграция с OFF API
└── frontend/              # Vue 3 PWA приложение
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── index.html
    ├── public/
    │   └── manifest.json  # PWA манифест
    └── src/
        ├── main.js
        ├── App.vue
        ├── components/    # Vue компоненты
        ├── stores/        # Pinia хранилища
        ├── utils/         # Утилиты
        └── styles/        # Стили
```

## Схема базы данных

### products
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| barcode | VARCHAR(13) UNIQUE | Штрихкод |
| name | VARCHAR(255) | Название продукта |
| calories_per_100g | FLOAT | Калории на 100г |
| protein_per_100g | FLOAT | Белки на 100г |
| fat_per_100g | FLOAT | Жиры на 100г |
| carbs_per_100g | FLOAT | Углеводы на 100г |
| created_at | DATETIME | Дата добавления |

### food_log
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| product_id | INTEGER FK | Ссылка на продукт |
| date | DATE | Дата приёма пищи |
| meal_type | VARCHAR(50) | Тип приёма (завтрак/обед/ужин/перекус) |
| grams | INTEGER | Вес в граммах |
| calories | FLOAT | Посчитанные калории |
| protein | FLOAT | Посчитанные белки |
| fat | FLOAT | Посчитанные жиры |
| carbs | FLOAT | Посчитанные углеводы |

### exercises
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| name | VARCHAR(255) UNIQUE | Название упражнения |
| created_at | DATETIME | Дата создания |

### workouts
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER | Первичный ключ |
| exercise_id | INTEGER FK | Ссылка на упражнение |
| date | DATETIME | Дата тренировки |
| sets | INTEGER | Количество подходов |
| reps | INTEGER | Повторения за подход |
| weight_kg | FLOAT | Вес снаряда (кг) |
| duration_minutes | INTEGER | Длительность (мин) |
| calories_burned | INTEGER | Потраченные калории |

## API Endpoints

### Продукты
- `GET /api/products?barcode=123` — поиск по штрихкоду
- `GET /api/products/search?q=яблоко` — поиск по названию
- `POST /api/products` — добавить продукт вручную
- `GET /api/products/off/barcode/123` — получить из Open Food Facts

### Дневник питания
- `GET /api/food-log?date=2024-01-15` — получить записи за дату
- `POST /api/food-log` — добавить запись
- `DELETE /api/food-log/{id}` — удалить запись
- `GET /api/food-log/stats?start=2024-01-01&end=2024-01-31` — статистика за период

### Упражнения
- `GET /api/exercises` — список упражнений
- `POST /api/exercises` — добавить упражнение
- `DELETE /api/exercises/{id}` — удалить упражнение

### Тренировки
- `GET /api/workouts?start=2024-01-01&end=2024-01-31` — тренировки за период
- `POST /api/workouts` — добавить тренировку
- `DELETE /api/workouts/{id}` — удалить тренировку
- `GET /api/workouts/heatmap?year=2024` — данные для heatmap
- `GET /api/workouts/progress` — данные для графиков прогресса

## Технология сканирования штрихкодов

Используется библиотека **Quagga.js** для распознавания штрихкодов через браузерный API камеры. Поддерживаемые форматы:
- EAN-13 (наиболее распространён в России)
- EAN-8
- UPC
- Code 128

**Важно:** Для работы камеры требуется HTTPS или localhost. При доступе по IP используйте HTTPS.

## PWA (Progressive Web App)

Приложение можно установить на домашний экран телефона:
1. Откройте сайт в Chrome/Safari на телефоне
2. Нажмите "Поделиться" → "На экран 'Домой'"
3. Приложение откроется как нативное (без адресной строки)

Service Worker кэширует статику для работы офлайн (просмотр уже загруженных данных).

## Безопасность

Так как приложение single-user и self-hosted:
- Нет системы пользователей/паролей
- Данные хранятся локально в SQLite
- Рекомендуется использовать за reverse proxy (nginx) с базовой авторизацией при доступе извне

Для добавления basic auth раскомментируйте секцию в docker-compose.yml.

## Переменные окружения

| Переменная | Значение по умолчанию | Описание |
|------------|----------------------|----------|
| DATABASE_URL | sqlite:///./data/tracker.db | Строка подключения к БД |
| OPENFOODFACTS_API | https://world.openfoodfacts.org | URL API Open Food Facts |

## Troubleshooting

**Камера не работает:**
- Убедитесь, что используется HTTPS или localhost
- Проверьте разрешения браузера на доступ к камере
- На iOS Safari требуется явное разрешение пользователя

**Продукты не находятся по штрихкоду:**
- Не все продукты есть в базе Open Food Facts
- Добавьте продукт вручную через форму
- Продукт сохранится в локальной БД для будущего использования

**Docker контейнеры не запускаются:**
```bash
docker-compose down
docker-compose up --build
```

## Лицензия

MIT License — свободное использование и модификация.
