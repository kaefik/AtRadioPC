# AtRadioPC
сервис прослушивания онлайн радиостанций для ПК


# Установка зависимостей

```
./install_libs.sh
```

# Настройка вирутального окружения для разработки
```
pyenv virtualenv 3.12.5 atradio_pc
```

Перейти в папку проекта и запустить
```
pyenv local atradio_pc
```


Для остановки контейнеров 

```
docker-compose down && docker system prune -a 
```

Собрать новый контейнер:

```
docker-compose -f docker-compose.yml up --build
```

Для проверки статусов:

```
# Проверка статуса контейнеров
docker-compose ps

# Проверка логов backend
docker-compose logs backend

# Проверка логов frontend
docker-compose logs frontend
```

Если вы хотите проверить работу приложения локально:

Frontend будет доступен по адресу: http://localhost
API будет доступно по адресу: http://localhost/api



----


Для запуска в режиме разработки:

# Запуск
docker-compose -f docker-compose.dev.yml up --build

# Остановка
docker-compose -f docker-compose.dev.yml down

# Просмотр логов
docker-compose -f docker-compose.dev.yml logs -f

# Просмотр логов конкретного сервиса
docker-compose -f docker-compose.dev.yml logs -f backend