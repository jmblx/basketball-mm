var ws;
var clients = [];
var wsReady = false; // Флаг готовности WebSocket

async function startWebSocket(userId) {
    return new Promise((resolve, reject) => {
        ws = new WebSocket(`ws://localhost:8000/finding-match/1x1/ws?userid=${userId}`);

        ws.onopen = function() {
            wsReady = true;
            resolve(); // WebSocket готов
        };

        ws.onmessage = function(event) {
            clients.forEach(client => {
                client.postMessage(event.data);
            });
        };

        ws.onclose = function() {
            console.log('WebSocket closed. Trying to reconnect...');
            wsReady = false;
        };

        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
            wsReady = false;
            reject(error); // Ошибка WebSocket
        };
    });
}

function confirmReady(userId, matchId) {
    console.log(matchId);
    if (matchId && userId) {
        fetch(`http://localhost:8000/finding-match/1x1/confirm_ready/${matchId}/${userId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === 'confirmed') {
                    document.getElementById('matchmakingStatus').textContent = 'You confirmed the match.';
                }
            });
    }
}

function notConfirmReady(userId, matchId) {
    if (matchId && userId) {
        fetch(`/finding-match/1x1/not_ready/${matchId}/${userId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === 'search restarted for opposing user') {
                    document.getElementById('matchmakingStatus').textContent = 'Match declined.';
                }
            });
    }
}

async function startFindingMatch(userId) {
    if (userId && wsReady) {
        const response = await fetch(`http://localhost:8000/finding-match/1x1/start_search/${userId}`, {
            method: 'POST'
        });
        if (response.ok) {
            // Обработка успешного начала поиска
            console.log('Searching for a match...');
        } else {
            alert('Failed to start matchmaking.');
        }
    } else {
        console.log('WebSocket не готов или отсутствует ID пользователя.');
    }
}

self.onconnect = function(e) {
    var port = e.ports[0];
    clients.push(port);
    port.onmessage = async function(event) {
        var data = JSON.parse(event.data);
        userId = data.userId
        matchId = data.matchId
        switch (data.action) {
            case 'startSearch':
                if (userId) {
                    // Попытка установить соединение, если оно ещё не установлено
                    if (!ws || !wsReady) {
                        try {
                            await startWebSocket(userId);
                            startFindingMatch(userId);
                        } catch (error) {
                            console.log('Не удалось установить WebSocket соединение:', error);
                        }
                    } else if (ws && wsReady) {
                        startFindingMatch(userId);
                    }
                }
                break;

            case 'confirmReady':
                confirmReady(userId, matchId)
                break;
            case 'notConfirmReady':
                notConfirmReady(userId, matchId)
                break;
        }
    };

    port.start();
};
