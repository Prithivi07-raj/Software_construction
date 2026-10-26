import io
import os
import pytest
from services.storage_service import (
    LocalStorageService,
    AzureBlobStorageService,
    StorageError,
    StorageFileNotFoundError
)


def test_local_storage_lifecycle(temp_storage):
    """Test saving, checking existence, reading path, and deleting files."""
    service = LocalStorageService(upload_folder=temp_storage)
    user_id = 99
    stored_name, ext = service.generate_stored_filename("my document.pdf")

    assert ext == ".pdf"
    assert len(stored_name) > 10

    # 1. Save file
    content = b"Sample binary or text content"
    stream = io.BytesIO(content)
    bytes_written = service.save_file(user_id, stream, stored_name)
    assert bytes_written == len(content)

    # 2. Check existence
    assert service.file_exists(user_id, stored_name) is True

    # 3. Get path and verify content on disk
    path = service.get_file_path(user_id, stored_name)
    assert os.path.exists(path)
    with open(path, 'rb') as f:
        assert f.read() == content

    # 4. List files
    file_list = service.list_stored_files(user_id)
    assert stored_name in file_list

    # 5. Delete file
    deleted = service.delete_file(user_id, stored_name)
    assert deleted is True
    assert service.file_exists(user_id, stored_name) is False


def test_local_storage_path_traversal_prevention(temp_storage):
    """
    CRITICAL SECURITY TEST:
    Verify LocalStorageService refuses paths attempting directory traversal.
    """
    service = LocalStorageService(upload_folder=temp_storage)
    user_id = 1

    # Malicious filenames trying to write outside user directory
    traversal_names = [
        "../evil.txt",
        "..\\evil.txt",
        "/etc/passwd",
        "C:\\Windows\\System32\\cmd.exe",
        "../../outside.txt"
    ]

    for malicious_name in traversal_names:
        with pytest.raises(StorageError):
            service.save_file(user_id, io.BytesIO(b"evil"), malicious_name)

        with pytest.raises(StorageError):
            service.get_file_path(user_id, malicious_name)


def test_file_not_found_handling(temp_storage):
    """Verify non-existent files raise clean StorageFileNotFoundError."""
    service = LocalStorageService(upload_folder=temp_storage)
    with pytest.raises(StorageFileNotFoundError):
        service.get_file_path(user_id=1, stored_filename="non_existent_file.pdf")



def test_azure_blob_service_contract():
    """Verify missing Azure configuration is handled clearly."""
    with pytest.raises(StorageError, match="Azure connection string is missing"):
        AzureBlobStorageService(
            connection_string=None,
            container_name="test-container",
        )
