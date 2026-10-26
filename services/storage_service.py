import os
import uuid
from io import BytesIO
from abc import ABC, abstractmethod
from typing import Optional, Tuple

from flask import current_app
from werkzeug.utils import secure_filename

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError


class StorageError(Exception):
    """Base exception for storage operations."""
    pass


class StorageFileNotFoundError(StorageError):
    """Raised when a requested file is not found in storage."""
    pass


class BaseStorageService(ABC):
    """Common interface for local and Azure storage."""

    @abstractmethod
    def save_file(self, user_id: int, file_stream, stored_filename: str) -> int:
        pass

    @abstractmethod
    def get_file_path(self, user_id: int, stored_filename: str) -> str:
        pass

    def get_file_stream(self, user_id: int, stored_filename: str):
        """Open a stored file as a binary stream."""
        return open(self.get_file_path(user_id, stored_filename), "rb")

    @abstractmethod
    def delete_file(self, user_id: int, stored_filename: str) -> bool:
        pass

    @abstractmethod
    def file_exists(self, user_id: int, stored_filename: str) -> bool:
        pass

    @abstractmethod
    def list_stored_files(self, user_id: int) -> list:
        pass

    @staticmethod
    def generate_stored_filename(original_filename: str) -> Tuple[str, str]:
        clean_name = secure_filename(original_filename)
        _, ext = os.path.splitext(clean_name)
        ext = ext.lower()
        return f"{uuid.uuid4().hex}{ext}", ext


class LocalStorageService(BaseStorageService):
    """Store files on the local filesystem."""

    def __init__(self, upload_folder: Optional[str] = None):
        self.upload_folder = os.path.abspath(
            upload_folder or "storage/uploads"
        )
        os.makedirs(self.upload_folder, exist_ok=True)

    def _get_user_directory(self, user_id: int) -> str:
        base = os.path.abspath(self.upload_folder)
        user_dir = os.path.abspath(os.path.join(base, str(user_id)))

        if os.path.commonpath([base, user_dir]) != base:
            raise StorageError("Invalid user storage path.")

        os.makedirs(user_dir, exist_ok=True)
        return user_dir

    def _get_safe_path(self, user_id: int, stored_filename: str) -> str:
        if (
            not stored_filename
            or secure_filename(stored_filename) != stored_filename
            or os.path.basename(stored_filename) != stored_filename
        ):
            raise StorageError("Invalid filename.")

        user_dir = self._get_user_directory(user_id)
        path = os.path.abspath(os.path.join(user_dir, stored_filename))

        if os.path.commonpath([user_dir, path]) != user_dir:
            raise StorageError("Invalid file path.")

        return path

    def save_file(self, user_id: int, file_stream, stored_filename: str) -> int:
        path = self._get_safe_path(user_id, stored_filename)
        if hasattr(file_stream, "seek"):
            file_stream.seek(0)

        total = 0
        with open(path, "wb") as destination:
            while True:
                chunk = file_stream.read(64 * 1024)
                if not chunk:
                    break
                destination.write(chunk)
                total += len(chunk)

        return total

    def get_file_path(self, user_id: int, stored_filename: str) -> str:
        path = self._get_safe_path(user_id, stored_filename)
        if not os.path.isfile(path):
            raise StorageFileNotFoundError("File not found.")
        return path

    def delete_file(self, user_id: int, stored_filename: str) -> bool:
        try:
            path = self._get_safe_path(user_id, stored_filename)
            if os.path.isfile(path):
                os.remove(path)
                return True
            return False
        except (OSError, StorageError):
            return False

    def file_exists(self, user_id: int, stored_filename: str) -> bool:
        try:
            return os.path.isfile(
                self._get_safe_path(user_id, stored_filename)
            )
        except (OSError, StorageError):
            return False

    def list_stored_files(self, user_id: int) -> list:
        user_dir = self._get_user_directory(user_id)
        return [
            name for name in os.listdir(user_dir)
            if os.path.isfile(os.path.join(user_dir, name))
        ]


class AzureBlobStorageService(BaseStorageService):
    """Store private user files in Azure Blob Storage."""

    def __init__(
        self,
        connection_string: Optional[str] = None,
        container_name: str = "cloudvault-files",
    ):
        if not connection_string:
            raise StorageError(
                "Azure connection string is missing. Check your .env settings."
            )

        self.container_name = container_name
        self._service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        self._container = self._service_client.get_container_client(
            container_name
        )

        try:
            self._container.create_container()
        except ResourceExistsError:
            pass

    def _validate_filename(self, stored_filename: str) -> str:
        if (
            not stored_filename
            or secure_filename(stored_filename) != stored_filename
            or os.path.basename(stored_filename) != stored_filename
        ):
            raise StorageError("Invalid filename.")
        return stored_filename

    def _get_blob_name(self, user_id: int, stored_filename: str) -> str:
        safe_name = self._validate_filename(stored_filename)
        return f"users/{int(user_id)}/{safe_name}"

    def save_file(self, user_id: int, file_stream, stored_filename: str) -> int:
        blob_name = self._get_blob_name(user_id, stored_filename)

        if hasattr(file_stream, "seek"):
            file_stream.seek(0)

        blob = self._container.get_blob_client(blob_name)
        blob.upload_blob(file_stream, overwrite=False)

        return blob.get_blob_properties().size

    def get_file_path(self, user_id: int, stored_filename: str) -> str:
        # Azure files do not have a local filesystem path.
        raise NotImplementedError(
            "Use get_file_stream() for Azure Blob Storage."
        )

    def get_file_stream(self, user_id: int, stored_filename: str):
        blob_name = self._get_blob_name(user_id, stored_filename)
        blob = self._container.get_blob_client(blob_name)

        try:
            content = blob.download_blob().readall()
        except ResourceNotFoundError as exc:
            raise StorageFileNotFoundError("File not found in Azure.") from exc

        return BytesIO(content)

    def delete_file(self, user_id: int, stored_filename: str) -> bool:
        blob_name = self._get_blob_name(user_id, stored_filename)
        blob = self._container.get_blob_client(blob_name)

        try:
            blob.delete_blob()
            return True
        except ResourceNotFoundError:
            return False

    def file_exists(self, user_id: int, stored_filename: str) -> bool:
        blob_name = self._get_blob_name(user_id, stored_filename)
        return self._container.get_blob_client(blob_name).exists()

    def list_stored_files(self, user_id: int) -> list:
        prefix = f"users/{int(user_id)}/"
        return [
            item.name[len(prefix):]
            for item in self._container.list_blobs(name_starts_with=prefix)
            if item.name.startswith(prefix)
        ]


def get_storage_service(app=None) -> BaseStorageService:
    """Return the configured storage backend."""
    if app is None:
        app = current_app

    storage_type = app.config.get("STORAGE_TYPE", "local").lower()

    if storage_type == "azure":
        return AzureBlobStorageService(
            connection_string=app.config.get(
                "AZURE_STORAGE_CONNECTION_STRING"
            ),
            container_name=app.config.get(
                "AZURE_CONTAINER_NAME", "cloudvault-files"
            ),
        )

    return LocalStorageService(
        upload_folder=app.config.get("UPLOAD_FOLDER")
    )