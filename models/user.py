from datetime import datetime, timezone
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from . import db


class User(UserMixin, db.Model):
    """User account model with secure password hashing and storage tracking."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to user's uploaded files
    files = db.relationship(
        'FileRecord',
        backref='owner',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def set_password(self, password: str) -> None:
        """Hash and store password securely."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify candidate password against stored hash."""
        return check_password_hash(self.password_hash, password)

    def get_storage_used_bytes(self) -> int:
        """Calculate total storage in bytes used by this user."""
        from .file import FileRecord
        total = db.session.query(func.coalesce(func.sum(FileRecord.file_size), 0))\
            .filter(FileRecord.user_id == self.id)\
            .scalar()
        return int(total or 0)

    def get_storage_quota_bytes(self) -> int:
        """Get the configured quota limit for this user."""
        return current_app.config.get('USER_STORAGE_QUOTA_BYTES', 250 * 1024 * 1024)

    def get_storage_percentage(self) -> float:
        """Calculate percentage of storage quota used."""
        quota = self.get_storage_quota_bytes()
        if quota <= 0:
            return 0.0
        used = self.get_storage_used_bytes()
        return min(round((used / quota) * 100, 1), 100.0)

    def get_formatted_storage_used(self) -> str:
        """Return human-readable representation of used storage."""
        bytes_val = self.get_storage_used_bytes()
        return self._format_bytes(bytes_val)

    def get_formatted_storage_quota(self) -> str:
        """Return human-readable representation of total quota."""
        bytes_val = self.get_storage_quota_bytes()
        return self._format_bytes(bytes_val)

    @staticmethod
    def _format_bytes(num_bytes: int) -> str:
        """Helper to format raw bytes into KB, MB, or GB."""
        if num_bytes < 1024:
            return f"{num_bytes} B"
        elif num_bytes < 1024 * 1024:
            return f"{num_bytes / 1024:.1f} KB"
        elif num_bytes < 1024 * 1024 * 1024:
            return f"{num_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{num_bytes / (1024 * 1024 * 1024):.2f} GB"

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.full_name})>"
