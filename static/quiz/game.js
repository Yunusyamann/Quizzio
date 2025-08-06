// static/quiz/game.js

// DOM Elements
const countdownScreen = document.getElementById('countdown-screen');
const countdownMessage = document.getElementById('countdown-message');
const questionScreen = document.getElementById('question-screen');
const questionText = document.getElementById('question-text');
const choicesContainer = document.getElementById('choices-container');
const timerBar = document.getElementById('timer');
const scoreboardScreen = document.getElementById('scoreboard-screen');
const scoreboardBody = document.getElementById('scoreboard-body');

let currentQuestionId = null;
let timerInterval;

const gameSocket = new WebSocket(
    'ws://' + window.location.host + `/ws/game/${SESSION_ID}/${PLAYER_NAME}/`
);

gameSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const type = data.type;

    if (type === 'game.countdown') {
        showCountdown(data.message);
    } else if (type === 'new.question') {
        displayQuestion(data);
    } else if (type === 'show.scoreboard') {
        displayScoreboard(data.scoreboard);
    }
};

gameSocket.onclose = function(e) {
    console.error('Oyun bağlantısı beklenmedik şekilde kapandı.');
    alert('Bağlantı kesildi. Lütfen sayfayı yenileyin.');
};

function showCountdown(message) {
    countdownScreen.classList.remove('d-none');
    questionScreen.classList.add('d-none');
    scoreboardScreen.classList.add('d-none');
    countdownMessage.textContent = message;
    countdownMessage.classList.add('animate__animated', 'animate__zoomIn');
    
    // Animasyonu her seferinde tetiklemek için sınıfı kaldırıp ekle
    countdownMessage.addEventListener('animationend', () => {
        countdownMessage.classList.remove('animate__animated', 'animate__zoomIn');
    });
}

function displayQuestion(data) {
    clearInterval(timerInterval); // Önceki zamanlayıcıyı temizle

    currentQuestionId = data.question_id;
    countdownScreen.classList.add('d-none');
    scoreboardScreen.classList.add('d-none');
    questionScreen.classList.remove('d-none');

    questionText.textContent = data.question;
    choicesContainer.innerHTML = '';

    data.choices.forEach((choice, index) => {
        const choiceButton = document.createElement('div');
        choiceButton.className = 'col-md-6';
        choiceButton.innerHTML = `
            <button class="btn btn-outline-primary w-100 p-3 choice-btn" data-choice-id="${choice.id}">
                ${choice.text}
            </button>
        `;
        choicesContainer.appendChild(choiceButton);
    });

    document.querySelectorAll('.choice-btn').forEach(button => {
        button.addEventListener('click', submitAnswer);
    });

    startTimer(data.time_limit);
}

function startTimer(duration) {
    let timeLeft = duration;
    timerBar.style.width = '100%';
    timerBar.style.transition = `width ${duration}s linear`;
    
    // Animasyonu tetiklemek için küçük bir gecikme
    setTimeout(() => {
        timerBar.style.width = '0%';
    }, 100);
}


function submitAnswer(event) {
    const choiceId = event.target.dataset.choiceId;

    // Tüm butonları devre dışı bırak ve seçileni vurgula
    document.querySelectorAll('.choice-btn').forEach(btn => {
        btn.disabled = true;
        btn.classList.remove('btn-outline-primary');
        if (btn.dataset.choiceId === choiceId) {
            btn.classList.add('btn-primary'); // Seçileni mavi yap
        } else {
            btn.classList.add('btn-secondary'); // Diğerlerini gri yap
        }
    });

    gameSocket.send(JSON.stringify({
        'command': 'submit_answer',
        'question_id': currentQuestionId,
        'choice_id': choiceId,
        'player_name': PLAYER_NAME
    }));

    // Zamanlayıcıyı durdur
    clearInterval(timerInterval);
}

function displayScoreboard(scoreboard) {
    countdownScreen.classList.add('d-none');
    questionScreen.classList.add('d-none');
    scoreboardScreen.classList.remove('d-none');
    scoreboardScreen.classList.add('animate__animated', 'animate__fadeIn');

    scoreboardBody.innerHTML = '';
    scoreboard.forEach((player, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${player.name}</td>
            <td>${player.score}</td>
            <td>${player.correct}</td>
            <td>${player.wrong}</td>
        `;
        scoreboardBody.appendChild(row);
    });
}