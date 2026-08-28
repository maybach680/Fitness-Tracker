<template>
  <div class="food-diary">
    <!-- Статистика за сегодня -->
    <div class="card">
      <h2 class="card-title">Сегодня</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ Math.round(stats.calories) }}</div>
          <div class="stat-label">ккал</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ Math.round(stats.protein) }}г</div>
          <div class="stat-label">белки</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ Math.round(stats.fat) }}г</div>
          <div class="stat-label">жиры</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ Math.round(stats.carbs) }}г</div>
          <div class="stat-label">углеводы</div>
        </div>
      </div>
    </div>

    <!-- Поиск/сканирование продукта -->
    <div class="card">
      <h2 class="card-title">Добавить продукт</h2>
      
      <!-- Кнопка сканера -->
      <button class="btn btn-primary btn-block mb-2" @click="showScanner = true">
        📷 Сканировать штрихкод
      </button>
      
      <!-- Поиск по названию -->
      <div class="form-group">
        <input 
          v-model="searchQuery"
          @input="debouncedSearch"
          type="text" 
          class="form-input" 
          placeholder="Поиск по названию..."
        />
      </div>
      
      <!-- Результаты поиска -->
      <div v-if="searchResults.length > 0" class="search-results">
        <div 
          v-for="product in searchResults" 
          :key="product.barcode"
          class="log-item"
          @click="selectProduct(product)"
        >
          <div class="log-info">
            <div class="log-name">{{ product.name }}</div>
            <div class="log-details">
              {{ Math.round(product.calories_per_100g) }} ккал | 
              Б:{{ Math.round(product.protein_per_100g) }} Ж:{{ Math.round(product.fat_per_100g) }} У:{{ Math.round(product.carbs_per_100g) }}
            </div>
          </div>
          <span class="btn btn-sm btn-outline">+</span>
        </div>
      </div>
      
      <!-- Кнопка ручного добавления -->
      <button class="btn btn-outline btn-block mt-2" @click="showManualForm = true">
        ➕ Добавить вручную
      </button>
    </div>

    <!-- Список приёмов пищи -->
    <div class="card">
      <h2 class="card-title">Приёмы пищи сегодня</h2>
      
      <div v-if="store.foodLogs.length === 0" class="text-center text-muted">
        Нет записей за сегодня
      </div>
      
      <ul v-else class="log-list">
        <li v-for="log in store.foodLogs" :key="log.id" class="log-item">
          <div class="log-info">
            <div class="log-name">{{ log.product?.name || 'Продукт' }}</div>
            <div class="log-details">
              {{ log.meal_type }} • {{ log.grams }}г • 
              {{ Math.round(log.calories) }} ккал
            </div>
          </div>
          <div class="log-actions">
            <button class="btn btn-sm btn-danger" @click="deleteLog(log.id)">✕</button>
          </div>
        </li>
      </ul>
    </div>

    <!-- Модальное окно сканера -->
    <div v-if="showScanner" class="modal-overlay" @click.self="showScanner = false">
      <div class="modal">
        <h3 class="modal-title">Сканирование штрихкода</h3>
        <BarcodeScanner @scanned="handleScan" @close="showScanner = false" />
      </div>
    </div>

    <!-- Модальное окно ручного добавления -->
    <div v-if="showManualForm" class="modal-overlay" @click.self="showManualForm = false">
      <div class="modal">
        <h3 class="modal-title">Добавить продукт вручную</h3>
        <form @submit.prevent="addManualProduct">
          <div class="form-group">
            <label class="form-label">Штрихкод</label>
            <input v-model="manualProduct.barcode" type="text" class="form-input" required />
          </div>
          <div class="form-group">
            <label class="form-label">Название</label>
            <input v-model="manualProduct.name" type="text" class="form-input" required />
          </div>
          <div class="grid grid-2">
            <div class="form-group">
              <label class="form-label">Ккал/100г</label>
              <input v-model.number="manualProduct.calories_per_100g" type="number" step="0.1" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Белки (г)</label>
              <input v-model.number="manualProduct.protein_per_100g" type="number" step="0.1" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Жиры (г)</label>
              <input v-model.number="manualProduct.fat_per_100g" type="number" step="0.1" class="form-input" />
            </div>
            <div class="form-group">
              <label class="form-label">Углеводы (г)</label>
              <input v-model.number="manualProduct.carbs_per_100g" type="number" step="0.1" class="form-input" />
            </div>
          </div>
          <button type="submit" class="btn btn-primary btn-block">Сохранить</button>
          <button type="button" class="btn btn-outline btn-block mt-2" @click="showManualForm = false">Отмена</button>
        </form>
      </div>
    </div>

    <!-- Модальное окно добавления в дневник -->
    <div v-if="selectedProduct" class="modal-overlay" @click.self="selectedProduct = null">
      <div class="modal">
        <h3 class="modal-title">{{ selectedProduct.name }}</h3>
        <form @submit.prevent="addToDiary">
          <div class="form-group">
            <label class="form-label">Тип приёма</label>
            <select v-model="diaryEntry.meal_type" class="form-select">
              <option value="breakfast">Завтрак</option>
              <option value="lunch">Обед</option>
              <option value="dinner">Ужин</option>
              <option value="snack">Перекус</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Вес (граммы)</label>
            <input v-model.number="diaryEntry.grams" type="number" min="1" class="form-input" required />
          </div>
          <div class="stats-grid mb-2">
            <div class="stat-card">
              <div class="stat-value">{{ Math.round(calculatedCalories) }}</div>
              <div class="stat-label">ккал</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ Math.round(calculatedProtein) }}г</div>
              <div class="stat-label">белки</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ Math.round(calculatedFat) }}г</div>
              <div class="stat-label">жиры</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ Math.round(calculatedCarbs) }}г</div>
              <div class="stat-label">углеводы</div>
            </div>
          </div>
          <button type="submit" class="btn btn-primary btn-block">Добавить</button>
          <button type="button" class="btn btn-outline btn-block mt-2" @click="selectedProduct = null">Отмена</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTrackerStore } from '../stores/tracker'
