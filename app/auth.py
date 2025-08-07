from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User
from .database import db

# Blueprint for authentication
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return {'message': 'Already logged in', 'is_authenticated': True}, 200

    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return {'message': 'Login successful!', 'is_authenticated': True, 'username': user.username}, 200
    return {'message': 'Invalid username or password.'}, 401


@auth_bp.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return {'message': 'Already logged in', 'is_authenticated': True}, 200

    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return {'message': 'Username already exists.'}, 409
    if User.query.filter_by(email=email).first():
        return {'message': 'Email already registered.'}, 409

    hashed = generate_password_hash(password, method='scrypt')
    new_user = User(username=username, email=email, password=hashed)
    db.session.add(new_user)
    db.session.commit()

    return {'message': 'Registration successful!'}, 201


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return {'message': 'Logged out.'}, 200


@auth_bp.route('/status')
def status():
    return {'is_authenticated': current_user.is_authenticated,
            'username': current_user.username if current_user.is_authenticated else None}, 200

