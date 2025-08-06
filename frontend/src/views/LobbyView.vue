<template>
  <div class="d-flex justify-content-center align-items-center">
    <div class="join-card text-center p-4 p-md-5">
      <h1 class="display-5 fw-bold">Lobi</h1>
      <p class="lead mb-2">Host: <strong>{{ gameStore.isHost ? gameStore.playerName : '...' }}</strong></p>
      <p class="mb-3">Oda Kodu: <br> <input type="text" :value="gameStore.sessionCode" class="form-control text-center my-2 fs-4 fw-bold" readonly style="letter-spacing: 0.2em;"></p>
      
      <div class="card player-list-card mt-4">
        <div class="card-header">
          Oyuncular ({{ gameStore.players.length }})
        </div>
        <ul class="list-group list-group-flush" id="player-list">
          <li v-for="player in gameStore.players" :key="player.name" class="list-group-item">
            {{ player.name }}
          </li>
        </ul>
      </div>

      <button v-if="gameStore.isHost" @click="gameStore.startGame" class="btn btn-join btn-lg mt-4 w-100 animate__animated animate__pulse animate__infinite">Oyunu Başlat</button>
      <p v-else class="mt-4">Host'un oyunu başlatması bekleniyor...</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useGameStore } from '@/stores/game'

const gameStore = useGameStore()

onMounted(() => {
  if (!gameStore.sessionCode || !gameStore.playerName) {
    // Eğer state yoksa, kullanıcıyı ana sayfaya yönlendir
    router.push({ name: 'home' })
  } else {
    gameStore.connectToLobbySocket()
  }
})
</script>