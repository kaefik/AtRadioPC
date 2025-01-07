
# AtRadioPC  

сервис прослушивания онлайн радиостанций для ПК  
  

#  Основные настройки программы

в  server/config.py находится параметр SECRET_KEY , его нужно генерировать с помощью скрипта server/generate_secret_key.py



# Собрать новый контейнер для разработки  
  
  
## Доступ к приложению в режиме разработки:  
  
- Frontend: http://localhost:8080  
- Backend API: http://localhost:5000/api  

  
## Запуск  

```
docker-compose -f docker-compose.dev.yml up --build  
```

  
## Остановка  

```
docker-compose -f docker-compose.dev.yml down  
```

  
## Просмотр логов  

```
docker-compose -f docker-compose.dev.yml logs -f  
```

  
## Просмотр логов конкретного сервиса  

```
docker-compose -f docker-compose.dev.yml logs -f backend  
```

  
## Подключение к контейнеру backend  

```
docker-compose -f docker-compose.dev.yml exec backend bash 
```
 
  
## Просмотр логов nginx  

```
docker-compose -f docker-compose.dev.yml exec frontend tail -f /var/log/nginx/error.log  
```

  
## Проверка статуса контейнеров  

```
docker-compose -f docker-compose.dev.yml ps
```


## Для остановки контейнеров 

```  
 docker-compose down && docker system prune -a  
```  


  
# Собрать новый контейнер для продакшена  


## Если вы хотите проверить работу приложения локально  
  
- Frontend будет доступен по адресу: http://localhost  
- API будет доступно по адресу: http://localhost/api 

## Запуск  

```  
docker-compose -f docker-compose.yml up --build  
```  
  


## Проверка статуса контейнеров 
```  
 docker-compose ps   
```  


## Проверка логов backend 

```
docker-compose logs backend 
```


## Проверка логов frontend  

```
docker-compose logs frontend  
```



 

  
----  
  
