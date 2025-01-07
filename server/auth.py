# auth.py
from flask import Blueprint, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User

auth = Blueprint('auth', __name__)
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.route('/api/auth/register', methods=['POST'])
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


@auth.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({'message': 'Logged in successfully'})

    return jsonify({'error': 'Invalid username or password'}), 401


@auth.route('/api/auth/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

