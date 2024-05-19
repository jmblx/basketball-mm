var ws;
var clients = [];
var wsReady = false;

function closeCurrentConnection() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
    }
}

async function startWebSocket(objectId, matchType, teamId) {

    closeCurrentConnection();
    return new Promise((resolve, reject) => {
        teamId = teamId || null
        console.log("connecting")
        let team_info;
        if (teamId != null) {
            teamInfo = `&teamid=${teamId}`
        }
        else {
            teamInfo = ''
        }
        console.log(`176.109.110.111/finding-match/${matchType}/ws?userid=${objectId}${teamInfo}`)
        ws = new WebSocket(`ws://176.109.110.111/finding-match/${matchType}/ws?userid=${objectId}${teamInfo}`);
        console.log('connected')
        console.log(objectId);
        ws.onopen = function() {
            wsReady = true;
            resolve();
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
            reject(error);
        };
    });
}

function confirmReady1x1(userId, matchId) {
    console.log(matchId);
    if (matchId && userId) {
        fetch(`http://176.109.110.111/finding-match/1x1/confirm_ready/${matchId}/${userId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === 'confirmed') {
                    document.getElementById('matchmakingStatus').textContent = 'You confirmed the match.';
                }
            });
    }
}

function notConfirmReady1x1(userId, matchId) {
    if (matchId && userId) {
        fetch(`http://176.109.110.111/finding-match/1x1/not_ready/${matchId}/${userId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === 'search restarted for opposing user') {
                    document.getElementById('matchmakingStatus').textContent = 'Match declined.';
                }
            });
    }
}

function confirmReadyPlayer(matchId, userId) {
    console.log(userId)
    console.log(matchId)
    if (matchId && userId) {
        fetch(`http://176.109.110.111/finding-match/5x5/player/confirm_ready/${matchId}/${userId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === 'confirmed') {
                    document.getElementById('matchmakingStatus').textContent = 'Вы приняли матч';
                }
            });
    }
}

function notConfirmReadyPlayer(matchId, teamId) {
    if (matchId && teamId) {
        fetch(`http://176.109.110.111/finding-match/5x5/player/not_ready/${matchId}/${teamId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === 'search restarted for opposing team') {
                    document.getElementById('matchmakingStatus').textContent = 'Матч отклонен';
                }
            });
    }
}

function confirmReadyCaptain(matchId, teamId) {
    if (matchId) {
        fetch(`http://176.109.110.111/finding-match/5x5/captain/confirm_ready/${matchId}/${teamId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === 'confirmed') {
                    document.getElementById('matchmakingStatus').textContent = 'You confirmed the match.';
                }
            });
    }
}

function notConfirmReadyCaptain(matchId, teamId) {
    if (matchId && teamId) {
        fetch(`http://176.109.110.111/finding-match/5x5/captain/not_ready/${matchId}/${teamId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (data.status === 'search restarted for opposing team') {
                    document.getElementById('matchmakingStatus').textContent = 'Match declined.';
                }
            });
    }
}

function matchStarted() {
    window.location = 'http://176.109.110.111/templates/match'
}

async function startFindingMatch(objectId, matchType) {
    console.log(`http://176.109.110.111/finding-match/${matchType}/start_search/${objectId}`);
    if (objectId && wsReady) {
        console.log("zapros bil");
        const response = await fetch(`http://176.109.110.111/finding-match/${matchType}/start_search/${objectId}`, {
            method: 'POST'
        });
        if (response.ok) {
            console.log('Поиск нового матча...');
        }
        else {
            alert('Не удалось начать матч');
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
        console.log("data");
        console.log(data);
        finderId = data.finderId
        userId = data.userId
        matchId = data.matchId
        matchType = data.matchType
        teamId = data.teamId
        console.log(data.action)
        if (matchType === '1x1') {
            switch (data.action) {
                case 'startSearch':
                    console.log("case")
                    if (finderId) {
                        console.log("finderId")
                        console.log(finderId)
                        if (!ws || !wsReady) {
                            console.log("!ws || !wsReady")
                            try {
                                console.log("trying to connect")
                                await startWebSocket(finderId, matchType, null);
                                console.log(finderId)
                                console.log(matchType)
                                startFindingMatch(finderId, matchType);
                            } catch (error) {
                                console.log('Не удалось установить WebSocket соединение:', error);
                            }
                        } else if (ws && wsReady) {
                            startFindingMatch(finderId, matchType);
                        }
                    }
                    break;

                case 'confirmReady':
                    confirmReady1x1(finderId, matchId)
                    break;
                case 'notConfirmReady':
                    notConfirmReady1x1(finderId, matchId)
                    break;
            }
        }
        else {
            switch (data.action) {
                case 'connect5x5':
                    await startWebSocket(userId, matchType, finderId);
                    break;
                case 'startSearch':
                    if (finderId) {
                        if (!ws || !wsReady) {
                            try {
                                await startWebSocket(userId, matchType, finderId);
                                startFindingMatch(finderId, matchType);
                            } catch (error) {
                                console.log('Не удалось установить WebSocket соединение:', error);
                            }
                        } else if (ws && wsReady) {
                            startFindingMatch(finderId, matchType);
                        }
                    }
                    break;
                case 'confirmReadyPlayer':
                    confirmReadyPlayer(matchId, userId)
                    break;
                case 'notConfirmReadyPlayer':
                    notConfirmReadyPlayer(matchId, teamId)
                    break;
                case 'confirmReadyCaptain':
                    console.log("222")
                    confirmReadyCaptain(matchId, teamId)
                    break;
                case 'notConfirmReadyCaptain':
                    console.log("dsdasd")
                    notConfirmReadyCaptain(matchId, teamId)
                    break;
                case 'matchStarted':
                    matchStarted()
            }
        }
    };

    port.start();
};
