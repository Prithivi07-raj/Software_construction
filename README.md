<<<<<<< HEAD
# CloudVault — Secure Cloud Storage System

A modern, secure cloud storage web application developed for the **Software Construction** college project. CloudVault is inspired by enterprise SaaS platforms like Google Drive and Dropbox, offering a responsive user interface, end-to-end user isolation, resilient local file storage, and a modular architecture engineered for future **Microsoft Azure Blob Storage** deployment.

---

## 🌟 Key Features

### 1. Modern SaaS User Interface & Experience
- **Google Drive & Dropbox Inspired Dashboard**: Clean white background with soft blue (`#2563EB`) and deep navy accents (`#0F172A`).
- **Responsive Layout**: Designed for desktop, tablet, and mobile with an off-canvas drawer navigation for small screens.
- **Dynamic File Explorer**: Switch seamlessly between **Grid View** (with image thumbnails and category badges) and **List View** (detailed tabular metrics). Remembers user preference across sessions via `localStorage`.
- **Drag-and-Drop Uploader**: Fast drag-and-drop dropzones both on the dashboard and via a global modal with real-time progress percentages (0%–100%).
- **Interactive Password Guidance**: Real-time password strength meter checking character count, letters, numbers, and symbols.
- **Toast Notifications & Modals**: Auto-dismissing alerts and confirmation dialogs before permanent file deletion.

### 2. File Organization & Exploration
- **Instant Search**: Search files by name with real-time keyword matching.
- **Multi-Field Sorting**: Sort files ascending or descending by upload date, original filename, or file size.
- **Category Filtering**: Filter files into *Documents*, *Spreadsheets*, *Presentations*, *Images*, *Archives*, *Media*, and *Other*.
- **Direct Preview & Safe Download**: In-browser inline preview for images and documents, and secure attachment downloads.

### 3. Rigorous Security & File Isolation
- **Authentication**: Salted password hashing using **Werkzeug** (`scrypt`/`pbkdf2`) and session management with **Flask-Login**.
- **User Ownership Enforcement**: Every file operation verifies `file.user_id == current_user.id` on the server before serving or deleting files. User A can never access or delete User B's files.
- **Storage Obfuscation**: Uploaded files are stored outside the public static directory in `storage/uploads/<user_id>/` with cryptographically random UUID filenames, preventing script execution, directory traversal, and name collisions.
- **CSRF Protection**: All form submissions and AJAX file actions are secured with **Flask-WTF** CSRF tokens.
- **Upload Restrictions**: Backend validation restricts file extensions and enforces both per-file size limits and user storage quotas.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, Modern CSS3 (Variables, Flexbox, Grid), Vanilla JavaScript (ES6+), FontAwesome |
| **Backend Framework** | Python 3.13, Flask 3.1, Jinja2 |
| **Database & ORM** | SQLite, Flask-SQLAlchemy 3.1 |
| **Authentication & Forms** | Flask-Login 0.6, Flask-WTF 1.3, WTForms, Werkzeug Security, email-validator |
| **Storage Architecture** | Abstract `BaseStorageService` with active `LocalStorageService` and prepared `AzureBlobStorageService` |
| **Testing** | pytest 9.1 |

---

## 📁 Project Directory Structure

```text
CloudVault/
├── app.py                     # Application factory, blueprints & error handlers
├── config.py                  # Configurations (Dev, Testing, Prod, Storage, Limits)
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Pytest configuration
├── seed_demo.py               # Presentation demo seeder script
├── .env.example               # Environment variables template
├── .env                       # Local environment settings
├── .gitignore                 # Git ignore rules (secrets, venv, database, storage)
├── README.md                  # Comprehensive documentation
│
├── models/                    # SQLAlchemy database models
│   ├── __init__.py            # Database instance & exports
│   ├── user.py                # User model with password hashing & quota logic
│   └── file.py                # FileRecord model with categorization & size helpers
│
├── services/                  # Business logic & storage adapters
│   ├── __init__.py            # Storage service exports
│   └── storage_service.py     # BaseStorageService, LocalStorageService, AzureBlobStorageService
│
├── forms/                     # Flask-WTF forms & CSRF protection
│   ├── __init__.py            # Forms exports
│   ├── auth_forms.py          # LoginForm, RegistrationForm, ChangePasswordForm
│   └── file_forms.py          # FileUploadForm, DeleteFileForm
│
├── routes/                    # Modular Flask blueprints
│   ├── __init__.py            # Blueprints exports
│   ├── auth.py                # /login, /register, /logout
│   ├── main.py                # /, /dashboard, /profile, /about
│   └── files.py               # /files, upload, download, preview, delete, stats
│
├── templates/                 # Jinja2 HTML templates
│   ├── base.html              # Base shell with sidebar, topbar, modals & toasts
│   ├── login.html             # Login page
│   ├── register.html          # Registration page with strength meter
│   ├── dashboard.html         # User dashboard & metrics breakdown
│   ├── files.html             # File manager (grid & list views, filter, search)
│   ├── profile.html           # User profile, password update & quota stats
│   ├── about.html             # Project architecture & Azure roadmap
│   ├── about_content.html     # Reusable architectural overview component
│   └── errors/                # Custom error pages (400, 403, 404, 413, 500)
│
├── static/                    # Public static assets
│   ├── css/
│   │   └── style.css          # Custom SaaS design system & responsiveness
│   ├── js/
│   │   └── app.js             # Client controller (drag-and-drop, progress, view toggle)
│   └── images/                # Static graphics and icons
│
├── storage/                   # File repository (outside web static root)
│   └── uploads/               # User-isolated directories (<user_id>/<uuid>.<ext>)
│
└── tests/                     # Automated pytest suite
    ├── conftest.py            # Test fixtures (in-memory SQLite, isolated temp storage)
    ├── test_auth.py           # Registration, login, logout, session security
    ├── test_files.py          # Upload, download, ownership isolation, delete, search
    └── test_storage.py        # Local storage lifecycle & path traversal prevention
```

