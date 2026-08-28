import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const productsApi = {
  // Поиск по штрихкоду в локальной БД
  getByBarcode(barcode) {
    return api.get('/products', { params: { barcode } }).then(r => r.data[0])
  },
  
  // Поиск по названию в локальной БД
  search(query) {
    return api.get('/products/search', { params: { q: query } }).then(r => r.data)
  },
  
  // Получить из Open Food Facts
  getFromOFF(barcode) {
    return api.get(`/products/off/barcode/${barcode}`)
  },
  
  // Поиск в Open Food Facts
  searchOFF(query) {
    return api.get('/products/off/search', { params: { q: query } }).then(r => r.data)
  },
  
  // Создать продукт вручную
  create(product) {
    return api.post('/products', product).then(r => r.data)
  },
  
  // Все продукты
  getAll(limit = 100) {
    return api.get('/products', { params: { limit } }).then(r => r.data)
  },
}

export const foodLogApi = {
  // Получить за дату
  getByDate(dateStr) {
    return api.get('/food-log', { params: { date_str: dateStr } }).then(r => r.data)
  },
  
  // Статистика за период
  getStats(start, end) {
    return api.get('/food-log/stats', { params: { start, end } }).then(r => r.data)
  },
  
  // Добавить запись
  create(entry) {
    return api.post('/food-log', entry).then(r => r.data)
  },
  
  // Удалить запись
  delete(id) {
    return api.delete(`/food-log/${id}`)
  },
}

export const exercisesApi = {
  getAll() {
    return api.get('/exercises').then(r => r.data)
  },
  
  create(exercise) {
    return api.post('/exercises', exercise).then(r => r.data)
  },
  
  delete(id) {
    return api.delete(`/exercises/${id}`)
  },
}

export const workoutsApi = {
  // Получить за период
  getRange(start, end) {
    return api.get('/workouts', { params: { start, end } }).then(r => r.data)
  },
  
  // Добавить тренировку
  create(workout) {
    return api.post('/workouts', workout).then(r => r.data)
  },
  
  // Обновить тренировку
  update(id, data) {
    return api.put(`/workouts/${id}`, data).then(r => r.data)
  },
  
  // Удалить тренировку
  delete(id) {
    return api.delete(`/workouts/${id}`)
  },
  
  // Heatmap данные
  getHeatmap(year) {
    return api.get('/workouts/heatmap', { params: { year } }).then(r => r.data)
  },
  
  // Прогресс данные
  getProgress(start, end) {
    return api.get('/workouts/progress', { params: { start, end } }).then(r => r.data)
  },
}

export default api
