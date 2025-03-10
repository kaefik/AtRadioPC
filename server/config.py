import os


class Config:
    # Базовые настройки
    JSON_AS_ASCII = False
    CORS_ORIGINS = ["http://localhost:5000", "http://127.0.0.1:5000"]

    # Пути к файлам конфигурации
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    CONFIG_DIR = os.path.join(BASE_DIR, "cfg")

    RADIO_STATIONS_FILE = os.path.join(CONFIG_DIR, "radio_stations.json")
    LAST_STATION_FILE = os.path.join(CONFIG_DIR, "last_station.json")
    FAVORITES_FILE = os.path.join(CONFIG_DIR, "favorites.json")


class DevelopmentConfig(Config):
    DEBUG = True
    HOST = "127.0.0.1"
    PORT = 5000
    API_URL = f"http://{HOST}:{PORT}/api"


class ProductionConfig(Config):
    DEBUG = False
    HOST = "0.0.0.0"  # Слушаем все внешние подключения
    PORT = 8080
    CORS_ORIGINS = ["https://your-domain.com"]  # Замените на ваш домен
    API_URL = "https://your-domain.com/api"  # Замените на ваш домен


# Словарь конфигураций
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}