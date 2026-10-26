import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env if present
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    """Base configuration with sensible secure defaults."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cloudvault-dev-secret-key-change-in-prod-2026')
    
    # SQLite Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f'sqlite:///{os.path.join(basedir, "instance", "cloudvault.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Storage Configuration
    STORAGE_TYPE = os.environ.get('STORAGE_TYPE', 'local')  # 'local' or 'azure'
    UPLOAD_FOLDER = os.path.join(basedir, os.environ.get('UPLOAD_FOLDER', 'storage/uploads'))
    
    # Max file upload size limit (Default: 50 MB)
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))
    
    # User storage quota limit (Default: 250 MB per user)
    USER_STORAGE_QUOTA_BYTES = int(os.environ.get('USER_STORAGE_QUOTA_BYTES', 250 * 1024 * 1024))
    
    # Allowed file extensions for security
    ALLOWED_EXTENSIONS = {
        # Documents
        'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'csv', 'tsv', 'json', 'xml', 'md',
        # Spreadsheets & Presentations
        'xls', 'xlsx', 'ppt', 'pptx',
        # Images
        'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp', 'ico',
        # Archives
        'zip', 'rar', '7z', 'tar', 'gz',
        # Audio / Video
        'mp3', 'wav', 'ogg', 'mp4', 'mov', 'webm', 'm4a'
    }
    
    # Session & Security Settings
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # Azure Blob Storage (Future Integration place-holders)
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get('AZURE_STORAGE_CONNECTION_STRING', None)
    AZURE_CONTAINER_NAME = os.environ.get('AZURE_CONTAINER_NAME', 'cloudvault-files')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = False  # Keep debug mode disabled by default as requested


class TestingConfig(Config):
    """Testing configuration with in-memory SQLite and isolated temp storage."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF in tests for simpler unit testing
    USER_STORAGE_QUOTA_BYTES = 50 * 1024 * 1024  # 50 MB for tests


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True  # Require HTTPS in production


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
