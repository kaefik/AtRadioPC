import config from './config.js';

let currentStation = null;
let isAuthenticated = false;


// Функции аутентификации
async function checkAuth() {
    try {
        const response = await fetch(`${config.API_URL}/auth/check`, {
            credentials: 'include'  // Важно для работы с сессиями
        });
        isAuthenticated = response.ok;
        return isAuthenticated;
    } catch (error) {
        console.error('Auth check error:', error);
        return false;
    }
}

async function login(username, password) {
    try {
        const response = await fetch(`${config.API_URL}/auth/login`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            isAuthenticated = true;
            showApp();
            // Сбрасываем форму входа
            document.getElementById('loginForm').reset();
        } else {
            const data = await response.json();
            showNotification(data.error || 'Ошибка входа', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('Ошибка входа', 'error');
    }
}

async function register(username, email, password) {
    try {
        const response = await fetch(`${config.API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Регистрация успешна, выполните вход');
            switchAuthTab('login');
            // Сбрасываем форму регистрации
            document.getElementById('registerForm').reset();
        } else {
            showNotification(data.error || 'Ошибка регистрации', 'error');
        }
    } catch (error) {
        console.error('Register error:', error);
        showNotification('Ошибка регистрации', 'error');
    }
}

async function logout() {
    try {
        await fetch(`${config.API_URL}/auth/logout`, {
            method: 'GET',
            credentials: 'include'
        });
        isAuthenticated = false;
        showAuth();
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// Функции UI
function showAuth() {
    document.getElementById('authContainer').style.display = 'block';
    document.getElementById('appContainer').style.display = 'none';
}

function showApp() {
    document.getElementById('authContainer').style.display = 'none';
    document.getElementById('appContainer').style.display = 'block';
    loadInitialData();
}

function switchAuthTab(tab) {
    // Обновляем активную вкладку
    document.querySelectorAll('.auth-tab').forEach(t => {
        t.classList.toggle('active', t.dataset.tab === tab);
    });

    // Показываем нужную форму
    document.getElementById('loginForm').style.display = tab === 'login' ? 'flex' : 'none';
    document.getElementById('registerForm').style.display = tab === 'register' ? 'flex' : 'none';
}

// Обновляем все fetch запросы для работы с credentials
async function fetchWithAuth(url, options = {}) {
    const defaultOptions = {
        credentials: 'include',
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    };

    const response = await fetch(url, defaultOptions);

    if (response.status === 401) {
        isAuthenticated = false;
        showAuth();
        throw new Error('Unauthorized');
    }

    return response;
}





// Move these functions to the global scope

// Управление модальным окном
window.openModal = function() {
    document.getElementById('addStationModal').style.display = 'block';
}

window.closeModal = function()  {
    document.getElementById('addStationModal').style.display = 'none';
}

// Сохранение станций в CSV
window.saveStations = async function() {
    try {
        // Fetch current stations from the API
        const response = await fetchWithAuth(`${config.API_URL}/stations`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error('Failed to fetch stations');
        }

        // Convert stations to CSV format
        const csvContent = [
            // CSV header
            ['Name', 'URL'].join(','),
            // Station data rows
            ...data.stations.map(station => [
                // Escape quotes and commas in the station name
                `"${station.name.replace(/"/g, '""')}"`,
                `"${station.url.replace(/"/g, '""')}"`
            ].join(','))
        ].join('\n');

        // Create blob with CSV content
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

        // Create download link
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.setAttribute('download', `radio_stations_${new Date().toISOString().split('T')[0]}.csv`);

        // Trigger download
        document.body.appendChild(link);
        link.click();

        // Cleanup
        document.body.removeChild(link);
        URL.revokeObjectURL(link.href);

    } catch (error) {
        console.error('Error saving stations:', error);
        showNotification('Ошибка при сохранении станций', 'error');
    }
}