import BarcodeScanner from './BarcodeScanner.vue'

const store = useTrackerStore()

// Состояние
const searchQuery = ref('')
const searchResults = ref([])
const selectedProduct = ref(null)
const showScanner = ref(false)
const showManualForm = ref(false)
const manualProduct = ref({
  barcode: '',
  name: '',
  calories_per_100g: 0,
  protein_per_100g: 0,
  fat_per_100g: 0,
  carbs_per_100g: 0
})
const diaryEntry = ref({
  meal_type: 'lunch',
  grams: 100
})

let searchTimeout = null

// Статистика за сегодня
const stats = computed(() => store.todayStats)

// Расчёт КБЖУ для выбранной граммовки
const calculatedCalories = computed(() => {
  if (!selectedProduct.value) return 0
  return (selectedProduct.value.calories_per_100g * diaryEntry.value.grams) / 100
})

const calculatedProtein = computed(() => {
  if (!selectedProduct.value) return 0
  return (selectedProduct.value.protein_per_100g * diaryEntry.value.grams) / 100
})

const calculatedFat = computed(() => {
  if (!selectedProduct.value) return 0
  return (selectedProduct.value.fat_per_100g * diaryEntry.value.grams) / 100
})

const calculatedCarbs = computed(() => {
  if (!selectedProduct.value) return 0
  return (selectedProduct.value.carbs_per_100g * diaryEntry.value.grams) / 100
})

// Дебаунс поиска
function debouncedSearch() {
  clearTimeout(searchTimeout)
  if (searchQuery.value.length >= 2) {
    searchTimeout = setTimeout(async () => {
      searchResults.value = await store.searchProducts(searchQuery.value)
    }, 300)
  } else {
    searchResults.value = []
  }
}

// Выбор продукта
function selectProduct(product) {
  selectedProduct.value = product
  diaryEntry.value = { meal_type: 'lunch', grams: 100 }
}

// Обработка сканирования
async function handleScan(barcode) {
  showScanner.value = false
  try {
    const result = await store.getProductByBarcode(barcode)
    selectProduct(result.product)
  } catch (e) {
    alert('Продукт не найден. Добавьте вручную.')
  }
}

// Добавление в дневник
async function addToDiary() {
  if (!selectedProduct.value) return
  
  await store.addFoodLog({
    product_id: selectedProduct.value.id,
    date: new Date().toISOString().split('T')[0],
    meal_type: diaryEntry.value.meal_type,
    grams: diaryEntry.value.grams
  })
  
  selectedProduct.value = null
  searchResults.value = []
  searchQuery.value = ''
}

// Ручное добавление продукта
async function addManualProduct() {
  try {
    await store.createProduct(manualProduct.value)
    showManualForm.value = false
    manualProduct.value = {
      barcode: '',
      name: '',
      calories_per_100g: 0,
      protein_per_100g: 0,
      fat_per_100g: 0,
      carbs_per_100g: 0
    }
  } catch (e) {
    alert('Ошибка: ' + e.message)
  }
}

// Удаление записи
async function deleteLog(id) {
  if (confirm('Удалить запись?')) {
    await store.removeFoodLog(id)
  }
}

// Загрузка данных при монтировании
onMounted(() => {
  const today = new Date().toISOString().split('T')[0]
  store.loadFoodLogs(today)
})
</script>

<style scoped>
.search-results {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  margin-top: 8px;
}

.log-item {
  cursor: pointer;
}

.log-item:hover {
  background: var(--bg-color);
}
</style>
