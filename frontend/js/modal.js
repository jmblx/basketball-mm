const modal = document.getElementById("myModal");
const searchImg = document.getElementById("searchImg");
const searchButton = document.getElementById("searchButton");
const span = document.getElementsByClassName("close")[0];
const body = document.body;

searchImg.onclick = function() {
    modal.style.display = "block";
    body.classList.add("body-no-scroll");
}

span.onclick = function() {
    modal.style.display = "none";
    body.classList.remove("body-no-scroll");
}

window.onclick = function(event) {
    if (event.target === modal) {
        modal.style.display = "none";
        body.classList.remove("body-no-scroll");
    }
}

const searchInput = document.getElementById('searchInput');
let searchTimeout;

searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(performSearch, 1300); // Поиск через 1.3 секунды после последнего ввода символа
});

searchButton.addEventListener('click', () => {
    performSearch();
});

async function performSearch() {
    const searchText = searchInput.value;
    if (searchText.trim() !== '') {
        const userResults = await searchUsers(searchText);
        displayUserResults(userResults);

        const teamResults = await searchTeams(searchText);
        displayTeamResults(teamResults);
    } else {
        document.getElementById('user-search-results').innerHTML = 'Пользователи не найдены';
        document.getElementById('team-search-results').innerHTML = 'Команды не найдены';
    }
}

async function searchUsers(searchText) {
    const response = await fetch(`http://127.0.0.1:8000/social/find-user?nickname=${searchText}`);
    return await response.json();
}

async function searchTeams(searchText) {
    const response = await fetch(`http://127.0.0.1:8000/social/find-team?team_name=${searchText}`);
    return await response.json();
}

function displayUserResults(nicknames) {
    const userResultsDiv = document.getElementById('user-search-results');
    if (Array.isArray(nicknames) && nicknames.length > 0) {
        userResultsDiv.innerHTML = nicknames.map(nickname =>
            `<a href="http://localhost:8000/user/${nickname}">${nickname}</a>`
        ).join('<br>');
    } else {
        userResultsDiv.innerHTML = 'Пользователь не найден';
    }
}

function displayTeamResults(teams) {
    const teamResultsDiv = document.getElementById('team-search-results');
    if (Array.isArray(teams) && teams.length > 0) {
        teamResultsDiv.innerHTML = teams.map(team =>
            `<a href="http://localhost:8000/team/page/${team.slug}">${team.name}</a>`
        ).join('<br>');
    } else {
        teamResultsDiv.innerHTML = 'Команды не найдены';
    }
}
