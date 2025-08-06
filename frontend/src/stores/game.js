import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '@/router'

export const useGameStore = defineStore('game', () => {
  // State
  const sessionCode = ref(null)
  const playerName = ref(null)
  const isHost = ref(false)
  const players = ref([])
  const gameState = ref('connecting') // connecting, countdown, question, scoreboard
  const countdownMessage = ref('')
  const currentQuestion = ref(null)
  const scoreboard = ref(null)

  let lobbySocket = null
  let gameSocket = null

  // Actions
  function connectToLobbySocket() {
    if (lobbySocket) lobbySocket.close()

    const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
    lobbySocket = new WebSocket(
      `${wsScheme}://${window.location.host}/ws/lobby/${sessionCode.value}/`
    )

    lobbySocket.onopen = () => {
      console.log('Lobby WebSocket connected.')
      lobbySocket.send(JSON.stringify({
        command: 'join_lobby',
        player_name: isHost.value ? `${playerName.value} (Host)` : playerName.value
      }))
    }

    lobbySocket.onmessage = (e) => {
      const data = JSON.parse(e.data)
      if (data.type === 'player.update') {
        players.value = data.players
      } else if (data.type === 'game.start') {
        router.push({ name: 'game', params: { sessionCode: sessionCode.value } })
      }
    }

    lobbySocket.onclose = () => console.log('Lobby WebSocket disconnected.')
    lobbySocket.onerror = (err) => console.error('Lobby WebSocket error:', err)
  }

  function connectToGameSocket() {
    if (gameSocket) gameSocket.close()

    const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
    gameSocket = new WebSocket(
      `${wsScheme}://${window.location.host}/ws/game/${sessionCode.value}/${playerName.value}/`
    )

    gameSocket.onopen = () => console.log('Game WebSocket connected.')
    
    gameSocket.onmessage = (e) => {
      const data = JSON.parse(e.data)
      switch(data.type) {
        case 'game.countdown':
          gameState.value = 'countdown'
          countdownMessage.value = data.message
          break;
        case 'new.question':
          gameState.value = 'question'
          currentQuestion.value = data
          break;
        case 'show.scoreboard':
          gameState.value = 'scoreboard'
          scoreboard.value = data.scoreboard
          break;
      }
    }
  }

  function startGame() {
    if (lobbySocket) {
      lobbySocket.send(JSON.stringify({ command: 'start_game' }))
    }
  }
  
  function submitAnswer(choiceId) {
    if (gameSocket && currentQuestion.value) {
      gameSocket.send(JSON.stringify({
        command: 'submit_answer',
        question_id: currentQuestion.value.question_id,
        choice_id: choiceId
      }))
    }
  }

  function resetState() {
    sessionCode.value = null
    playerName.value = null
    isHost.value = false
    players.value = []
    gameState.value = 'connecting'
    if (lobbySocket) lobbySocket.close()
    if (gameSocket) gameSocket.close()
  }

  return { 
    sessionCode, playerName, isHost, players, gameState, countdownMessage, 
    currentQuestion, scoreboard, connectToLobbySocket, connectToGameSocket, 
    startGame, submitAnswer, resetState 
  }
})