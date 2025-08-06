// static/quiz/lobby.js

const playerList = document.getElementById('player-list');
const startGameBtn = document.getElementById('start-game-btn');

const lobbySocket = new WebSocket(
    'ws://' + window.location.host + '/ws/lobby/' + SESSION_ID + '/'
);

lobbySocket.onopen = function(e) {
    console.log("Lobi bağlantısı kuruldu.");
    // Host değilse ve adı varsa, lobiye katılım mesajı gönder
    const playerName = localStorage.getItem('playerName');
    if (!IS_HOST && playerName) {
        lobbySocket.send(JSON.stringify({
            'command': 'join_lobby',
            'player_name': playerName
        }));
        localStorage.removeItem('playerName'); // kullandıktan sonra temizle
    } else if (IS_HOST) {
        // Host da kendi adıyla katılsın
         lobbySocket.send(JSON.stringify({
            'command': 'join_lobby',
            'player_name': HOST_NAME + " (Host)"
        }));
    }
};

lobbySocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const type = data.type;

    if (type === 'player.update') {
        updatePlayerList(data.players);
    } else if (type === 'game.start') {
        // Oyuncunun adını URL'ye ekleyerek oyun sayfasına yönlendir
        const playerNameFromList = Array.from(playerList.children).find(li => li.textContent.includes(localStorage.getItem('savedPlayerName') || document.getElementById('player-name-input')?.value))?.textContent || HOST_NAME + " (Host)";
        const cleanPlayerName = playerNameFromList.replace(' (Host)', '').trim();
        window.location.pathname = `/game/${SESSION_ID}/${cleanPlayerName}/`;
    }
};

lobbySocket.onclose = function(e) {
    console.error('Lobi bağlantısı kapandı.');
};

function updatePlayerList(players) {
    playerList.innerHTML = '';
    players.forEach(player => {
        const li = document.createElement('li');
        li.className = 'list-group-item animate__animated animate__fadeIn';
        li.textContent = player.name;
        playerList.appendChild(li);
    });
}

if (IS_HOST && startGameBtn) {
    startGameBtn.addEventListener('click', function() {
        lobbySocket.send(JSON.stringify({
            'command': 'start_game'
        }));
    });
}

// Sayfa yüklendiğinde oyuncu adını sakla (eğer host değilse)
window.onload = () => {
    if (!IS_HOST) {
        const storedName = localStorage.getItem('playerName');
        if (storedName) {
            localStorage.setItem('savedPlayerName', storedName);
        }
    }
};