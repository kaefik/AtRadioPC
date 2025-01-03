from flask import Flask, request, jsonify
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

RADIO_STATIONS_FILE = "cfg/radio_stations.json"
LAST_STATION_FILE = "cfg/last_station.json"
FAVORITES_FILE = "cfg/favorites.json"


def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, "r") as file:
            return json.load(file)
    return {"favorite1": None, "favorite2": None, "favorite3": None}


def save_favorites(favorites):
    with open(FAVORITES_FILE, "w") as file:
        json.dump(favorites, file, ensure_ascii=False, indent=2)


def load_radio_stations():
    if not os.path.exists(RADIO_STATIONS_FILE):
        os.makedirs(os.path.dirname(RADIO_STATIONS_FILE), exist_ok=True)
        # Создаем файл с тестовыми данными
        initial_stations = [
            {"name": "TatRadioTsentr", "url": "https://listen4.myradio24.com/trc"},
            {"name": "Yuldash (bashkirskoe radio)", "url": "https://radio.mediacdn.ru/uldash.mp3"}
        ]
        with open(RADIO_STATIONS_FILE, "w") as file:
            json.dump(initial_stations, file, ensure_ascii=False, indent=2)
        return initial_stations

    with open(RADIO_STATIONS_FILE, "r") as file:
        return json.load(file)


def save_radio_stations(stations):
    with open(RADIO_STATIONS_FILE, "w") as file:
        json.dump(stations, file, ensure_ascii=False, indent=2)


def save_last_station(station):
    with open(LAST_STATION_FILE, "w") as file:
        json.dump(station, file)


def get_last_station():
    if os.path.exists(LAST_STATION_FILE):
        with open(LAST_STATION_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return None
    return None


@app.route("/api/stations", methods=["GET"])
def get_stations():
    return jsonify({
        "stations": load_radio_stations(),
        "last_station": get_last_station()
    })


@app.route("/api/stations", methods=["POST"])
def add_station():
    data = request.json
    stations = load_radio_stations()
    stations.append({"name": data["name"], "url": data["url"]})
    save_radio_stations(stations)
    return jsonify({"success": True})


@app.route("/api/stations/<name>", methods=["DELETE"])
def delete_station(name):
    stations = load_radio_stations()
    stations = [s for s in stations if s["name"] != name]
    save_radio_stations(stations)

    last_station = get_last_station()
    if last_station and last_station["name"] == name:
        if os.path.exists(LAST_STATION_FILE):
            os.remove(LAST_STATION_FILE)

    return jsonify({"success": True})



@app.route("/api/last-station", methods=["POST"])
def update_last_station():
    data = request.json
    save_last_station({"name": data["name"], "url": data["url"]})
    return jsonify({"success": True})


@app.route("/api/favorites/<favorite_id>", methods=["GET", "POST"])
def manage_favorite(favorite_id):
    favorites = load_favorites()

    if request.method == "GET":
        return jsonify(favorites.get(f"favorite{favorite_id}"))

    data = request.json
    if data.get("save"):
        last_station = get_last_station()
        if last_station:
            favorites[f"favorite{favorite_id}"] = last_station
            save_favorites(favorites)
            return jsonify({"message": "Станция сохранена как избранная"})
        return jsonify({"error": "Нет текущей станции для сохранения"}), 400

    elif data.get("play"):
        favorite = favorites.get(f"favorite{favorite_id}")
        if favorite:
            save_last_station(favorite)
            return jsonify({"message": "Станция воспроизводится"})
        return jsonify({"error": "На эту кнопку нет сохраненной станции"}), 400

    return jsonify({"error": "Неверный запрос"}), 400


@app.route("/api/stations/save", methods=["POST"])
def save_stations_to_csv():
    try:
        stations = load_radio_stations()
        directory = request.json.get('directory', '')

        filename = os.path.join(os.path.expanduser('~'), directory, 'stations.csv')
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('Name;URL\n')
            for station in stations:
                f.write(f"{station['name']};{station['url']}\n")

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stations/load", methods=["POST"])
def load_stations_from_csv():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Файл не выбран"}), 400

        file = request.files['file']
        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')

        if len(lines) < 2:
            return jsonify({"error": "Файл пуст или неверного формата"}), 400

        if not lines[0].strip() == 'Name;URL':
            return jsonify({"error": "Неверный формат заголовка CSV"}), 400

        current_stations = load_radio_stations()
        current_names = {station['name'] for station in current_stations}

        for line in lines[1:]:
            name, url = line.strip().split(';')
            if name not in current_names:
                current_stations.append({"name": name, "url": url})

        save_radio_stations(current_stations)
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)