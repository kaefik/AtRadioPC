from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
import os
from config import config
from models import db, User, UserStation, Favorite

login_manager = LoginManager()


def create_app(config_name="default"):
    app = Flask(__name__)

    # Загружаем конфигурацию
    app.config.from_object(config[config_name])

    # Добавляем настройки для базы данных и аутентификации
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///radio.db'
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SECRET_KEY'] = 'your-secret-key-change-this'  # Измените на реальный секретный ключ

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})

    # Создаем все таблицы при первом запуске
    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Регистрация и авторизация
    @app.route("/api/auth/register", methods=["POST"])
    def register():
        data = request.json

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400

        user = User(
            username=data['username'],
            email=data['email'],
            auth_type='local'
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User registered successfully'})

    @app.route("/api/auth/login", methods=["POST"])
    def login():
        data = request.json
        user = User.query.filter_by(username=data['username']).first()

        if user and user.check_password(data['password']):
            login_user(user)
            return jsonify({'message': 'Logged in successfully'})

        return jsonify({'error': 'Invalid username or password'}), 401

    @app.route("/api/auth/logout")
    @login_required
    def logout():
        logout_user()
        return jsonify({'message': 'Logged out successfully'})

    # Работа со станциями
    @app.route("/api/stations", methods=["GET"])
    @login_required
    def get_stations():
        stations = UserStation.query.filter_by(user_id=current_user.id).all()
        stations_data = [{"name": s.name, "url": s.url} for s in stations]

        last_station = None
        if current_user.last_station_id:
            station = UserStation.query.get(current_user.last_station_id)
            if station:
                last_station = {"name": station.name, "url": station.url}

        return jsonify({
            "stations": stations_data,
            "last_station": last_station
        })

    @app.route("/api/stations", methods=["POST"])
    @login_required
    def add_station():
        data = request.json

        existing = UserStation.query.filter_by(
            user_id=current_user.id,
            name=data["name"]
        ).first()

        if existing:
            return jsonify({"error": "Станция с таким названием уже существует"}), 400

        station = UserStation(
            user_id=current_user.id,
            name=data["name"],
            url=data["url"]
        )

        db.session.add(station)
        db.session.commit()

        return jsonify({"success": True})

    @app.route("/api/stations/<name>", methods=["DELETE"])
    @login_required
    def delete_station(name):
        station = UserStation.query.filter_by(
            user_id=current_user.id,
            name=name.strip()
        ).first()

        if not station:
            return jsonify({"error": "Станция не найдена"}), 404

        # Удаляем связанные избранные
        Favorite.query.filter_by(station_id=station.id).delete()

        # Очищаем last_station_id если это была последняя станция
        if current_user.last_station_id == station.id:
            current_user.last_station_id = None

        db.session.delete(station)
        db.session.commit()

        return jsonify({"success": True})

    @app.route("/api/last-station", methods=["POST"])
    @login_required
    def update_last_station():
        data = request.json
        station = UserStation.query.filter_by(
            user_id=current_user.id,
            name=data["name"]
        ).first()

        if not station:
            return jsonify({"error": "Станция не найдена"}), 404

        current_user.last_station_id = station.id
        db.session.commit()

        return jsonify({"success": True})

    # Работа с избранным
    @app.route("/api/favorites/<favorite_id>", methods=["GET", "POST"])
    @login_required
    def manage_favorite(favorite_id):
        if request.method == "GET":
            favorite = Favorite.query.filter_by(
                user_id=current_user.id,
                position=int(favorite_id)
            ).first()

            if favorite:
                station = UserStation.query.get(favorite.station_id)
                return jsonify({
                    "name": station.name,
                    "url": station.url
                })
            return jsonify(None)

        data = request.json
        position = int(favorite_id)

        if data.get("save"):
            if not current_user.last_station_id:
                return jsonify({"error": "Нет текущей станции для сохранения"}), 400

            # Удаляем существующую избранную станцию если есть
            Favorite.query.filter_by(
                user_id=current_user.id,
                position=position
            ).delete()

            # Сохраняем новую
            favorite = Favorite(
                user_id=current_user.id,
                station_id=current_user.last_station_id,
                position=position
            )
            db.session.add(favorite)
            db.session.commit()

            return jsonify({"message": "Станция сохранена как избранная"})

        elif data.get("play"):
            favorite = Favorite.query.filter_by(
                user_id=current_user.id,
                position=position
            ).first()

            if not favorite:
                return jsonify({"error": "На эту кнопку нет сохраненной станции"}), 400

            station = UserStation.query.get(favorite.station_id)
            current_user.last_station_id = station.id
            db.session.commit()

            return jsonify({
                "message": "Станция воспроизводится",
                "station": {
                    "name": station.name,
                    "url": station.url
                }
            })

        return jsonify({"error": "Неверный запрос"}), 400

    # Импорт/экспорт станций
    @app.route("/api/stations/save", methods=["POST"])
    @login_required
    def save_stations_to_csv():
        try:
            stations = UserStation.query.filter_by(user_id=current_user.id).all()
            directory = request.json.get('directory', '')

            filename = os.path.join(os.path.expanduser('~'), directory, 'stations.csv')
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, 'w', encoding='utf-8') as f:
                f.write('Name;URL\n')
                for station in stations:
                    f.write(f"{station.name};{station.url}\n")

            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/stations/load", methods=["POST"])
    @login_required
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

            existing_names = {
                station.name for station in
                UserStation.query.filter_by(user_id=current_user.id).all()
            }

            for line in lines[1:]:
                name, url = line.strip().split(';')
                if name not in existing_names:
                    station = UserStation(
                        user_id=current_user.id,
                        name=name.strip(),
                        url=url.strip()
                    )
                    db.session.add(station)

            db.session.commit()
            return jsonify({"success": True})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app


if __name__ == "__main__":
    env = os.getenv("FLASK_ENV", "development")
    app = create_app(env)
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )