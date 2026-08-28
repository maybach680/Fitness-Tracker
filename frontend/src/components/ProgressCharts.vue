<template>
  <div class="progress-charts">
    <!-- Графики -->
    <div class="grid grid-2">
      <!-- Калории по дням -->
      <div class="card">
        <h2 class="card-title">Калории</h2>
        <LineChart 
          v-if="caloriesData.labels.length"
          :data="caloriesData" 
          :options="chartOptions"
        />
        <div v-else class="text-center text-muted">Нет данных</div>
      </div>
      
      <!-- БЖУ по дням -->
      <div class="card">
        <h2 class="card-title">БЖУ</h2>
        <BarChart 
          v-if="macrosData.labels.length"
          :data="macrosData" 
          :options="chartOptions"
        />
        <div v-else class="text-center text-muted">Нет данных</div>
      </div>
    </div>
    
    <!-- Тренировки -->
    <div class="card">
      <h2 class="card-title">Объём тренировок</h2>
      <LineChart 
        v-if="workoutData.labels.length"
        :data="workoutData" 
        :options="chartOptions"
      />
      <div v-else class="text-center text-muted">Нет данных</div>
    </div>
    
    <!-- Период -->
    <div class="card">
      <h2 class="card-title">Период</h2>
      <div class="flex">
        <input v-model="startDate" type="date" class="form-input" @change="loadData" />
        <span>—</span>
        <input v-model="endDate" type="date" class="form-input" @change="loadData" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { LineChart, BarChart } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { useTrackerStore } from '../stores/tracker'

// Регистрируем компоненты Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

const store = useTrackerStore()

// Даты периода
const endDate = ref(new Date().toISOString().split('T')[0])
const startDate = ref(new Date(Date.now() - 29 * 24 * 60 * 60 * 1000).toISOString().split('T')[0])

// Опции графиков
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top'
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

// Данные для графика калорий
const caloriesData = computed(() => {
  const labels = store.progressData.map(d => {
    const date = new Date(d.date)
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  })
  
  const calories = store.progressData.map(d => d.calories || 0)
  
  return {
    labels,
    datasets: [{
      label: 'ккал',
      data: calories,
      borderColor: '#4CAF50',
      backgroundColor: 'rgba(76, 175, 80, 0.1)',
      fill: true,
      tension: 0.3
    }]
  }
})

// Данные для графика БЖУ
const macrosData = computed(() => {
  const labels = store.progressData.map(d => {
    const date = new Date(d.date)
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  })
  
  return {
    labels,
    datasets: [
      {
        label: 'Белки',
        data: store.progressData.map(d => d.protein || 0),
        backgroundColor: '#2196F3'
      },
      {
        label: 'Жиры',
        data: store.progressData.map(d => d.fat || 0),
        backgroundColor: '#FF9800'
      },
      {
        label: 'Углеводы',
        data: store.progressData.map(d => d.carbs || 0),
        backgroundColor: '#9C27B0'
      }
    ]
  }
})

// Данные для графика тренировок
const workoutData = computed(() => {
  const labels = store.progressData.map(d => {
    const date = new Date(d.date)
    return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
  })
  
  return {
    labels,
    datasets: [{
      label: 'Длительность (мин)',
      data: store.progressData.map(d => d.workout_duration || 0),
      borderColor: '#E91E63',
      backgroundColor: 'rgba(233, 30, 99, 0.1)',
      fill: true,
      tension: 0.3
    }]
  }
})

// Загрузка данных
async function loadData() {
  await store.loadProgress(startDate.value, endDate.value)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.progress-charts {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card {
  min-height: 300px;
}

.chart-container {
  position: relative;
  height: 250px;
}
</style>
