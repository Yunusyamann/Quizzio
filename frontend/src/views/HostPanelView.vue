<template>
  <div class="d-flex justify-content-center align-items-center">
    <div v-if="isDialogVisible" class="dialog-overlay">
      <div class="dialog-box animate__animated animate__fadeInDown" :class="dialogStatus === 'success' ? 'dialog-success' : 'dialog-error'">
        <p class="dialog-message">{{ dialogMessage }}</p>
        <button @click="isDialogVisible = false" class="btn btn-light">Tamam</button>
      </div>
    </div>

    <div class="join-card text-center p-4 p-md-5">
      <h1 class="display-5 fw-bold">Quizzio Host Paneli</h1>
      <p class="lead">Hoş geldin, {{ gameStore.playerName }}!</p>
      <hr class="my-4">

      <div class="ai-section my-4">
        <h5>Yapay Zeka ile Soru Oluştur</h5>
        <p class="text-muted small">Oluşturmak istediğiniz soruların konusunu aşağıya yazın.</p>
        <form @submit.prevent="generateQuestions">
          <div class="form-floating mb-3">
            <textarea v-model="prompt" class="form-control" placeholder="Örn: Osmanlı Tarihi" id="ai-prompt" style="height: 100px" required></textarea>
            <label for="ai-prompt">Soru Konusu (Örn: Türkiye Coğrafyası)</label>
          </div>
          <button type.="submit" class="btn btn-success w-100" :disabled="isLoading">
            <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            {{ isLoading ? 'Oluşturuluyor...' : 'Soruları Oluştur' }}
          </button>
        </form>
        <div v-if="initialMessage" class="alert alert-info mt-3 small">
          {{ initialMessage }}
        </div>
      </div>
      
      <p>Soruları ve cevapları yönetmek veya yeni oyun başlatmak için aşağıdaki butonları kullanın.</p>
      
      <div class="d-grid gap-2 col-8 mx-auto mt-4">
        <a href="/admin/" class="btn btn-admin btn-lg" target="_blank">Admin Paneli (Manuel Kontrol)</a>
        <button @click="createSession" class="btn btn-join btn-lg">Yeni Oyun Odası Oluştur</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useGameStore } from '@/stores/game'
import { useRouter } from 'vue-router'
import { ref, onMounted, onUnmounted } from 'vue'

const gameStore = useGameStore()
const router = useRouter()
const prompt = ref('Türkiye\'nin gölleri ve nehirleri')
const isLoading = ref(false)
const initialMessage = ref('')

// Dialog için yeni state'ler
const isDialogVisible = ref(false)
const dialogMessage = ref('')
const dialogStatus = ref('success') // 'success' or 'error'

let notificationSocket = null;

onMounted(() => {
  // Bildirim WebSocket'ini aç
  const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
  notificationSocket = new WebSocket(`${wsScheme}://${window.location.host}/ws/notifications/`);

  notificationSocket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'notification') {
      dialogMessage.value = data.message;
      dialogStatus.value = data.status;
      isDialogVisible.value = true;
    }
  };
});

onUnmounted(() => {
  // Sayfadan ayrılırken bağlantıyı kapat
  if (notificationSocket) {
    notificationSocket.close();
  }
});

async function generateQuestions() {
  isLoading.value = true;
  initialMessage.value = '';

  const response = await fetch('/api/generate_questions/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt: prompt.value })
  });
  const data = await response.json();
  if (response.ok) {
    initialMessage.value = data.message;
  } else {
    initialMessage.value = data.error || 'Bir hata oluştu.';
  }
  isLoading.value = false;
}

async function createSession() {
  const response = await fetch('/api/create_session/')
  const data = await response.json()
  if (data.success) {
    gameStore.sessionCode = data.session_code
    router.push({ name: 'lobby', params: { sessionCode: data.session_code } })
  } else {
    alert('Oturum oluşturulurken bir hata oluştu.')
  }
}
</script>