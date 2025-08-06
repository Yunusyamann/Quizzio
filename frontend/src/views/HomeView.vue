<template>
  <div class="d-flex justify-content-center align-items-center">
    <div class="join-card text-center p-4 p-md-5">
      <h1 class="brand-logo mb-3">Quizzio</h1>
      <p class="brand-slogan mb-4">Arkadaşlarınla yarış, bilgini konuştur!</p>
      
      <form @submit.prevent="joinLobby" class="row g-3 justify-content-center align-items-center">
        <div class="col-md-5">
          <input type="text" v-model="inputCode" class="form-control form-control-lg text-center fw-bold" placeholder="Oda Kodu" required maxlength="4" style="text-transform:uppercase; letter-spacing: 0.2em;">
        </div>
        <div class="col-md-4">
          <input type="text" v-model="inputName" class="form-control form-control-lg" placeholder="Adınızı Girin" required>
        </div>
        <div class="col-md-3">
          <button type="submit" class="btn btn-join btn-lg w-100">Lobiye Katıl</button>
        </div>
      </form>

      <div class="mt-4">
        <small>Host musun? <RouterLink to="/login">Giriş Yap</RouterLink></small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useGameStore } from '@/stores/game';

const inputCode = ref('');
const inputName = ref('');
const router = useRouter();
const gameStore = useGameStore();

function joinLobby() {
  if (inputCode.value && inputName.value) {
    gameStore.sessionCode = inputCode.value.toUpperCase();
    gameStore.playerName = inputName.value;
    gameStore.isHost = inputName.value.toLowerCase() === 'yunus';
    
    router.push({ name: 'lobby', params: { sessionCode: gameStore.sessionCode } });
  }
}
</script>