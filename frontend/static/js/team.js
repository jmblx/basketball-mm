var teamSlug = new URL(window.location.href).pathname.split("/").pop();
        var teamId;
        var teamData;
        var participants;
        var userId;
        var userData;
        var originalTeamName;
        var originalIsCaptainOnlySearch;
        var matchId;

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
                userId = userData.id;
            }
            else {
                console.error('токена чела нет');
            }
        }

        var myWorker;
        function sendMessageToWorker(message) {
            myWorker.port.postMessage(JSON.stringify(message));
        }

       if (window.SharedWorker) {
            myWorker = new SharedWorker('/static/js/shared-websocket-worker.js');
            myWorker.port.start();

            myWorker.port.onmessage = function(e) {
                var data = JSON.parse(e.data);
                matchId = data.matchId;
                switch (data.action) {
                    case 'matchFound':
                        resetMatchButtons();
                        document.getElementById('matchInvitation').style.display = 'block';  // Это гарантирует, что контейнер становится видимым
                        break;
                    case 'matchFound5x5Cap':
                        console.log('5x5 Match for captain found:', data.matchId);
                        console.log(document.getElementById('acceptMatch').dataset.role)
                        document.getElementById('acceptMatch').dataset.role = 'captain';
                        document.getElementById('declineMatch').dataset.role = 'captain';
                        document.getElementById('matchInvitation').style.display = 'block';
                        break;
                    case 'matchFound5x5Mem':
                        console.log('5x5 Match for member found:', data.matchId);
                        document.getElementById('acceptMatch').dataset.role = 'member';
                        document.getElementById('declineMatch').dataset.role = 'member';
                        document.getElementById('matchInvitation').style.display = 'block';
                        break;
                }
            };

            function sendMessageToWorker(message) {
                if (myWorker) {
                    myWorker.port.postMessage(JSON.stringify(message));
                }
            }

            function resetMatchButtons() {
                console.log(document.getElementById('acceptMatch'))
                document.getElementById('acceptMatch').dataset.role = '';
                document.getElementById('declineMatch').dataset.role = '';
                document.getElementById('acceptMatch').style.display = 'none';
                document.getElementById('declineMatch').style.display = 'none';
            }

            document.getElementById('acceptMatch').addEventListener('click', function() {
                const role = this.dataset.role;
                const action = role === 'captain' ? 'confirmReadyCaptain' : role === 'member' ? 'confirmReadyPlayer' : 'confirmReady';
                sendMessageToWorker({ action: action, matchId: matchId, userId: userData.id, teamId: teamId });
                resetMatchButtons();
            });

            document.getElementById('declineMatch').addEventListener('click', function() {
                const role = this.dataset.role;
                const action = role === 'captain' ? 'notConfirmReadyCaptain' : role === 'member' ? 'notConfirmReadyPlayer' : 'notConfirmReady';
                sendMessageToWorker({ action: action, matchId: matchId, userId: userData.id, teamId: teamId });
                resetMatchButtons();
            });
       }

        function checkUserInTeam() {
            if (participants && userId) {
                const userIsInTeam = participants.some(member => member.id === userId);
                if (userIsInTeam) {
                    document.getElementById('joinTeamButton').style.display = "none";
                    document.getElementById('leaveTeamButton').style.display = ""; // Показываем кнопку выхода
                } else {
                    document.getElementById('leaveTeamButton').style.display = "none";
                }
            }
            if (userId && teamData && userId !== teamData.team_captain_id) {
                document.getElementById('renameTeamButton').style.display = 'none';
                document.getElementById('newTeamName').style.display = 'none';
                document.getElementById('saveChangesButton').style.display = 'none';
                document.getElementById('isCaptainOnlySearch').disabled = true;
            }
        }


        async function getTeamData() {
            const response = await fetch(`http://localhost:8082/team/data/${teamSlug}`);
            if (response.ok) {
                data = await response.json(); // Получаем данные
                teamData = data;
                teamId = data.team_id;
                originalTeamName = data.team_name;
                originalIsCaptainOnlySearch = data.is_captain_only_search;
                document.getElementById('teamName').textContent = data.team_name;
                document.getElementById('teamCaptain').textContent = "Капитан: " + data.team_captain_nickname;
                document.getElementById('teamNumber').textContent = "Участники: " + data.number;
                document.getElementById('isCaptainOnlySearch').checked = data.is_captain_only_search;
                participants = data.participants;
                updateTeamMembers(data.participants);
                getTeamImage();
            } else {
                console.error('Ошибка при получении данных о команде');
            }
        }

        function updateTeamMembers(members) {
            const membersList = document.getElementById('membersList');
            members.forEach(member => {
                let listItem = document.createElement('li');
                listItem.textContent = member.nickname + ' (рейтинг: ' + member.group_rating + ')';
                membersList.appendChild(listItem);
            });
        }

        async function getTeamImage() {
            fetch(`http://localhost:8082/team/image/${teamId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Сетевой запрос не удался');
                }
                return response.blob();
            })
            .then(blob => {
                const imageUrl = URL.createObjectURL(blob);
                document.getElementById('teamImage').src = imageUrl;
            })
            .catch(error => {
                console.error('Произошла ошибка при выполнении запроса:', error);
                alert('Ошибка при загрузке изображения');
            });
        }

        async function joinTeam() {
            const token = localStorage.getItem("auth_token");
            const response = await fetch(`http://localhost:8082/team/join-team?team_id=${teamId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                alert('Вы успешно присоединились к команде!');
                document.getElementById('joinTeamButton').style.display = "none"
                const newMember = { id: userId, nickname: userData.nickname, group_rating: userData.group_rating};
                participants.push(newMember);
                updateTeamMembersList();
            } else {
                alert('Ошибка при попытке присоединиться к команде');
            }
        }

        function updateTeamMembersList() {
            const membersList = document.getElementById('membersList');
            membersList.innerHTML = '';
            updateTeamMembers(participants);
        }


        async function renameTeam() {
            const newName = prompt("Введите новое название команды:", originalTeamName);
            if (newName !== null && newName !== "") {
                document.getElementById('teamName').textContent = newName;
                document.getElementById('newTeamName').value = newName;
                document.getElementById('newTeamName').style.display = "";

                updateSaveChangesButtonVisibility();
            }
        }

        async function saveChanges() {
            const newTeamName = document.getElementById('newTeamName').value;
            const newIsCaptainOnlySearch = document.getElementById('isCaptainOnlySearch').checked;

            const changes = {};
            if (newTeamName !== originalTeamName && newTeamName !== "") {
                changes.name = newTeamName;
            }
            if (newIsCaptainOnlySearch !== originalIsCaptainOnlySearch) {
                changes.is_captain_only_search = newIsCaptainOnlySearch;
            }
            console.log(changes)
            const token = localStorage.getItem("auth_token");
            const response = await fetch(`http://localhost:8082/team/update/${teamId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(changes)
            });

            if (response.ok) {
                alert('Изменения сохранены успешно!');
                document.getElementById('newTeamName').style.display = "none";
                document.getElementById('saveChangesButton').style.display = "none";

                if (changes.name) {
                    originalTeamName = changes.name;
                }
                if (changes.is_captain_only_search !== null) {
                    originalIsCaptainOnlySearch = changes.is_captain_only_search;
                }

                updateSaveChangesButtonVisibility();
            } else {
                alert('Ошибка при сохранении изменений');
            }
        }

        function updateSaveChangesButtonVisibility() {
            const newTeamName = document.getElementById('newTeamName').value;
            const newIsCaptainOnlySearch = document.getElementById('isCaptainOnlySearch').checked;

            if (newTeamName === originalTeamName && newIsCaptainOnlySearch === originalIsCaptainOnlySearch) {
                document.getElementById('saveChangesButton').style.display = "none";
            } else {

                document.getElementById('saveChangesButton').style.display = "";
            }
        }

        document.getElementById('isCaptainOnlySearch').addEventListener('change', updateSaveChangesButtonVisibility);

        document.addEventListener('DOMContentLoaded', async () => {
            await Promise.all([getUserData(), getTeamData()]);
            checkUserInTeam();
            document.getElementById('saveChangesButton').addEventListener('click', saveChanges);
            document.getElementById('renameTeamButton').addEventListener('click', renameTeam);
        });

        async function leaveTeam() {
            const token = localStorage.getItem("auth_token");
            const response = await fetch(`http://localhost:8082/team/leave-team?team_id=${teamId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                alert('Вы покинули команду.');
                document.getElementById('leaveTeamButton').style.display = "none";
                const index = participants.findIndex(member => member.id === userId);
                if (index > -1) {
                    participants.splice(index, 1); // Удаляем пользователя из списка участников
                    updateTeamMembersList(); // Обновляем список участников на странице
                }
            } else {
                alert('Ошибка при попытке покинуть команду.');
            }
        }