document.getElementById('regForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const loginData = await login(email, password); // Сохраняем результат функции login
        console.log('Успешный вход', loginData);
        window.location.href = "../index.html";
    } catch (error) {
        console.error('Ошибка при регистрации и входе:', error);
    }
});

async function login(email, password) {
    try {
        const loginResponse = await fetch('http://176.109.110.111/auth/jwt/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
        });

        if (!loginResponse.ok) {
            if (loginResponse.status === 404) {
                alert("Пользователь не найден")
                throw new Error("Пользователь не найден");
            } else if (loginResponse.status === 401) {
                alert("Неверный пароль")
                throw new Error("Неверный пароль");
            } else {
                throw new Error("Ошибка входа");
            }
        }

        const loginData = await loginResponse.json();
        localStorage.setItem("auth_token", loginData.access_token);

        return loginData;

    } catch (error) {
        console.error('Ошибка:', error);
        throw error;
    }
}
