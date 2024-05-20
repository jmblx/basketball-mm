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

        userData = await response.json();
        console.log('Данные профиля:', userData);
        displayUserProfile(userData);

    } catch (error) {
        console.error('Ошибка при получении данных профиля:', error);
    }
}

function displayUserProfile(userData) {
    console.log("ID пользователя:", userData.id);
    const nickname = userData.nickname;
    document.getElementById('userNickname').textContent = nickname || 'Гость';
    console.log("Дата регистрации:", userData.registered_at);
    console.log("Соло рейтинг:", userData.rating);
    console.log("Аватарка: ", userData.avatar_path);
    document.getElementById('userAvatar').src = userData.avatar_path
    console.log("Групповой рейтинг:", userData.group_rating);
}

fetchUserProfile();

function displaySavedEmail() {
    const savedEmail = localStorage.getItem('userEmail');
    const emailDisplayDiv = document.getElementById('userEmail');

    if (savedEmail) {
        emailDisplayDiv.textContent = savedEmail;
    } else {
        emailDisplayDiv.textContent = 'Вы не вошли или не зарегистрировались в системе';
    }
}

document.addEventListener('DOMContentLoaded', displaySavedEmail);
