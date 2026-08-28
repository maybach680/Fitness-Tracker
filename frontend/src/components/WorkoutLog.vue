<template>
  <div class="workout-log">
    <!-- Добавление тренировки -->
    <div class="card">
      <h2 class="card-title">Добавить тренировку</h2>
      
      <form @submit.prevent="addWorkout">
        <div class="form-group">
          <label class="form-label">Упражнение</label>
          <div class="flex">
            <select v-model="newWorkout.exercise_id" class="form-select" required>
              <option :value="null" disabled>Выберите упражнение</option>
              <option v-for="ex in store.exercises" :key="ex.id" :value="ex.id">
                {{ ex.name }}
              </option>
            </select>
            <button type="button" class="btn btn-secondary" @click="showExerciseForm = true">+</button>
          </div>
        </div>
        
        <div class="grid grid-2">
          <div class="form-group">
            <label class="form-label">Дата</label>
            <input v-model="newWorkout.date" type="datetime-local" class="form-input" required />
          </div>
          <div class="form-group">
            <label class="form-label">Подходы</label>
            <input v-model.number="newWorkout.sets" type="number" min="1" class="form-input" />
          </div>
        </div>
        
        <div class="grid grid-3">
          <div class="form-group">
            <label class="form-label">Повторения</label>
            <input v-model.number="newWorkout.reps" type="number" min="1" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">Вес (кг)</label>
            <input v-model.number="newWorkout.weight_kg" type="number" step="0.5" min="0" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">Длительность (мин)</label>
            <input v-model.number="newWorkout.duration_minutes" type="number" min="0" class="form-input" />
          </div>
        </div>
        
        <div class="form-group">
          <label class="form-label">Калории (опционально)</label>
          <input v-model.number="newWorkout.calories_burned" type="number" min="0" class="form-input" />
        </div>
        
        <button type="submit" class="btn btn-primary btn-block">Добавить тренировку</button>
      </form>
    </div>

    <!-- Heatmap календарь -->
    <div class="card">
      <h2 class="card-title">Активность за {{ currentYear }}</h2>
      <div class="heatmap-container">
        <div class="heatmap-months">
          <span v-for="(month, i) in months" :key="i" :style="{ gridColumnStart: month.start }" class="heatmap-month">
            {{ month.name }}
          </span>
        </div>
        <div class="heatmap">
          <div 
            v-for="day in yearDays" 
            :key="day.date"
            :class="['heatmap-cell', 'level-' + getLevel(day.date)]"
            :title="`${day.date}: ${day.value || 0}`"
          ></div>
        </div>
      </div>
      <div class="flex mt-2 text-muted" style="font-size: 12px;">
        <span>Меньше</span>
        <div class="heatmap-cell level-0"></div>
        <div class="heatmap-cell level-1"></div>
        <div class="heatmap-cell level-2"></div>
        <div class="heatmap-cell level-3"></div>
        <div class="heatmap-cell level-4"></div>
        <span>Больше</span>
      </div>
    </div>

    <!-- Список тренировок -->
    <div class="card">
      <h2 class="card-title">История тренировок</h2>
      
      <div v-if="store.workouts.length === 0" class="text-center text-muted">
        Нет записей за выбранный период
      </div>
      
      <ul v-else class="log-list">
        <li v-for="workout in store.workouts" :key="workout.id" class="log-item">
          <div class="log-info">
            <div class="log-name">{{ workout.exercise?.name || 'Упражнение' }}</div>
            <div class="log-details">
              {{ formatDate(workout.date) }} • 
              {{ workout.sets }}×{{ workout.reps }} × {{ workout.weight_kg }}кг •
              {{ workout.duration_minutes }} мин
            </div>
          </div>
          <div class="log-actions">
            <button class="btn btn-sm btn-danger" @click="deleteWorkout(workout.id)">✕</button>
          </div>
        </li>
      </ul>
    </div>

    <!-- Модальное окно добавления упражнения -->
    <div v-if="showExerciseForm" class="modal-overlay" @click.self="showExerciseForm = false">
      <div class="modal">
        <h3 class="modal-title">Новое упражнение</h3>
        <form @submit.prevent="createExercise">
          <div class="form-group">
            <label class="form-label">Название</label>
            <input v-model="newExerciseName" type="text" class="form-input" placeholder="Приседания" required />
          </div>
          <button type="submit" class="btn btn-primary btn-block">Создать</button>
          <button type="button" class="btn btn-outline btn-block mt-2" @click="showExerciseForm = false">Отмена</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTrackerStore } from '../stores/tracker'

