document.getElementById('teamForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const teamName = document.getElementById('teamName').value; // Получаем название команды из поля ввода
    if (!teamName) {
        alert('Пожалуйста, введите название команды.');
        return;
    }

    try {
        const response = await fetch('http://176.109.110.111/team/add-new-team', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('auth_token') // Предполагаем, что токен хранится в localStorage
            },
            body: JSON.stringify({
                name: teamName,
                pathfile: "string"
            })
        });

        if (!response.ok) {
            const errorDetails = await response.json();
            throw new Error(`Ошибка при создании команды: ${errorDetails.message}`);
        }

        const result = await response.json();
        console.log('Команда успешно создана:', result);

        createTeamCard(teamName);

        document.getElementById('teamName').value = '';

        localStorage.setItem('createdTeam', JSON.stringify(result));

    } catch (error) {
        console.error('Ошибка:', error.message);
        alert('Не удалось создать команду: ' + error.message);
    }
});

function createTeamCard(teamName) {
    const card = document.createElement('div');
    card.className = 'team-card';
    card.textContent = teamName;
    card.style.border = '1px solid #ccc';
    card.style.borderRadius = '5px';
    card.style.padding = '10px';
    card.style.marginTop = '10px';
    card.style.backgroundColor = '#f9f9f9';
    document.body.appendChild(card);
}
