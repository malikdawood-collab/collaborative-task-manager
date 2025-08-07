# app/__init__.py

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_login import LoginManager

from .config import Config
from .database import db

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'message': 'Unauthorized: Please log in'}), 401

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # CORS: allow our React dev server + include credentials,
    # and explicitly allow the methods we need (including DELETE & OPTIONS).
    CORS(
        app,
        resources={
            r"/api/*":  {"origins": "http://localhost:3000"},
            r"/auth/*": {"origins": "http://localhost:3000"},
        },
        supports_credentials=True,
        methods=["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "Authorization"]
    )

    # Register Blueprints
    from .auth import auth_bp
    from .projects import projects_bp
    from .tasks import tasks_bp

    app.register_blueprint(auth_bp,    url_prefix='/auth')
    app.register_blueprint(projects_bp, url_prefix='/api/projects')
    app.register_blueprint(tasks_bp,    url_prefix='/api')

    # Create tables (and apply any new migrations you’ve run)
    with app.app_context():
        db.create_all()

    return app
