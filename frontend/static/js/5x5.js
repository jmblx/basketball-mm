var ws;
    var matchId;
    let is_captain_search;
    var myWorker;
    var userData;


    async function loadUserTeams(userId) {
        const response = await fetch(`http://localhost:8082/profile/user-teams?user_id=${userId}`, {
            method: 'GET'
        });

        if (response.ok) {
            const userTeams = await response.json();
            const teamSelect = document.getElementById('teamSelect');
            teamSelect.innerHTML = '';
            for (const teamId in userTeams) {
                const option = document.createElement('option');
                option.value = userTeams[teamId].team_id;
                option.textContent = userTeams[teamId].name;
                teamSelect.appendChild(option);
            }
            teamSelect.addEventListener('change', async function () {
                const selectedTeamId = teamSelect.value;
                const isCaptain = await checkCaptainship(userData.id, selectedTeamId);
                if (isCaptain) {
                    document.getElementById('captainSearch').style.display = 'block';
                } else {
                    document.getElementById('captainSearch').style.display = 'none';
                }
                // Вызываем startConnection после изменения команды
                await startConnection();
        });
        await startConnection();
        const initiallySelectedTeamId = teamSelect.value;
        const isCaptain = await checkCaptainship(userData.id, initiallySelectedTeamId);
        if (isCaptain) {
            document.getElementById('captainSearch').style.display = 'block';
        } else {
            document.getElementById('captainSearch').style.display = 'none';
        }
    }   else {
            console.error('Failed to fetch user teams.');
        }
    }


    async function checkCaptainship(userId, teamId) {
        const response = await fetch(`http://localhost:8082/team/check-captainship?user_id=${userId}&team_id=${teamId}`, {
            method: 'GET'
        });

        if (response.ok) {
            const result = await response.json();
            return result.isCaptain;
        } else {
            console.error('Failed to check captainship.');
            return false;
        }
    }

    async function getUserData() {
        const token = localStorage.getItem("auth_token");
        const response = await fetch('http://localhost:8082/profile/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            userData = await response.json();
            loadUserTeams(userData.id);
            return userData; // Возвращаем userData для дальнейшего использования
        } else {
            console.error('Failed to fetch user data.');
            return null; // Возвращаем null, если запрос не удался
        }
    }

    document.addEventListener('DOMContentLoaded', async (event) => {
        await getUserData(); // Дожидаемся выполнения асинхронной функции
        // После получения данных пользователя можно инициализировать SharedWorker и другие компоненты
        initializeWorkerAndUI();
    });

    function initializeWorkerAndUI() {
        if (window.SharedWorker) {
            myWorker = new SharedWorker('/static/js/shared-websocket-worker.js');
            myWorker.port.start();
            userId = userData.id
            myWorker.port.onmessage = function(e) {
                var data = JSON.parse(e.data);
                switch (data.action) {
                    case 'matchFound5x5Cap':
                    case 'matchFound5x5Mem':
                        matchId = Number(data.matchId);
                        document.getElementById('matchmakingStatus').textContent = `Match with ID ${data.matchId} found. Please confirm your readiness.`;
                        if (is_captain_search) {
                            document.getElementById('confirmReadyCaptain').style.display = 'block';
                            document.getElementById('notConfirmReadyCaptain').style.display = 'block';
                        }
                        else {
                            document.getElementById('confirmReadyPlayer').style.display = 'block';
                            document.getElementById('notConfirmReadyPlayer').style.display = 'block';
                        }
                        break;
                    case 'matchCancelled':
                        document.getElementById('matchmakingStatus').textContent = 'Match cancelled. Waiting for a new match...';
                        hideConfirmationButtons();
                        break;
                    case 'matchResearch':
                        document.getElementById('matchmakingStatus').textContent = 'Searching for a new match...';
                        break;
                    case 'matchStarted':
                        window.location = 'http://penis'
                        break;
                    default:
                        console.log('Unknown action:', data.action);
                }
            }
        };
    }

    function sendMessageToWorker(message) {
            myWorker.port.postMessage(JSON.stringify(message));
    }

    async function startConnection(){
        const userId = userData.id; // Обеспечиваем, что userData уже загружены
        const teamId = document.getElementById('teamSelect').value;
        if (!teamId) {
            console.error("Team ID is not selected.");
            return;
        }
        console.log("Starting connection with team ID:", teamId);
        console.log(userId)
        sendMessageToWorker({ action: "connect5x5", finderId: teamId, matchType: '5x5', userId: userId });
    }

    async function startMatchmaking(is_captain) {
        userId = userData.id
        is_captain_search = is_captain
        const teamId = document.getElementById('teamSelect').value;
        if (teamId) {
            sendMessageToWorker({ action: "startSearch", finderId: teamId, matchType: '5x5', userId: userId });
            document.getElementById('matchmakingStatus').textContent = 'Searching for a match...';
        }
        else {
            alert('Team ID is required to start matchmaking.');
        }
    }

    function confirmReadyPlayer() {
        let userId = userData.id
        if (matchId && userId) {
            sendMessageToWorker({ action: "confirmReadyPlayer", userId: userId, matchId: matchId, matchType: '5x5'});
        }
        hideConfirmationButtons();
    }

    function notConfirmReadyPlayer() {
        const teamId = document.getElementById('teamSelect').value;
        if (matchId && teamId) {
            sendMessageToWorker({ action: "notConfirmReadyPlayer", teamId: teamId, matchId: matchId, matchType: '5x5'});
        }
        hideConfirmationButtons()
    }

    function confirmReadyCaptain() {
        const teamId = document.getElementById('teamSelect').value;
        if (matchId) {
           sendMessageToWorker({ action: "confirmReadyCaptain", teamId: teamId, matchId: matchId, matchType: '5x5'});
        }
        hideConfirmationButtons();
    }

    function notConfirmReadyCaptain() {
        const teamId = document.getElementById('teamSelect').value;
        console.log('not conf 1')
        if (matchId){
            sendMessageToWorker({ action: "notConfirmReadyCaptain", teamId: teamId, matchId: matchId, matchType: '5x5'});
        }
        hideConfirmationButtons()
    }

    function hideConfirmationButtons() {
        document.getElementById('confirmReadyPlayer').style.display = 'none';
        document.getElementById('notConfirmReadyPlayer').style.display = 'none';
        document.getElementById('confirmReadyCaptain').style.display = 'none';
        document.getElementById('notConfirmReadyCaptain').style.display = 'none';
    }