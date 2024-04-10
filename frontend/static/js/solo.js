 var matchId;
        var userData;

        async function getUserData() {
            const token = localStorage.getItem("auth_token");
            const response = await fetch('/profile/', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                userData = await response.json();
            }
            else {
                console.error('Failed to fetch user data.');
            }
        }

        if (window.SharedWorker) {
            var myWorker = new SharedWorker('/static/js/shared-websocket-worker.js');
            myWorker.port.start();
            myWorker.port.onmessage = function(e) {
                var data = JSON.parse(e.data);
                switch (data.action) {
                    case 'matchFound':
                        console.log(data.matchID)
                        matchId = Number(data.matchId);
                        document.getElementById('matchmakingStatus').textContent = `Match with ID ${data.matchId} found. Please confirm your readiness.`;
                        document.getElementById('confirmReady').style.display = 'block';
                        document.getElementById('notConfirm').style.display = 'block';
                        break;
                    case 'matchCancelled':
                        document.getElementById('matchmakingStatus').textContent = 'Match cancelled. Waiting for a new match...';
                        hideConfirmationButtons();
                        break;
                    case 'matchResearch':
                        document.getElementById('matchmakingStatus').textContent = 'Searching for a new match...';
                        break;
                    case 'matchStarted':
                        document.getElementById('matchmakingStatus').textContent = 'Match is starting...';
                        break;
                    default:
                        console.log('Unknown action:', data.action);
                }
            }
        };


        function sendMessageToWorker(message) {
                myWorker.port.postMessage(JSON.stringify(message));
        }

        function startMatchmaking() {
            if (userData && userData.id) {
                console.log(userData.id)
                sendMessageToWorker({ action: "startSearch", finderId: userData.id, matchType: '1x1' });
                document.getElementById('matchmakingStatus').textContent = 'Searching for a match...';
            }
            else {
                alert('User ID is required to start matchmaking.');
            }
        }

        function hideConfirmationButtons() {
            document.getElementById('confirmReady').style.display = 'none';
            document.getElementById('notConfirm').style.display = 'none';
        }

        function confirmReady() {
            if (matchId && userData && userData.id) {
                sendMessageToWorker({ action: "confirmReady", matchId: matchId, finderId: userData.id, matchType: '1x1' });
                hideConfirmationButtons();
            }
        }

        function notConfirmReady() {
            if (matchId && userData && userData.id) {
                sendMessageToWorker({ action: "notConfirmReady", matchId: matchId, finderId: userData.id, matchType: '1x1' });
                hideConfirmationButtons();
            }
        }

        document.addEventListener('DOMContentLoaded', (event) => {
            getUserData();
        });