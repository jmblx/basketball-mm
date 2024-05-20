let userData = null;

document.addEventListener('DOMContentLoaded', function() {
    const nickname = localStorage.getItem('nickname');
    document.getElementById('userNickname').textContent = nickname || 'Гость';
});

document.addEventListener('DOMContentLoaded', function() {
    const userEmail = localStorage.getItem('email');
    if (userEmail) {
        document.getElementById('userEmail').textContent = userEmail;
    }
});

function logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('nickname');
    localStorage.removeItem('userEmail');
    window.location.href = 'http://176.109.110.111/templates/index.html';
}

function attemptUpload() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        console.log('Файл не выбран.');
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        alert('Размер файла не должен превышать 5MB.');
        return;
    }

    if (!file.type.startsWith('image/')) {
        alert('Пожалуйста, выберите изображение.');
        return;
    }

    uploadFile(file);
}

async function uploadFile(file) {
    if (!file) {
        console.error('Файл не выбран или не передан.');
        return;
    }

    if (!userData || !userData.id) {
        console.error('Данные пользователя не загружены или отсутствует ID пользователя.');
        return;
    }

    const url = `http://176.109.110.111/profile/uploadfile/avatar/${userData.id}`;

    const formData = new FormData();
    formData.append('file', file, file.name);

    console.log('Отправка данных на сервер:');
    console.log('URL:', url);
    console.log('Файл:', file);
    console.log('FormData:', ...formData.entries());

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error('Не удалось загрузить файл: ' + response.statusText + ' - ' + errorText);
        }

        const result = await response.json();
        console.log('Файл успешно загружен:', result);
        alert('Файл успешно загружен!');

        document.getElementById('userAvatar').src = `http://176.109.110.111/profile/image/${userData.id}`;

    } catch (error) {
        console.error('Ошибка при загрузке файла:', error);
        alert(error.message);
    }
}
