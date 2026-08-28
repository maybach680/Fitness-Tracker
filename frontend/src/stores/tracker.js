import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { productsApi, foodLogApi, exercisesApi, workoutsApi } from '../utils/api'

export const useTrackerStore = defineStore('tracker', () => {
  // Состояние
  const products = ref([])
  const foodLogs = ref([])
  const exercises = ref([])
  const workouts = ref([])
  const heatmapData = ref([])
  const progressData = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Вычисляемые свойства для статистики за сегодня
  const todayStats = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    const todayLogs = foodLogs.value.filter(log => log.date === today)
    
    return {
      calories: todayLogs.reduce((sum, log) => sum + log.calories, 0),
      protein: todayLogs.reduce((sum, log) => sum + log.protein, 0),
      fat: todayLogs.reduce((sum, log) => sum + log.fat, 0),
      carbs: todayLogs.reduce((sum, log) => sum + log.carbs, 0),
      mealsCount: todayLogs.length
    }
  })

  // ===== Продукты =====
  async function searchProducts(query) {
    if (query.length < 2) return []
    loading.value = true
    try {
      const results = await productsApi.search(query)
      return results
    } catch (e) {
      error.value = e.message
      return []
    } finally {
      loading.value = false
    }
  }

  async function getProductByBarcode(barcode) {
    loading.value = true
    try {
      // Сначала ищем в локальной БД
      let product = await productsApi.getByBarcode(barcode)
      if (product) return { product, cached: true }
      
      // Если не найдено, запрашиваем из Open Food Facts
      const response = await productsApi.getFromOFF(barcode)
      product = response.data
      
      // Сохраняем в локальную БД
      const savedProduct = await productsApi.create(product)
      return { product: savedProduct, cached: false }
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createProduct(product) {
    loading.value = true
    try {
      const result = await productsApi.create(product)
      products.value.push(result)
      return result
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  // ===== Дневник питания =====
  async function loadFoodLogs(dateStr) {
    loading.value = true
    try {
      foodLogs.value = await foodLogApi.getByDate(dateStr)
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function addFoodLog(entry) {
    loading.value = true
    try {
      const result = await foodLogApi.create(entry)
      foodLogs.value.unshift(result)
      return result
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function removeFoodLog(id) {
    try {
      await foodLogApi.delete(id)
      foodLogs.value = foodLogs.value.filter(log => log.id !== id)
    } catch (e) {
      error.value = e.message
      throw e
    }
  }

  // ===== Упражнения =====
  async function loadExercises() {
    loading.value = true
    try {
      exercises.value = await exercisesApi.getAll()
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function createExercise(name) {
    loading.value = true
    try {
      const result = await exercisesApi.create({ name })
      exercises.value.push(result)
      return result
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  // ===== Тренировки =====
  async function loadWorkouts(start, end) {
    loading.value = true
    try {
      workouts.value = await workoutsApi.getRange(start, end)
    } catch (e) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function addWorkout(workout) {
    loading.value = true
    try {
      const result = await workoutsApi.create(workout)
      workouts.value.unshift(result)
      return result
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function loadHeatmap(year) {
    try {
      heatmapData.value = await workoutsApi.getHeatmap(year)
    } catch (e) {
      error.value = e.message
    }
  }

  async function loadProgress(start, end) {
    try {
      progressData.value = await workoutsApi.getProgress(start, end)
    } catch (e) {
      error.value = e.message
    }
  }

  return {
    // State
    products,
    foodLogs,
    exercises,
    workouts,
    heatmapData,
    progressData,
    loading,
    error,
    
    // Computed
    todayStats,
    
    // Actions
    searchProducts,
    getProductByBarcode,
    createProduct,
    loadFoodLogs,
    addFoodLog,
    removeFoodLog,
    loadExercises,
    createExercise,
    loadWorkouts,
    addWorkout,
    loadHeatmap,
    loadProgress
  }
})