// Загрузка станций из CSV
window.loadStations = async function() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.csv';

    input.addEventListener('change', async (e) => {
        if (e.target.files.length > 0) {
            const formData = new FormData();
            formData.append('file', e.target.files[0]);

            try {
                const response = await fetchWithAuth(`${config.API_URL}/stations/load`, {
                    method: 'POST',
                    body: formData
                });
                if (response.ok) {
                    showNotification('Станции загружены успешно', 'success');
                    // Загружаем обновленный список станций
                    const stationsResponse = await fetchWithAuth(`${config.API_URL}/stations`);
                    const stationsData = await stationsResponse.json();
                    updateStationsList(stationsData.stations);
                } else {
                    const data = await response.json();
                    showNotification(data.error || 'Ошибка при загрузке', 'error');

                }
            } catch (error) {
                console.error('Error loading stations:', error);
            }
        }
    });

    input.click();
}


// Загрузка начальных данных
async function loadInitialData() {
    try {
        const response = await fetchWithAuth(`${config.API_URL}/stations`);
        const data = await response.json();

        if (data.last_station) {
            currentStation = data.last_station;
        }

        updateStationsList(data.stations);

        if (data.last_station) {
            playStation(data.last_station);
            markLastStationActive(data.last_station.name);
        }
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

// Обновление списка станций
function updateStationsList(stations) {
    const stationsList = document.getElementById('stationsList');
    if (!stationsList) {
        console.error('stationsList element not found');
        return;
    }

    stationsList.innerHTML = '';

    stations.forEach(station => {
        const li = document.createElement('li');
        const playButton = document.createElement('button');

        // Добавляем класс active для текущей станции
        const isActive = currentStation && currentStation.name === station.name;
        playButton.className = `station-button ${isActive ? 'active' : ''}`;
        playButton.textContent = station.name;

        playButton.onclick = () => {
            // Сначала убираем active класс у всех кнопок
            document.querySelectorAll('.station-button').forEach(btn => {
                btn.classList.remove('active');
            });
            // Добавляем active класс текущей кнопке
            playButton.classList.add('active');
            // Запускаем воспроизведение
            playStation(station);
            // Прокручиваем к активной станции
            scrollToActiveStation(station.name);
        };

        const deleteButton = document.createElement('button');
        deleteButton.className = 'delete-btn';
        deleteButton.textContent = '✖';
        deleteButton.onclick = () => deleteStation(station.name);

        li.appendChild(playButton);
        li.appendChild(deleteButton);
        stationsList.appendChild(li);
    });
}

// Функция для пометки последней станции как активной
function markLastStationActive(stationName) {
    const buttons = document.querySelectorAll('.station-button');
    buttons.forEach(button => {
        if (button.textContent === stationName) {
            button.classList.add('active');
        }
    });
}

// Функция для прокрутки к активной станции
function scrollToActiveStation(stationName) {
    const buttons = document.querySelectorAll('.station-button');
    buttons.forEach(button => {
        if (button.textContent === stationName) {
            button.scrollIntoView({ block: 'center', behavior: 'smooth' });
        }
    });
}

// Воспроизведение станции
async function playStation(station) {
    try {
        // Обновляем текущую станцию
        currentStation = station;

        // Обновляем название в заголовке
        const currentStationElement = document.getElementById('currentStation');
        if (currentStationElement) {
            currentStationElement.textContent = station.name;
        }

        // Обновляем и запускаем плеер
        const audioPlayer = document.getElementById('audioPlayer');
        if (audioPlayer) {
            audioPlayer.src = station.url;
            try {
                await audioPlayer.play();
            } catch (error) {
                console.error('Error playing audio:', error);
            }
        }

        // Сохраняем последнюю станцию на сервере
        await fetchWithAuth(`${config.API_URL}/last-station`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(station)
        });

    } catch (error) {
        console.error('Error in playStation:', error);
    }
}

// Удаление станции
async function deleteStation(name) {
    if (!confirm(`Удалить станцию ${name}?`)) return;

    try {
        await fetchWithAuth(`${config.API_URL}/stations/${name}`, {
            method: 'DELETE'
        });
        // Загружаем обновленный список станций
        const response = await fetchWithAuth(`${config.API_URL}/stations`);
        const data = await response.json();
        updateStationsList(data.stations);
    } catch (error) {
        console.error('Error deleting station:', error);
    }
}

// Обработка добавления новой станции
document.getElementById('addStationForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const station = {
        name: formData.get('station_name'),
        url: formData.get('station_url')
    };

    try {
        await fetchWithAuth(`${config.API_URL}/stations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(station)
        });
        closeModal();
        e.target.reset();
        // Загружаем обновленный список станций
        const response = await fetchWithAuth(`${config.API_URL}/stations`);
        const data = await response.json();
        updateStationsList(data.stations);
    } catch (error) {
        console.error('Error adding station:', error);
    }
});


// Управление избранными станциями
document.querySelectorAll('.favorite-btn').forEach((button) => {
    const favoriteId = button.getAttribute('data-id');
    let pressTimer;
    let isLongPress = false;
    let touchStartTime = 0;

    // Функция для сохранения станции
    const saveFavorite = async () => {
        try {
            const response = await fetchWithAuth(`${config.API_URL}/favorites/${favoriteId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ save: true })
            });
            const data = await response.json();
            showNotification(data.message || data.error || 'Станция сохранена');
        } catch (error) {
            console.error('Error saving favorite:', error);
            showNotification('Ошибка при сохранении станции', 'error');
        }
    };

    // Функция для воспроизведения станции
    const playFavorite = async () => {
        try {
            const response = await fetchWithAuth(`${config.API_URL}/favorites/${favoriteId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ play: true })
            });
            const data = await response.json();
            if (response.ok && data.station) {
                currentStation = data.station;
                playStation(data.station);
                const stationsResponse = await fetchWithAuth(`${config.API_URL}/stations`);
                const stationsData = await stationsResponse.json();
                updateStationsList(stationsData.stations);
            } else {
                showNotification(data.error || 'Ошибка воспроизведения', 'error');
            }
        } catch (error) {
            console.error('Error playing favorite:', error);
            showNotification('Ошибка воспроизведения', 'error');
        }
    };

    // Обработчики для десктопа
    button.addEventListener('click', (e) => {
        e.preventDefault();
        if (!isLongPress) {
            playFavorite();
        }
    });

    button.addEventListener('mousedown', (e) => {
        e.preventDefault();
        isLongPress = false;
        pressTimer = setTimeout(() => {
            isLongPress = true;
            Promise.resolve().then(saveFavorite);
        }, 1000);
    });

    button.addEventListener('mouseup', (e) => {
        e.preventDefault();
        clearTimeout(pressTimer);
    });

    button.addEventListener('mouseleave', (e) => {
        e.preventDefault();
        clearTimeout(pressTimer);
    });

    // Обработчики для мобильных устройств
    button.addEventListener('touchstart', (e) => {
        e.preventDefault();
        isLongPress = false;
        touchStartTime = Date.now();
        pressTimer = setTimeout(() => {
            isLongPress = true;
            Promise.resolve().then(saveFavorite);
        }, 1000);
    });

    button.addEventListener('touchend', (e) => {
        e.preventDefault();
        clearTimeout(pressTimer);

        // Проверяем, было ли это коротким нажатием
        const touchDuration = Date.now() - touchStartTime;
        if (touchDuration < 1000 && !isLongPress) {
            playFavorite();
        }
    });

    // Предотвращаем двойное срабатывание на устройствах с поддержкой и тача, и мыши
    button.addEventListener('touchstart', (e) => {
        e.preventDefault();
    }, { passive: false });

    button.addEventListener('touchend', (e) => {
        e.preventDefault();
    }, { passive: false });
});



// Опциональная функция для создания красивого уведомления
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Удаляем уведомление через 3 секунды
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Закрытие модального окна при клике вне его
window.onclick = function(event) {
    const modal = document.getElementById('addStationModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
};

// Загружаем данные при запуске
// Инициализация приложения
document.addEventListener('DOMContentLoaded', async () => {
    // Настраиваем обработчики форм аутентификации
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        await login(formData.get('username'), formData.get('password'));
    });

    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        if (formData.get('password') !== formData.get('password_confirm')) {
            showNotification('Пароли не совпадают', 'error');
            return;
        }
        await register(
            formData.get('username'),
            formData.get('email'),
            formData.get('password')
        );
    });

    // Настраиваем переключение вкладок
    document.querySelectorAll('.auth-tab').forEach(tab => {
        tab.addEventListener('click', () => switchAuthTab(tab.dataset.tab));
    });

    // Настраиваем кнопку выхода
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Проверяем аутентификацию и показываем нужный экран
    if (await checkAuth()) {
        showApp();
    } else {
        showAuth();
    }
});