async function getUserData() {
    const response = await fetch('http://127.0.0.1:8000/stats/top5-users-solo');
    const users = await response.json();
    updateCardsWithUserData(users);
}

async function getUserData() {
    const response = await fetch('http://127.0.0.1:8000/stats/top5-users-solo');
    const users = await response.json();

    // Сортируем пользователей так, чтобы топ 1 был посередине
    const sortedUsers = [users.top4, users.top2, users.top1, users.top3, users.top5];

    sortedUsers.forEach(async (user, index) => {
        if (user) {
            const userImageResponse = await fetch(`http://127.0.0.1:8000/profile/image/${user.id}`);
            const imgSrc = userImageResponse.url;
            const userData = {
                top: index === 2 ? 'top1' : '', // Указываем, что это топ 1
                imgSrc: imgSrc,
                title: user.nickname,
                rating: user.solo_rating,
                link: `http://localhost:8000/user/${user.nickname}`,
            };
            header.appendChild(createCard(userData));
        }
    });
}


function createCard(data) {
    const container = document.createElement('div');
    container.className = 'container';

    let cardClass = 'card';
    if (data.top === 'top1') {
        cardClass += ' card-top1'; // Добавляем класс для топ 1 игрока
    }

    container.innerHTML = `
        <div class="${cardClass}">
            <img src="${data.imgSrc}" alt="Изображение игрока" class="image">
            <div class="card-title-nick">${data.title}</div>
            <div class="card-sub">РЕЙТИНГ:<br><span style="color: rgb(0, 47, 255)"><b>${data.rating}</b></span></br></div>
            <button onclick="document.location='${data.link}'" class="button2">Просмотр</button>
        </div>
    `;
    return container;
}


document.addEventListener('DOMContentLoaded', getUserData);
// document.addEventListener('wheel', function(event) {
//     event.preventDefault(); // Предотвращение стандартной прокрутки

//     var currentSection = document.elementFromPoint(window.innerWidth / 2, window.innerHeight / 2);
//     var nextSection;

//     if (event.deltaY > 0) {
//         // Прокрутка вниз
//         nextSection = currentSection.nextElementSibling;
//     } else {
//         // Прокрутка вверх
//         nextSection = currentSection.previousElementSibling;
//     }

//     if (nextSection && nextSection.classList.contains('scroll-section')) {
//         window.scrollTo({
//             top: nextSection.offsetTop,
//             behavior: 'smooth'
//         });
//     }
// });

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
