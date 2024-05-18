async function fetchUserProfile() {
    try {
        const response = await fetch('http://176.109.110.111/profile', {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('auth_token'),
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Ошибка запроса профиля: ${response.statusText}`);
        }

        const userData = await response.json();
        console.log('Данные профиля:', userData);
        displayUserProfile(userData);

    } catch (error) {
        console.error('Ошибка при получении данных профиля:', error);
    }
}

function displayUserProfile(userData) {
    console.log("ID пользователя:", userData.id);
    const nickname = userData.nickname
    document.getElementById('userNickname').textContent = nickname || 'Гость'
    console.log("Дата регистрации:", userData.registered_at);
    console.log("Соло рейтинг:", userData.rating);
    console.log("Групповой рейтинг:", userData.group_rating);
}

fetchUserProfile()
