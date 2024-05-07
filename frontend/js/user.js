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
    localStorage.removeItem('nickname')
    localStorage.removeItem('email')
    window.location.href = '../index.html';
}

function attemptUpload() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0]; // Получаем файл из input

    if (!file) {
        console.log('Файл не выбран.');
        return;
    }

    // Проверка размера файла (например, не больше 5MB)
    if (file.size > 5 * 1024 * 1024) {
        alert('Размер файла не должен превышать 5MB.');
        return;
    }

    // Проверка типа файла
    if (!file.type.startsWith('image/')) {
        alert('Пожалуйста, выберите изображение.');
        return;
    }

    // Вызов функции загрузки файла
    uploadFile(file);
}

async function uploadFile(file) {
    const url = `http://176.109.110.111/profile/uploadfile/avatar/${userId}`;

    const formData = new FormData();
    formData.append('avatar', file, file.name);

    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Не удалось загрузить файл: ' + response.statusText);
        }

        const result = await response.json();
        console.log('Файл успешно загружен:', result);
        alert('Файл успешно загружен!');
    } catch (error) {
        console.error('Ошибка при загрузке файла:', error);
        alert(error.message);
    }
}