---

## 🚀 Setup & Execution Guide (Windows PowerShell)

Follow these exact commands to set up and run CloudVault locally:

### Step 1: Clone or Navigate to the Workspace
```powershell
cd c:\Users\jdyt1\OneDrive\Desktop\CloudVault
```

### Step 2: Create and Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### Step 3: Install Required Dependencies
```powershell
.\venv\Scripts\pip.exe install -r requirements.txt
```

### Step 4 (Optional): Seed Demo Data for Presentation
Populate the database with a pre-configured user and sample files:
```powershell
.\venv\Scripts\python.exe seed_demo.py
```
> **Demo Account Credentials:**
> - **Email**: `demo@cloudvault.local`
> - **Password**: `Password123!`

### Step 5: Start the Local Application
```powershell
.\venv\Scripts\python.exe app.py
```

Open your browser and navigate to:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🧪 Running the Automated Test Suite

CloudVault includes 18 unit and integration tests covering authentication, upload validation, user file ownership isolation, search/sorting, path traversal defense, and storage service contracts.

To execute the test suite:
```powershell
.\venv\Scripts\python.exe -m pytest -v
```

Expected output:
```text
============================= test session starts =============================
tests/test_auth.py::test_register_success PASSED                         [  5%]
tests/test_auth.py::test_register_duplicate_email PASSED                 [ 11%]
tests/test_auth.py::test_register_password_mismatch PASSED               [ 16%]
tests/test_auth.py::test_login_success PASSED                            [ 22%]
tests/test_auth.py::test_login_invalid_password PASSED                   [ 27%]
tests/test_auth.py::test_logout PASSED                                   [ 33%]
tests/test_auth.py::test_protected_routes_require_login PASSED           [ 38%]
tests/test_files.py::test_upload_file_success PASSED                     [ 44%]
tests/test_files.py::test_upload_ajax PASSED                             [ 50%]
tests/test_files.py::test_upload_disallowed_extension PASSED             [ 55%]
tests/test_files.py::test_download_file PASSED                           [ 61%]
tests/test_files.py::test_file_ownership_isolation PASSED                [ 66%]
tests/test_files.py::test_delete_file_success PASSED                     [ 72%]
tests/test_files.py::test_search_and_filter PASSED                       [ 77%]
tests/test_storage.py::test_local_storage_lifecycle PASSED               [ 83%]
tests/test_storage.py::test_local_storage_path_traversal_prevention PASSED [ 88%]
tests/test_storage.py::test_file_not_found_handling PASSED               [ 94%]
tests/test_storage.py::test_azure_blob_service_contract PASSED           [100%]

============================= 18 passed in 5.3s ===============================
```

---

## ☁️ Microsoft Azure Blob Storage Integration Roadmap (Phase 2)

CloudVault is built from the ground up to support Microsoft Azure Blob Storage without rewriting the presentation or business logic.

### Architectural Adapter Pattern
In `services/storage_service.py`, both local disk storage and cloud storage implement the unified `BaseStorageService` contract:

```python
class BaseStorageService(ABC):
    @abstractmethod
    def save_file(self, user_id: int, file_stream, stored_filename: str) -> int:
        pass

    @abstractmethod
    def get_file_path(self, user_id: int, stored_filename: str) -> str:
        pass

    @abstractmethod
    def delete_file(self, user_id: int, stored_filename: str) -> bool:
        pass

    @abstractmethod
    def file_exists(self, user_id: int, stored_filename: str) -> bool:
        pass
```

### Transitioning to Azure in Phase 2
When transitioning to cloud deployment:
1. **Install the Azure SDK**:
   ```bash
   pip install azure-storage-blob
   ```
2. **Update `.env` configuration**:
   ```ini
   STORAGE_TYPE=azure
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=<storage_account>;AccountKey=<key>;EndpointSuffix=core.windows.net
   AZURE_CONTAINER_NAME=cloudvault-files
   ```
3. **Zero UI or Route Changes**: The factory `get_storage_service()` instantiates `AzureBlobStorageService`, and all existing routes (`upload_file`, `download_file`, `delete_file`) continue operating without alteration.

---

## 🔒 Security Summary

1. **Password Safety**: Uses `werkzeug.security.generate_password_hash` with modern salting. Plaintext passwords are never saved.
2. **Strict Authorization**: Every file query explicitly filters by `user_id == current_user.id`. Direct URL manipulation (`/files/99/download`) cannot access another user's files.
3. **Directory Traversal Mitigation**: File paths are validated with `os.path.abspath` to ensure they never escape the designated user folder.
4. **CSRF Tokens**: All state-modifying requests (`POST`) are protected with CSRF tokens validated by Flask-WTF.
5. **Configurable Limits**: Default upload file cap is 50 MB and user quota is 250 MB, both configurable via environment variables.

---

## 📄 License & Attribution
Developed for the **Software Construction** college curriculum. All rights reserved &copy; 2026.
=======
# Software_construction
>>>>>>> github/main