const store = useTrackerStore()

const showExerciseForm = ref(false)
const newExerciseName = ref('')
const currentYear = ref(new Date().getFullYear())

const newWorkout = ref({
  exercise_id: null,
  date: new Date().toISOString().slice(0, 16),
  sets: 3,
  reps: 10,
  weight_kg: 0,
  duration_minutes: 30,
  calories_burned: 0
})

// Месяцы для heatmap
const months = [
  { name: 'Янв', start: 1 },
  { name: 'Фев', start: 5 },
  { name: 'Мар', start: 9 },
  { name: 'Апр', start: 14 },
  { name: 'Май', start: 18 },
  { name: 'Июн', start: 23 },
  { name: 'Июл', start: 27 },
  { name: 'Авг', start: 32 },
  { name: 'Сен', start: 36 },
  { name: 'Окт', start: 40 },
  { name: 'Ноя', start: 45 },
  { name: 'Дек', start: 49 }
]

// Дни года для heatmap
const yearDays = computed(() => {
  const days = []
  const year = currentYear.value
  const startDate = new Date(year, 0, 1)
  
  // Определяем день недели первого дня года (0 = Вс, 1 = Пн, ...)
  let startDay = startDate.getDay()
  // Корректируем для начала с понедельника
  startDay = startDay === 0 ? 6 : startDay - 1
  
  for (let i = 0; i < 371; i++) { // 53 недели * 7 дней
    const currentDate = new Date(startDate)
    currentDate.setDate(startDate.getDate() + i - startDay)
    
    if (currentDate.getFullYear() === year) {
      days.push({
        date: currentDate.toISOString().split('T')[0],
        value: 0
      })
    } else {
      days.push({ date: currentDate.toISOString().split('T')[0], value: null })
    }
  }
  
  // Заполняем значения из heatmap данных
  store.heatmapData.forEach(h => {
    const day = days.find(d => d.date === h.date)
    if (day) day.value = h.value
  })
  
  return days
})

// Получение уровня интенсивности
function getLevel(dateStr) {
  const day = store.heatmapData.find(h => h.date === dateStr)
  return day ? day.level : 0
}

// Форматирование даты
function formatDate(dateStr) {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

// Добавление упражнения
async function createExercise() {
  if (newExerciseName.value.trim()) {
    await store.createExercise(newExerciseName.value.trim())
    newExerciseName.value = ''
    showExerciseForm.value = false
  }
}

// Добавление тренировки
async function addWorkout() {
  if (!newWorkout.value.exercise_id) {
    alert('Выберите упражнение')
    return
  }
  
  await store.addWorkout({
    ...newWorkout.value,
    date: new Date(newWorkout.value.date).toISOString()
  })
  
  // Сброс формы
  newWorkout.value = {
    exercise_id: null,
    date: new Date().toISOString().slice(0, 16),
    sets: 3,
    reps: 10,
    weight_kg: 0,
    duration_minutes: 30,
    calories_burned: 0
  }
}

// Удаление тренировки
async function deleteWorkout(id) {
  if (confirm('Удалить запись о тренировке?')) {
    await store.workoutsApi.delete(id)
    await store.loadWorkouts(
      new Date().toISOString().split('T')[0],
      new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
    )
  }
}

onMounted(async () => {
  await store.loadExercises()
  await store.loadHeatmap(currentYear.value)
  
  const today = new Date().toISOString().split('T')[0]
  const future = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  await store.loadWorkouts(today, future)
})
</script>

<style scoped>
.heatmap-container {
  padding: 10px 0;
}

.heatmap-months {
  margin-bottom: 4px;
}

.heatmap-month {
  font-size: 10px;
  color: var(--text-light);
}
</style>
