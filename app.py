import os
from flask import Flask, render_template, jsonify
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import config_by_name
from models import db, User
from routes import auth_bp, main_bp, files_bp

login_manager = LoginManager()
csrf = CSRFProtect()


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    return db.session.get(User, int(user_id))


def create_app(config_name=None) -> Flask:
    """
    Application factory for CloudVault.
    Initializes configurations, extensions, blueprints, and error handlers.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    config_class = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_class)

    # Ensure required runtime directories exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please sign in to access your secure CloudVault."
    login_manager.login_message_category = "info"

    # Register modular blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(files_bp)

    # Context processors for templates
    @app.context_processor
    def inject_global_vars():
        return {
            'app_name': 'CloudVault',
            'app_tagline': 'Secure Cloud Storage System',
            'storage_mode': app.config.get('STORAGE_TYPE', 'local').upper(),
            'max_upload_mb': int(app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024) / (1024 * 1024))
        }

    # Error Handlers
    @app.errorhandler(400)
    def bad_request(error):
        return render_template('errors/400.html', description=getattr(error, 'description', 'Bad Request')), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html', description=getattr(error, 'description', 'Forbidden')), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html', description=getattr(error, 'description', 'Page Not Found')), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return render_template('errors/413.html', description="Uploaded file exceeds the maximum allowed size limit."), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html', description="An internal server error occurred. Please try again later."), 500

    # Initialize database tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    # Keep debug mode disabled by default as requested in guidelines
    app.run(host='127.0.0.1', port=5000, debug=False)
