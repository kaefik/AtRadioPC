from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

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


@app.route("/", methods=["GET", "POST"])
def index():
    radio_stations = load_radio_stations()
    last_station = get_last_station()

    if request.method == "POST":
        if "new_station" in request.form:
            name = request.form.get("station_name")
            url = request.form.get("station_url")
            if name and url:
                radio_stations.append({"name": name, "url": url})
                save_radio_stations(radio_stations)
        elif "delete_station" in request.form:
            station_name = request.form.get("delete_station")
            radio_stations = [s for s in radio_stations if s["name"] != station_name]
            save_radio_stations(radio_stations)
            if last_station and last_station["name"] == station_name:
                last_station = None
                if os.path.exists(LAST_STATION_FILE):
                    os.remove(LAST_STATION_FILE)
        else:
            station_name = request.form.get("station_name")
            station_url = request.form.get(f"station_url_{station_name}")
            last_station = {"name": station_name, "url": station_url}
            save_last_station(last_station)

        return redirect(url_for("index"))

    return render_template("index.html", stations=radio_stations, last_station=last_station)


@app.route("/save_stations", methods=["POST"])
def save_stations():
    try:
        stations = load_radio_stations()
        selected_dir = request.form.get('directory', '')

        filename = os.path.join(os.path.expanduser('~'), selected_dir, 'stations.csv')
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('Name;URL\n')
            for station in stations:
                f.write(f"{station['name']};{station['url']}\n")

        return '', 200

    except Exception as e:
        return str(e), 500


@app.route("/load_stations", methods=["POST"])
def load_stations_from_csv():
    try:
        if 'file' not in request.files:
            return 'Файл не выбран', 400

        file = request.files['file']
        if file.filename == '':
            return 'Файл не выбран', 400

        current_stations = load_radio_stations()
        current_names = {station['name'] for station in current_stations}

        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')

        if len(lines) < 2:
            return 'Файл пуст или неверного формата', 400

        if not lines[0].strip() == 'Name;URL':
            return 'Неверный формат заголовка CSV', 400

        new_stations = []
        for line in lines[1:]:
            name, url = line.strip().split(';')
            if name not in current_names:
                new_stations.append({"name": name, "url": url})

        if new_stations:
            current_stations.extend(new_stations)
            save_radio_stations(current_stations)

        return '', 200

    except Exception as e:
        return str(e), 500

@app.route("/favorites/<favorite_id>", methods=["POST"])
def manage_favorite(favorite_id):
    favorites = load_favorites()
    if "save" in request.form:
        last_station = get_last_station()
        if last_station:
            favorites[f"favorite{favorite_id}"] = last_station
            save_favorites(favorites)
            return "Станция сохранена как избранная", 200
        return "Нет текущей станции для сохранения", 400
    elif "play" in request.form:
        favorite = favorites.get(f"favorite{favorite_id}")
        if favorite:
            save_last_station(favorite)
            return "Станция воспроизводится", 200
        return "На эту кнопку нет сохраненной станции", 400
    return "Неверный запрос", 400

@app.route("/update_station", methods=["POST"])
def update_station():
    station_name = request.form.get("station_name")
    station_url = request.form.get("station_url")

    # Сохраняем текущую станцию
    last_station = {"name": station_name, "url": station_url}
    save_last_station(last_station)

    # Загружаем список станций
    radio_stations = load_radio_stations()

    # Возвращаем обновленный HTML-фрагмент: список станций и текущую станцию
    return {
        "station_list_html": render_template("station_list.html", stations=radio_stations, last_station=last_station),
        "last_station_name": last_station["name"],
        "last_station_url": last_station["url"],
    }


if __name__ == "__main__":
    app.run(debug=True)