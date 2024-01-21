document.getElementById('registrationForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const formData = new FormData();
    formData.append('email', document.getElementById('email').value);
    formData.append('nickname', document.getElementById('nickname').value);
    formData.append('password', document.getElementById('password').value);
    formData.append('avatar', document.getElementById('avatar').files[0]);

    const response = await fetch('/register', { // Путь к вашему API регистрации
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('userToken', data.token); // Сохраняем токен
        localStorage.setItem('userData', JSON.stringify(data.user)); // Сохраняем данные пользователя

        // Перенаправляем пользователя
        window.location.href = '.\index.html'; // Укажите здесь URL вашей страницы профиля
    } else {
        alert('Registration failed');
    }
});


