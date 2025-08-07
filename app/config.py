import os

class Config:
    # Secret key for session management and security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_that_you_should_change'

    # Database configuration
    # Using SQLite for simplicity, stored in the instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail configuration (if you were to add email functionality)
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')

    # CORS configuration is now handled directly in app/__init__.py initialization
    # Removed CORS_HEADERS and CORS_RESOURCES from here to avoid potential conflicts
