import config from './config.js';

let currentStation = null;

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
        const response = await fetch(`${config.API_URL}/stations`);
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
                const response = await fetch(`${config.API_URL}/stations/load`, {
                    method: 'POST',
                    body: formData
                });
                if (response.ok) {
                    showNotification('Станции загружены успешно', 'success');
                    // Загружаем обновленный список станций
                    const stationsResponse = await fetch(`${config.API_URL}/stations`);
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
        const response = await fetch(`${config.API_URL}/stations`);
        const data = await response.json();
        console.log('Loaded data:', data); // Для отладки

        // Обновляем currentStation перед обновлением списка станций
        if (data.last_station) {
            currentStation = data.last_station;
        }

        updateStationsList(data.stations);

        if (data.last_station) {
            playStation(data.last_station);
            markLastStationActive(data.last_station.name);
            scrollToActiveStation(data.last_station.name);
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
        await fetch(`${config.API_URL}/last-station`, {
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
        await fetch(`${config.API_URL}/stations/${name}`, {
            method: 'DELETE'
        });
        // Загружаем обновленный список станций
        const response = await fetch(`${config.API_URL}/stations`);
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
        await fetch(`${config.API_URL}/stations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(station)
        });
        closeModal();
        e.target.reset();
        // Загружаем обновленный список станций
        const response = await fetch(`${config.API_URL}/stations`);
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

    // Функция для сохранения станции
    const saveFavorite = async () => {
        try {
            const response = await fetch(`${config.API_URL}/favorites/${favoriteId}`, {
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

    // Короткое нажатие - воспроизведение
    button.addEventListener('click', async (e) => {
        e.preventDefault();

        // Если это было долгое нажатие, не запускаем воспроизведение
        if (isLongPress) {
            isLongPress = false;
            return;
        }

        try {
            const response = await fetch(`${config.API_URL}/favorites/${favoriteId}`, {
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
                const stationsResponse = await fetch(`${config.API_URL}/stations`);
                const stationsData = await stationsResponse.json();
                updateStationsList(stationsData.stations);
            } else {
                showNotification(data.error || 'Ошибка воспроизведения', 'error');
            }
        } catch (error) {
            console.error('Error playing favorite:', error);
            showNotification('Ошибка воспроизведения', 'error');
        }
    });

    // Начало нажатия
    button.addEventListener('mousedown', (e) => {
        e.preventDefault();
        isLongPress = false;
        pressTimer = setTimeout(() => {
            isLongPress = true;
            // Запускаем сохранение в отдельном микротаске
            Promise.resolve().then(saveFavorite);
        }, 1000);
    });

    // Отпускание кнопки
    button.addEventListener('mouseup', (e) => {
        e.preventDefault();
        clearTimeout(pressTimer);
    });

    // Уход мыши с кнопки
    button.addEventListener('mouseleave', (e) => {
        e.preventDefault();
        clearTimeout(pressTimer);
    });

    // Добавляем обработчики для тач-устройств
    button.addEventListener('touchstart', (e) => {
        e.preventDefault();
        isLongPress = false;
        pressTimer = setTimeout(() => {
            isLongPress = true;
            Promise.resolve().then(saveFavorite);
        }, 1000);
    });

    button.addEventListener('touchend', (e) => {
        e.preventDefault();
        clearTimeout(pressTimer);
    });
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
document.addEventListener('DOMContentLoaded', loadInitialData);