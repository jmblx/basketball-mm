async function getUserData() {
    const response = await fetch('http://127.0.0.1:8000/stats/top5-users-solo');
    const users = await response.json();
    updateCardsWithUserData(users);
}

function updateCardsWithUserData(usersData) {
    const userKeys = ['top1', 'top2', 'top3', 'top4', 'top5']; // Указываем порядок ключей

    userKeys.forEach(async (key) => {
        const user = usersData[key];
        if (user) {
            const userImageResponse = await fetch(`http://127.0.0.1:8000/profile/image/${user.id}`);
            const imgSrc = userImageResponse.url; // или другой способ получения URL изображения
            const userData = {
                imgSrc: imgSrc,
                title: user.nickname,
                rating: user.solo_rating,
                link: `http://localhost:8000/user/${user.nickname}`
            };
            header.appendChild(createCard(userData));
        }
    });
}

function createCard(data) {
    const container = document.createElement('div');
    container.className = 'container';
    container.innerHTML = `
        <div class="card">
            <img src="${data.imgSrc}" alt="Изображение игрока" class="image">
            <div class="card-title-nick">${data.title}</div>
            <div class="card-sub">РЕЙТИНГ:<br><span style="color: rgb(0, 47, 255)"><b>${data.rating}</b></span></br></div>
            <button onclick="document.location='${data.link}'" class="button">Просмотр</button>
        </div>
    `;
    return container;
}

document.addEventListener('DOMContentLoaded', getUserData);


window.onscroll = function() {scrollFunction()};

function scrollFunction() {
    var headerTop = document.querySelector(".header-top");
    if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50) {
        headerTop.style.padding = "10px 0";
        headerTop.style.fontSize = "30px";
    } else {
        headerTop.style.padding = "20px 0";
        headerTop.style.fontSize = "50px";
    }
}
