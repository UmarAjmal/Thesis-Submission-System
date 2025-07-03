

import os
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '27c16feb24bc3f0d7c84819327ea0709'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///thesis_submission.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Flask-Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Your email
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Your email password
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME

    # Flask-Caching Configuration
    CACHE_TYPE = 'SimpleCache'  # Options: 'RedisCache', 'MemcachedCache', etc.
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes

    # Pagination
    ITEMS_PER_PAGE = 10

    # Allowed File Extensions
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
