# radio_app.py
from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

RADIO_STATIONS_FILE = "cfg/radio_stations.json"
LAST_STATION_FILE = "cfg/last_station.json"

def load_radio_stations():
    """Загружаем радиостанции из файла конфигурации"""
    with open(RADIO_STATIONS_FILE, "r") as file:
        return json.load(file)

def save_radio_stations(stations):
    """Сохраняем список радиостанций в файл"""
    with open(RADIO_STATIONS_FILE, "w") as file:
        json.dump(stations, file, ensure_ascii=False, indent=2)

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
                return None
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    radio_stations = load_radio_stations()
    last_station = get_last_station()

    if request.method == "POST":
        if "new_station" in request.form:
            # Добавление новой станции
            name = request.form.get("station_name")
            url = request.form.get("station_url")
            if name and url:
                radio_stations.append({"name": name, "url": url})
                save_radio_stations(radio_stations)
        else:
            # Выбор станции для проигрывания
            station_name = request.form.get("station_name")
            station_url = request.form.get(f"station_url_{station_name}")
            last_station = {"name": station_name, "url": station_url}
            save_last_station(last_station)

        return redirect(url_for("index"))

    return render_template("index.html", stations=radio_stations, last_station=last_station)

if __name__ == "__main__":
    app.run(debug=True)