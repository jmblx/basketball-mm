async function register(email, password, name) {
    try {
        console.log(email, password, name)
        const registerResponse = await fetch('http://176.109.110.111/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password,
                nickname: name,
                role_id: 1,
                pathfile: "string",
                is_active: true,
                is_superuser: false,
                is_verified: false,
            })
        });

        if (!registerResponse.ok) {
            throw new Error(`Ошибка регистрации: ${registerResponse.statusText}`);
        }

        const registerData = await registerResponse.json();
        localStorage.setItem("nickname", registerData.nickname);
        localStorage.setItem("email", registerData.email);

        return await login(email, password);
    } catch (error) {
        console.error('Ошибка:', error);
        throw error;
    }
}

function validateEmail(email) {
    const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

function validatePassword(password) {
    return password.length >= 8;
}

document.getElementById('regForm').addEventListener('submit', async (event) => {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const name = document.getElementById('nickname').value;

    if (!validateEmail(email)) {
        alert("Введите корректный email адрес");
        return;
    }
    if (!validatePassword(password)) {
        alert('Пароль должен содержать как минимум 8 символов.');
        return;
    }

    try {
        await register(email, password, name);
        console.log('Успешная регистрация и вход');
        window.location.href = "../index.html"
    } catch (error) {
        console.error('Ошибка при регистрации и входе:', error);
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const nickname = localStorage.getItem('nickname');
    document.getElementById('userNickname').textContent = nickname || 'Гость';
});

fetchUserProfile()
