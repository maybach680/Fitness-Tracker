<template>
  <div class="app">
    <!-- Навигация -->
    <nav class="nav-tabs container">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['nav-tab', { active: currentTab === tab.id }]"
        @click="currentTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </nav>

    <!-- Контент -->
    <main class="container">
      <!-- Питание -->
      <FoodDiary v-if="currentTab === 'nutrition'" />
      
      <!-- Тренировки -->
      <WorkoutLog v-else-if="currentTab === 'workouts'" />
      
      <!-- Прогресс -->
      <ProgressCharts v-else-if="currentTab === 'progress'" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FoodDiary from './components/FoodDiary.vue'
import WorkoutLog from './components/WorkoutLog.vue'
import ProgressCharts from './components/ProgressCharts.vue'

const tabs = [
  { id: 'nutrition', label: '🍽️ Питание' },
  { id: 'workouts', label: '💪 Тренировки' },
  { id: 'progress', label: '📈 Прогресс' }
]

const currentTab = ref('nutrition')
</script>

<style scoped>
.app {
  min-height: 100vh;
  padding-bottom: 20px;
}

.nav-tabs {
  padding-top: 16px;
  position: sticky;
  top: 0;
  background: var(--bg-color);
  z-index: 100;
}
</style>
