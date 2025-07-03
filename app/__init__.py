import os
from werkzeug.exceptions import RequestEntityTooLarge
from flask import Flask, flash, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_caching import Cache
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Load environment variables from the .env file
load_dotenv()

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()
cache = Cache()

def create_app():
    """Application factory function to initialize and configure the Flask app."""
    app = Flask(__name__)

    # Load configuration from the Config class
    app.config.from_object('app.config.Config')

    # Initialize Flask extensions with the app instance
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)

    # Configure Flask-Login
    login_manager.login_view = 'routes.login'
    login_manager.login_message_category = 'info'

    # Define user_loader callback for Flask-Login
    from app.models import User  # Import inside to prevent circular imports

    @login_manager.user_loader
    def load_user(user_id):
        """Callback to reload the user object based on the user ID stored in the session."""
        try:
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            return None

    # Register blueprints
    from .routes import routes
    app.register_blueprint(routes)

    # Ensure the upload folder exists
    upload_folder = app.config.get('UPLOAD_FOLDER', os.path.join(app.root_path, 'static', 'uploads'))
    Path(upload_folder).mkdir(parents=True, exist_ok=True)

    # Set up logging
    setup_logging(app)

    # Register custom error handlers
    register_error_handlers(app)

    return app

def setup_logging(app):
    """Configure logging for the application."""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        # Create a rotating file handler for logs
        file_handler = RotatingFileHandler(
            log_dir / 'thesis_submission.log',
            maxBytes=10240,  # 10 KB per log file
            backupCount=10   # Keep the last 10 log files
        )
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # Set the overall logging level
        app.logger.setLevel(logging.INFO)
        app.logger.info('Thesis Submission System startup')

def register_error_handlers(app):
    """Register custom error handlers for the app."""
    from flask import render_template

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        db.session.rollback()  # Rollback in case of database errors
        return render_template('500.html'), 500

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(error):
        """Handle RequestEntityTooLarge errors (file size too large)."""
        flash('File is too large. Maximum allowed size is 16MB.', 'danger')
        return redirect(request.url), 413

