<template>
  <div id="game-container">
    <div v-if="gameStore.gameState === 'countdown'" id="countdown-screen">
      <h1 class="display-1 fw-bold text-white animate__animated animate__zoomIn">{{ gameStore.countdownMessage }}</h1>
    </div>

    <div v-else-if="gameStore.gameState === 'question' && gameStore.currentQuestion" id="question-screen">
      <header class="game-header">
        <div class="timer-container">
            <div ref="timerBarRef" class="timer-bar"></div>
        </div>
        <div class="question-counter">{{ gameStore.currentQuestion.question_index }}/{{ gameStore.currentQuestion.total_questions }}</div>
      </header>
      <main class="game-body">
        <div class="question-card animate__animated animate__fadeInDown">
          <h2>{{ gameStore.currentQuestion.question }}</h2>
        </div>
      </main>
      <footer class="game-footer">
        <div class="choice-grid">
          <button v-for="(choice, index) in gameStore.currentQuestion.choices" 
                  :key="choice.id"
                  @click="handleAnswer(choice.id)"
                  :disabled="answerSubmitted"
                  :class="['choice-btn', choiceColors[index], { 'choice-selected': selectedChoiceId === choice.id, 'choice-disabled': answerSubmitted && selectedChoiceId !== choice.id }]">
            <div class="shape"><i :class="choiceIcons[index]"></i></div>
            <div class="text">{{ choice.text }}</div>
          </button>
        </div>
      </footer>
    </div>

    <div v-else-if="gameStore.gameState === 'scoreboard'" id="scoreboard-container" class="animate__animated animate__fadeIn">
      <div class="join-card" style="width: 90%; max-width: 800px;">
        <div class="p-4">
          <h1 class="display-3 text-dark">Oyun Bitti!</h1>
          <h2 class="mb-4">Skor Tablosu</h2>
          <div class="table-responsive">
            <table class="table table-striped table-hover">
              <thead class="table-dark">
                <tr>
                  <th>Sıra</th>
                  <th>Oyuncu</th>
                  <th>Puan</th>
                  <th>Doğru</th>
                  <th>Yanlış</th>
                </tr>
              </thead>
              <tbody id="scoreboard-body">
                <tr v-for="player in gameStore.scoreboard" :key="player.name">
                  <td>{{ medals[player.rank-1] || player.rank }}</td>
                  <td>{{ player.name }}</td>
                  <td>{{ player.score }}</td>
                  <td>{{ player.correct }}</td>
                  <td>{{ player.wrong }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <RouterLink to="/" class="btn btn-join mt-4">Ana Sayfaya Dön</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue';
import { useGameStore } from '@/stores/game';
import { RouterLink } from 'vue-router';

const gameStore = useGameStore();
const choiceColors = ['choice-red', 'choice-blue', 'choice-yellow', 'choice-green'];
const choiceIcons = ['fa-solid fa-triangle', 'fa-solid fa-diamond', 'fa-solid fa-circle', 'fa-solid fa-square'];
const medals = ['🥇', '🥈', '🥉'];
const answerSubmitted = ref(false);
const selectedChoiceId = ref(null);

// DÜZELTME: Zamanlayıcı çubuğunun DOM elementine erişmek için bir ref oluşturuyoruz.
const timerBarRef = ref(null);

onMounted(() => {
  gameStore.connectToGameSocket();
});

// DÜZELTME: Yeni soru geldiğinde zamanlayıcıyı sıfırlayan watch fonksiyonu
watch(() => gameStore.currentQuestion, (newQuestion) => {
  if (newQuestion && timerBarRef.value) {
    answerSubmitted.value = false;
    selectedChoiceId.value = null;

    const timerBar = timerBarRef.value;
    
    // Adım 1: Animasyonu anlık olarak kapat
    timerBar.style.transition = 'none';
    
    // Adım 2: Çubuğu anında başa (%100 genişliğe) al
    timerBar.style.width = '100%';

    // Adım 3: Tarayıcının bu değişiklikleri işlemesi için çok kısa bir an bekle (reflow)
    // Bu 'offsetWidth' hilesi, tarayıcıyı değişikliği fark etmeye zorlar.
    void timerBar.offsetWidth;

    // Adım 4: Animasyonu yeni süreyle tekrar aç ve hedef genişliği ayarla
    timerBar.style.transition = `width ${newQuestion.time_limit}s linear`;
    timerBar.style.width = '0%';
  }
});

function handleAnswer(choiceId) {
  answerSubmitted.value = true;
  selectedChoiceId.value = choiceId;
  gameStore.submitAnswer(choiceId);
}
</script>