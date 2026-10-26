/**
 * CloudVault — Secure Cloud Storage System
 * Modern Client-Side Controller (Vanilla JavaScript)
 */

(function () {
    'use strict';

    // Global namespace for CloudVault helper functions
    window.CloudVault = window.CloudVault || {};

    // Retrieve CSRF token from page meta tag
    function getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        return meta ? meta.getAttribute('content') : '';
    }

    // =========================================================================
    // 1. Toast Notification Manager
    // =========================================================================
    function showToast(message, type = 'info', duration = 4500) {
        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `toast toast-${type} animate-slide-in`;

        let iconClass = 'fa-solid fa-circle-info';
        if (type === 'success') iconClass = 'fa-solid fa-circle-check';
        else if (type === 'danger') iconClass = 'fa-solid fa-circle-exclamation';
        else if (type === 'warning') iconClass = 'fa-solid fa-triangle-exclamation';

        toast.innerHTML = `
            <div class="toast-icon"><i class="${iconClass}"></i></div>
            <div class="toast-message">${escapeHtml(message)}</div>
            <button type="button" class="toast-close" aria-label="Close notification">
                <i class="fa-solid fa-xmark"></i>
            </button>
        `;

        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            toast.remove();
        });

        container.appendChild(toast);

        if (duration > 0) {
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.style.opacity = '0';
                    toast.style.transform = 'translateX(20px)';
                    toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    setTimeout(() => toast.remove(), 300);
                }
            }, duration);
        }
    }
    window.CloudVault.showToast = showToast;

    // Auto-dismiss initial server flash messages
    document.addEventListener('DOMContentLoaded', () => {
        const serverToasts = document.querySelectorAll('.toast');
        serverToasts.forEach(toast => {
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.style.opacity = '0';
                    toast.style.transform = 'translateX(20px)';
                    toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    setTimeout(() => toast.remove(), 300);
                }
            }, 4500);
        });
    });

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // =========================================================================
    // 2. Password Visibility Toggle
    // =========================================================================
    document.addEventListener('DOMContentLoaded', () => {
        const toggleButtons = document.querySelectorAll('.btn-password-toggle');
        toggleButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = btn.getAttribute('data-target');
                const input = document.getElementById(targetId);
                const icon = btn.querySelector('.eye-icon');
                if (!input) return;

                if (input.type === 'password') {
                    input.type = 'text';
                    if (icon) {
                        icon.classList.remove('fa-eye');
                        icon.classList.add('fa-eye-slash');
                    }
                } else {
                    input.type = 'password';
                    if (icon) {
                        icon.classList.remove('fa-eye-slash');
                        icon.classList.add('fa-eye');
                    }
                }
            });
        });
    });

    // =========================================================================
    // 3. Real-Time Password Strength Checker
    // =========================================================================
    function setupPasswordStrength(inputId, containerId, barId, textId, rulePrefix = 'rule') {
        const input = document.getElementById(inputId);
        const container = document.getElementById(containerId);
        const bar = document.getElementById(barId);
        const text = document.getElementById(textId);
        const ruleLength = document.getElementById(`${rulePrefix}Length`);
        const ruleLetter = document.getElementById(`${rulePrefix}Letter`);
        const ruleNumber = document.getElementById(`${rulePrefix}Number`);

        if (!input || !container || !bar || !text) return;

        input.addEventListener('input', () => {
            const val = input.value;
            if (!val) {
                container.style.display = 'none';
                return;
            }

            container.style.display = 'block';

            let score = 0;
            const hasLength = val.length >= 8;
            const hasLetter = /[A-Za-z]/.test(val);
            const hasNumber = /\d/.test(val);
            const hasSpecial = /[^A-Za-z0-9]/.test(val);

            // Update rule items
            if (ruleLength) updateRule(ruleLength, hasLength);
            if (ruleLetter) updateRule(ruleLetter, hasLetter);
            if (ruleNumber) updateRule(ruleNumber, hasNumber);

            if (hasLength) score++;
            if (hasLetter) score++;
            if (hasNumber) score++;
            if (hasSpecial && val.length >= 10) score++;

            bar.className = 'strength-bar';
            if (score <= 1) {
                bar.classList.add('weak');
                text.textContent = 'Weak password';
                text.style.color = 'var(--danger)';
            } else if (score === 2 || score === 3) {
                bar.classList.add('medium');
                text.textContent = 'Fair password';
                text.style.color = 'var(--warning)';
            } else {
                bar.classList.add('strong');
                text.textContent = 'Strong password';
                text.style.color = 'var(--success)';
            }
        });

        function updateRule(element, isValid) {
            const icon = element.querySelector('i');
            if (isValid) {
                element.classList.add('valid');
                if (icon) {
                    icon.className = 'fa-solid fa-check';
                }
            } else {
                element.classList.remove('valid');
                if (icon) {
                    icon.className = 'fa-solid fa-circle-notch';
                }
            }
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        // Registration page password
        setupPasswordStrength('regPassword', 'pwdStrengthBox', 'strengthBar', 'strengthText', 'rule');
        // Profile page new password
        setupPasswordStrength('newPassword', 'newPwdStrengthBox', 'newStrengthBar', 'newStrengthText', 'newRule');
    });

    // =========================================================================
    // 4. Modal Management (Upload & Delete)
    // =========================================================================
    const uploadModal = document.getElementById('uploadModal');
    const deleteModal = document.getElementById('deleteModal');

    function openUploadModal() {
        if (!uploadModal) return;
        uploadModal.classList.add('show');
        uploadModal.setAttribute('aria-hidden', 'false');
    }
    window.CloudVault.openUploadModal = openUploadModal;

    function closeUploadModal() {
        if (!uploadModal) return;
        uploadModal.classList.remove('show');
        uploadModal.setAttribute('aria-hidden', 'true');
        // Reset queue if needed
        const queue = document.getElementById('uploadQueue');
        if (queue) queue.style.display = 'none';
        const fileInput = document.getElementById('modalFileInput');
        if (fileInput) fileInput.value = '';
    }
    window.CloudVault.closeUploadModal = closeUploadModal;

    function openDeleteModal(fileId, filename) {
        if (!deleteModal) return;
        const targetFilenameSpan = document.getElementById('deleteFilenameTarget');
        const deleteForm = document.getElementById('deleteFileForm');
        if (targetFilenameSpan) targetFilenameSpan.textContent = `"${filename}"`;
        if (deleteForm) {
            deleteForm.action = `/files/${fileId}/delete`;
        }
        deleteModal.classList.add('show');
        deleteModal.setAttribute('aria-hidden', 'false');
    }
    window.CloudVault.openDeleteModal = openDeleteModal;

    function closeDeleteModal() {
        if (!deleteModal) return;
        deleteModal.classList.remove('show');
        deleteModal.setAttribute('aria-hidden', 'true');
    }
    window.CloudVault.closeDeleteModal = closeDeleteModal;

    document.addEventListener('DOMContentLoaded', () => {
        // Modal trigger buttons
        document.querySelectorAll('.upload-trigger-btn').forEach(btn => {
            btn.addEventListener('click', openUploadModal);
        });

        const closeUploadBtn = document.getElementById('closeUploadModalBtn');
        const cancelUploadBtn = document.getElementById('cancelUploadModalBtn');
        if (closeUploadBtn) closeUploadBtn.addEventListener('click', closeUploadModal);
        if (cancelUploadBtn) cancelUploadBtn.addEventListener('click', closeUploadModal);

        const cancelDeleteBtn = document.getElementById('cancelDeleteModalBtn');
        if (cancelDeleteBtn) cancelDeleteBtn.addEventListener('click', closeDeleteModal);

        // Close on clicking backdrop
        window.addEventListener('click', (e) => {
            if (e.target === uploadModal) closeUploadModal();
            if (e.target === deleteModal) closeDeleteModal();
        });

        // Close on Escape key
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                closeUploadModal();
                closeDeleteModal();
            }
        });
    });

    // =========================================================================
    // 5. File Upload Handler (AJAX with Real Progress)
    // =========================================================================
    function uploadSingleFile(file, onProgress, onComplete, onError) {
        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/files/upload', true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        xhr.setRequestHeader('X-CSRFToken', getCsrfToken());

        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable && onProgress) {
                const percent = Math.round((e.loaded / e.total) * 100);
                onProgress(percent);
            }
        };

        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (onComplete) onComplete(response);
                } catch (err) {
                    if (onComplete) onComplete({ success: true });
                }
            } else {
                let errorMsg = 'Upload failed.';
                try {
                    const res = JSON.parse(xhr.responseText);
                    if (res.message) errorMsg = res.message;
                } catch (e) {}
                if (onError) onError(errorMsg);
            }
        };

        xhr.onerror = () => {
            if (onError) onError('Network error occurred during upload.');
        };

        xhr.send(formData);
    }

    // Modal Dropzone Integration
    document.addEventListener('DOMContentLoaded', () => {
        const modalDropzone = document.getElementById('modalDropzone');
        const modalFileInput = document.getElementById('modalFileInput');
        const startUploadBtn = document.getElementById('startUploadBtn');
        const uploadQueue = document.getElementById('uploadQueue');
        const queueItemsList = document.getElementById('queueItemsList');
        const queueCount = document.getElementById('queueCount');

        let selectedFiles = [];

        if (modalDropzone && modalFileInput) {
            modalDropzone.addEventListener('click', () => modalFileInput.click());

            ['dragenter', 'dragover'].forEach(eventName => {
                modalDropzone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    modalDropzone.classList.add('dragover');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                modalDropzone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    modalDropzone.classList.remove('dragover');
                }, false);
            });

            modalDropzone.addEventListener('drop', (e) => {
                const dt = e.dataTransfer;
                const files = dt.files;
                handleSelectedFiles(files);
            });

            modalFileInput.addEventListener('change', (e) => {
                handleSelectedFiles(e.target.files);
            });
        }

        function handleSelectedFiles(files) {
            if (!files || files.length === 0) return;
            selectedFiles = Array.from(files);

            if (uploadQueue && queueItemsList && queueCount) {
                uploadQueue.style.display = 'block';
                queueCount.textContent = `0 / ${selectedFiles.length}`;
                queueItemsList.innerHTML = '';

                selectedFiles.forEach((f, idx) => {
                    const item = document.createElement('div');
                    item.className = 'queue-item';
                    item.id = `queueItem_${idx}`;
                    item.innerHTML = `
                        <div class="queue-item-header">
                            <span class="queue-filename">${escapeHtml(f.name)}</span>
                            <span class="queue-status" id="queueStatus_${idx}">Ready</span>
                        </div>
                        <div class="queue-item-progress">
                            <div class="queue-item-progress-fill" id="queueProgressFill_${idx}" style="width: 0%;"></div>
                        </div>
                    `;
                    queueItemsList.appendChild(item);
                });
            }

            if (startUploadBtn) {
                startUploadBtn.disabled = false;
            }
        }

        if (startUploadBtn) {
            startUploadBtn.addEventListener('click', () => {
                if (selectedFiles.length === 0) return;
                startUploadBtn.disabled = true;

                let completedCount = 0;
                let failedCount = 0;

                function uploadNext(index) {
                    if (index >= selectedFiles.length) {
                        showToast(`Successfully uploaded ${completedCount} file(s)!`, 'success');
                        setTimeout(() => window.location.reload(), 1200);
                        return;
                    }

                    const file = selectedFiles[index];
                    const statusSpan = document.getElementById(`queueStatus_${index}`);
                    const progressFill = document.getElementById(`queueProgressFill_${index}`);

                    if (statusSpan) statusSpan.textContent = 'Uploading...';

                    uploadSingleFile(
                        file,
                        (percent) => {
                            if (progressFill) progressFill.style.width = `${percent}%`;
                            if (statusSpan) statusSpan.textContent = `${percent}%`;
                        },
                        (res) => {
                            completedCount++;
                            if (queueCount) queueCount.textContent = `${completedCount} / ${selectedFiles.length}`;
                            if (statusSpan) {
                                statusSpan.textContent = 'Uploaded';
                                statusSpan.style.color = 'var(--success)';
                            }
                            if (progressFill) {
                                progressFill.style.width = '100%';
                                progressFill.style.backgroundColor = 'var(--success)';
                            }
                            uploadNext(index + 1);
                        },
                        (err) => {
                            failedCount++;
                            if (statusSpan) {
                                statusSpan.textContent = 'Failed';
                                statusSpan.style.color = 'var(--danger)';
                            }
                            if (progressFill) {
                                progressFill.style.backgroundColor = 'var(--danger)';
                            }
                            showToast(`Failed uploading ${file.name}: ${err}`, 'danger');
                            uploadNext(index + 1);
                        }
                    );
                }

                uploadNext(0);
            });
        }
    });

    // Dashboard Inline Dropzone
    document.addEventListener('DOMContentLoaded', () => {
        const dashDropzone = document.getElementById('dashboardDropzone');
        const dashFileInput = document.getElementById('dashboardFileInput');
        const dashProgress = document.getElementById('dashboardProgressContainer');
        const dashFilename = document.getElementById('dashboardProgressFilename');
        const dashPercent = document.getElementById('dashboardProgressPercent');
        const dashFill = document.getElementById('dashboardProgressFill');

        if (!dashDropzone || !dashFileInput) return;

        dashDropzone.addEventListener('click', (e) => {
            if (e.target.tagName !== 'INPUT') {
                dashFileInput.click();
            }
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dashDropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dashDropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dashDropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dashDropzone.classList.remove('dragover');
            }, false);
        });

        dashDropzone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
                processInlineUpload(files[0]);
            }
        });

        dashFileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files.length > 0) {
                processInlineUpload(e.target.files[0]);
            }
        });

        function processInlineUpload(file) {
            if (dashProgress) dashProgress.style.display = 'block';
            if (dashFilename) dashFilename.textContent = `Uploading "${file.name}"...`;

            uploadSingleFile(
                file,
                (percent) => {
                    if (dashPercent) dashPercent.textContent = `${percent}%`;
                    if (dashFill) dashFill.style.width = `${percent}%`;
                },
                (res) => {
                    if (dashPercent) dashPercent.textContent = '100%';
                    if (dashFill) {
                        dashFill.style.width = '100%';
                        dashFill.style.backgroundColor = 'var(--success)';
                    }
                    showToast(`"${file.name}" uploaded successfully!`, 'success');
                    setTimeout(() => window.location.reload(), 1200);
                },
                (err) => {
                    if (dashPercent) dashPercent.textContent = 'Failed';
                    if (dashFill) dashFill.style.backgroundColor = 'var(--danger)';
                    showToast(err, 'danger');
                }
            );
        }
    });

    // =========================================================================
    // 6. View Switcher (Grid vs List) with Memory
    // =========================================================================
    document.addEventListener('DOMContentLoaded', () => {
        const gridBtn = document.getElementById('viewGridBtn');
        const listBtn = document.getElementById('viewListBtn');
        const gridView = document.getElementById('filesGridView');
        const listView = document.getElementById('filesListView');
        const viewInput = document.getElementById('viewInput');

        if (!gridBtn || !listBtn || !gridView || !listView) return;

        function setView(mode) {
            if (mode === 'list') {
                gridView.classList.add('d-none');
                listView.classList.remove('d-none');
                listBtn.classList.add('active');
                gridBtn.classList.remove('active');
                if (viewInput) viewInput.value = 'list';
                localStorage.setItem('cloudvault_view', 'list');
            } else {
                listView.classList.add('d-none');
                gridView.classList.remove('d-none');
                gridBtn.classList.add('active');
                listBtn.classList.remove('active');
                if (viewInput) viewInput.value = 'grid';
                localStorage.setItem('cloudvault_view', 'grid');
            }
        }

        gridBtn.addEventListener('click', () => setView('grid'));
        listBtn.addEventListener('click', () => setView('list'));

        // Restore view preference from localStorage if URL didn't specify explicitly
        const urlParams = new URLSearchParams(window.location.search);
        if (!urlParams.has('view')) {
            const savedView = localStorage.getItem('cloudvault_view');
            if (savedView) {
                setView(savedView);
            }
        }
    });

    // =========================================================================
    // 7. Mobile Sidebar Drawer & User Dropdown
    // =========================================================================
    document.addEventListener('DOMContentLoaded', () => {
        const sidebar = document.getElementById('sidebar');
        const openBtn = document.getElementById('sidebarOpenBtn');
        const closeBtn = document.getElementById('sidebarCloseBtn');

        if (sidebar && openBtn) {
            openBtn.addEventListener('click', () => {
                sidebar.classList.add('open');
            });
        }

        if (sidebar && closeBtn) {
            closeBtn.addEventListener('click', () => {
                sidebar.classList.remove('open');
            });
        }

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (sidebar && sidebar.classList.contains('open')) {
                if (!sidebar.contains(e.target) && openBtn && !openBtn.contains(e.target)) {
                    sidebar.classList.remove('open');
                }
            }
        });

        // User profile menu toggle
        const userMenuToggle = document.getElementById('userMenuToggle');
        const userMenuDropdown = document.getElementById('userMenuDropdown');

        if (userMenuToggle && userMenuDropdown) {
            userMenuToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                userMenuDropdown.classList.toggle('show');
            });

            document.addEventListener('click', (e) => {
                if (!userMenuDropdown.contains(e.target) && !userMenuToggle.contains(e.target)) {
                    userMenuDropdown.classList.remove('show');
                }
            });
        }
    });

})();
