from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

# Путь к файлу конфигурации радиостанций
RADIO_STATIONS_FILE = "cfg/radio_stations.json"
# Файл для сохранения последней станции
LAST_STATION_FILE = "cfg/last_station.json"

def load_radio_stations():
    """Загружаем радиостанции из файла конфигурации"""
    with open(RADIO_STATIONS_FILE, "r") as file:
        return json.load(file)



def save_last_station(station):
    """Сохраняем последнюю станцию в файл"""
    with open(LAST_STATION_FILE, "w") as file:
        json.dump(station, file)

def get_last_station():
    """Получаем последнюю станцию из файла"""
    if os.path.exists(LAST_STATION_FILE):
        with open(LAST_STATION_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return None  # Если файл поврежден
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    radio_stations = load_radio_stations()
    last_station = get_last_station()

    if request.method == "POST":
        station_name = request.form.get("station_name")
        station_url = request.form.get(f"station_url_{station_name}")
        last_station = {"name": station_name, "url": station_url}

        save_last_station(last_station)

        # Перезагружаем страницу
        return redirect(url_for("index"))

    return render_template("index.html", stations=radio_stations, last_station=last_station)

if __name__ == "__main__":
    app.run(debug=True)
