<template>
  <div class="barcode-scanner">
    <div v-if="error" class="error text-center text-muted">
      {{ error }}
    </div>
    
    <div v-else class="scanner-container">
      <video ref="videoRef" class="scanner-video" autoplay playsinline></video>
      <div class="scanner-overlay"></div>
    </div>
    
    <div class="flex mt-2">
      <button class="btn btn-primary" @click="startScanner">
        {{ isScanning ? 'Перезапустить' : 'Запустить камеру' }}
      </button>
      <button class="btn btn-outline" @click="$emit('close')">
        Закрыть
      </button>
    </div>
    
    <!-- Ручной ввод штрихкода -->
    <div class="form-group mt-2">
      <label class="form-label">Или введите штрихкод вручную</label>
      <div class="flex">
        <input 
          v-model="manualBarcode" 
          type="text" 
          class="form-input" 
          placeholder="13 цифр EAN-13"
          maxlength="13"
        />
        <button class="btn btn-secondary" @click="submitManualBarcode">OK</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import Quagga from 'quagga'

const emit = defineEmits(['scanned', 'close'])

const videoRef = ref(null)
const isScanning = ref(false)
const error = ref('')
const manualBarcode = ref('')

let quaggaInstance = null

// Запуск сканера
async function startScanner() {
  error.value = ''
  
  try {
    // Останавливаем предыдущий экземпляр если есть
    if (quaggaInstance) {
      Quagga.stop()
    }
    
    // Инициализируем Quagga
    const result = await Quagga.init({
      inputStream: {
        name: 'Live',
        type: 'LiveStream',
        target: videoRef.value,
        constraints: {
          facingMode: 'environment', // Используем заднюю камеру
          width: { min: 640 },
          height: { min: 480 }
        }
      },
      decoder: {
        readers: ['ean_reader', 'ean_8_reader', 'upc_reader'],
        multiple: false
      },
      locator: {
        patchSize: 'medium',
        halfSample: true
      },
      numOfWorkers: 2,
      frequency: 10
    })
    
    if (!result) {
      throw new Error('Не удалось инициализировать камеру')
    }
    
    Quagga.start()
    isScanning.value = true
    
    // Обработка успешного сканирования
    Quagga.onDetected(handleDetection)
    
  } catch (e) {
    console.error('Scanner error:', e)
    error.value = 'Ошибка камеры. Проверьте разрешения.'
    isScanning.value = false
  }
}

// Обработка обнаруженного штрихкода
function handleDetection(result) {
  const code = result.codeResult?.code
  
  if (code && isValidBarcode(code)) {
    // Виброотклик (если поддерживается)
    if (navigator.vibrate) {
      navigator.vibrate(200)
    }
    
    emit('scanned', code)
    Quagga.stop()
    isScanning.value = false
  }
}

// Проверка валидности штрихкода
function isValidBarcode(code) {
  // EAN-13: 13 цифр
  if (/^\d{13}$/.test(code)) {
    return validateEAN13(code)
  }
  // EAN-8: 8 цифр
  if (/^\d{8}$/.test(code)) {
    return validateEAN8(code)
  }
  return false
}

// Валидация контрольной суммы EAN-13
function validateEAN13(code) {
  let sum = 0
  for (let i = 0; i < 12; i++) {
    sum += parseInt(code[i]) * (i % 2 === 0 ? 1 : 3)
  }
  const checkDigit = (10 - (sum % 10)) % 10
  return checkDigit === parseInt(code[12])
}

// Валидация контрольной суммы EAN-8
function validateEAN8(code) {
  let sum = 0
  for (let i = 0; i < 7; i++) {
    sum += parseInt(code[i]) * (i % 2 === 0 ? 3 : 1)
  }
  const checkDigit = (10 - (sum % 10)) % 10
  return checkDigit === parseInt(code[7])
}

// Ручной ввод штрихкода
function submitManualBarcode() {
  if (manualBarcode.value && isValidBarcode(manualBarcode.value)) {
    emit('scanned', manualBarcode.value)
    manualBarcode.value = ''
  } else {
    alert('Неверный формат штрихкода. Должно быть 13 или 8 цифр.')
  }
}

onMounted(() => {
  startScanner()
})

onBeforeUnmount(() => {
  if (quaggaInstance) {
    Quagga.stop()
  }
})
</script>

<style scoped>
.barcode-scanner {
  text-align: center;
}

.scanner-container {
  position: relative;
  background: #000;
  border-radius: var(--radius);
  overflow: hidden;
}

.scanner-video {
  display: block;
  width: 100%;
  max-height: 400px;
  object-fit: cover;
}

.scanner-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 70%;
  height: 120px;
  border: 3px solid var(--primary-color);
  border-radius: var(--radius);
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5);
  pointer-events: none;
}

.error {
  padding: 20px;
  color: var(--danger-color);
}
</style>
