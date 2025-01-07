from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    auth_type = db.Column(db.String(20), nullable=False)  # local, google, etc.

    # Связи с другими таблицами
    favorites = db.relationship('Favorite', backref='user', lazy=True)
    stations = db.relationship('UserStation', backref='user', lazy=True)
    last_station_id = db.Column(db.Integer, db.ForeignKey('user_station.id'), nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class UserStation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Добавляем составной уникальный индекс
    __table_args__ = (
        db.UniqueConstraint('user_id', 'name', name='unique_station_name_per_user'),
    )


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('user_station.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)  # 1, 2, или 3
