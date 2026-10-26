from datetime import datetime, timezone
from . import db


class FileRecord(db.Model):
    """Metadata record for files uploaded by authenticated users."""
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), unique=True, nullable=False, index=True)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    file_extension = db.Column(db.String(20), nullable=False, default='')
    mime_type = db.Column(db.String(100), nullable=False, default='application/octet-stream')
    category = db.Column(db.String(50), nullable=False, default='other', index=True)
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    @classmethod
    def categorize_extension(cls, ext: str) -> str:
        """Determine category string based on file extension."""
        ext = ext.lower().lstrip('.')
        categories = {
            'document': {'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'md', 'json', 'xml', 'csv', 'tsv'},
            'spreadsheet': {'xls', 'xlsx'},
            'presentation': {'ppt', 'pptx'},
            'image': {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'bmp', 'ico'},
            'archive': {'zip', 'rar', '7z', 'tar', 'gz'},
            'media': {'mp3', 'wav', 'ogg', 'mp4', 'mov', 'webm', 'm4a'}
        }
        for cat, extensions in categories.items():
            if ext in extensions:
                return cat
        return 'other'

    @property
    def formatted_size(self) -> str:
        """Return human-readable file size."""
        num_bytes = self.file_size
        if num_bytes < 1024:
            return f"{num_bytes} B"
        elif num_bytes < 1024 * 1024:
            return f"{num_bytes / 1024:.1f} KB"
        elif num_bytes < 1024 * 1024 * 1024:
            return f"{num_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{num_bytes / (1024 * 1024 * 1024):.2f} GB"

    @property
    def is_image(self) -> bool:
        """Check if file is an image."""
        return self.category == 'image'

    @property
    def is_previewable(self) -> bool:
        """Check if file can be previewed directly in the browser."""
        ext = self.file_extension.lower().lstrip('.')
        return ext in {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp', 'pdf', 'txt'}

    @property
    def icon_class(self) -> str:
        """Return CSS class for category icon."""
        icons = {
            'document': 'file-text',
            'spreadsheet': 'sheet',
            'presentation': 'presentation',
            'image': 'image',
            'archive': 'archive',
            'media': 'film',
            'other': 'file'
        }
        return icons.get(self.category, 'file')

    def to_dict(self) -> dict:
        """Serialize file record for JSON responses."""
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_size': self.file_size,
            'formatted_size': self.formatted_size,
            'file_extension': self.file_extension,
            'mime_type': self.mime_type,
            'category': self.category,
            'is_image': self.is_image,
            'is_previewable': self.is_previewable,
            'uploaded_at': self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self) -> str:
        return f"<FileRecord {self.id}: {self.original_filename} ({self.formatted_size})>"
