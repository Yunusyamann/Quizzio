<template>
  <div class="d-flex justify-content-center align-items-center">
    <div class="d-flex justify-content-center align-items-center">
    <div class="join-card text-center p-4 p-md-5">
      <h1 class="display-5 fw-bold mb-4">Quizzio Host Girişi</h1>
      </div>
  </div>
    <div class="join-card text-center p-4 p-md-5">
  
      <form @submit.prevent="handleLogin">
        <div class="form-floating mb-3">
          <input type="text" class="form-control" id="username" placeholder="yunus" v-model="username" required>
          <label for="username">Kullanıcı Adı</label>
        </div>
        <div class="form-floating mb-3">
          <input type="password" class="form-control" id="password" placeholder="Şifre" v-model="password" required>
          <label for="password">Şifre</label>
        </div>
        <p v-if="error" class="text-danger">{{ error }}</p>
        <button class="btn btn-join w-100 btn-lg" type="submit">Giriş Yap</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'

const username = ref('yunus')
const password = ref('')
const error = ref(null)
const router = useRouter()
const gameStore = useGameStore()

async function handleLogin() {
  error.value = null
  try {
    const response = await fetch('/api/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, password: password.value })
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Giriş yapılamadı.');
    }
    // Pinia store'da host bilgilerini set et
    gameStore.isHost = true;
    gameStore.playerName = data.username;
    router.push({ name: 'host' });
  } catch (err) {
    error.value = err.message;
  }
}
</script>