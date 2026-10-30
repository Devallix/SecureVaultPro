is t# SecureVault Pro

**Protect Everything. Trust Nothing.**

---

## Overview

SecureVault Pro is an enterprise-grade file encryption and password management desktop application built with Python 3.13+ and PySide6. It provides a unified, encrypted vault for passwords, secure notes, files, digital identities, and more -- all protected by a single master password and strong cryptographic primitives.

---

## Features

### Password Vault

- Full CRUD operations for password entries
- Organise entries by categories and tags
- Favourites for quick access
- Password history tracking with configurable retention
- Expiration warnings for aged credentials
- Password strength analysis and scoring

### Password Generator

- Random character mode with configurable character sets
- Passphrase mode using random wordlists
- Entropy calculation and real-time strength meter
- Adjustable length (8-128 characters)

### Secure Notes

- Markdown editing and rendering support
- End-to-end encryption at rest
- Rich text formatting via built-in markdown editor

### File Encryption

- Single file, batch, and folder encryption/decryption
- Streaming encryption for large files (up to 2 GB)
- Secure delete with multi-pass overwriting
- Configurable chunk processing (64 KB default)

### Digital Identity Management

- SSH key storage and management
- API key vault with metadata
- Software licence tracking

### Security Centre

- Weak password detection
- Duplicate and reused password identification
- Old credential warnings
- Overall vault health score

### Backup & Restore

- Encrypted backup creation and restoration
- Versioned backups with configurable retention (up to 10 versions)
- Scheduled automatic backups
- Restore wizard for guided recovery

### Audit Log

- All security-relevant events are tracked
- Configurable retention period (365 days default)
- Filterable and searchable audit entries

### Reporting

- Export reports in CSV, Excel (XLSX), and PDF formats
- Password inventory, security posture, and audit summaries

### Global Search

- Search across passwords, notes, files, and digital identities
- Instant results as you type

### Import / Export

- Import from CSV and JSON formats
- Export vault data to CSV and JSON
- KeePass compatibility (planned)

### Settings

- Appearance preferences (dark/light theme)
- Security settings (auto-lock timeout, clipboard clearing)
- Notification preferences
- Backup schedule configuration

### Additional Features

- Dark and light theme support
- Auto-lock timer (configurable, 300 seconds default)
- Notification centre for security alerts
- High-DPI display support
- 24-word recovery key for emergency access

---

## Architecture

SecureVault Pro follows a layered architecture with clear separation of concerns:

```
Presentation         PySide6 Widgets, Dialogs, Views
                          |
ViewModels            State management, Qt signals/slots
                          |
Application Services  Business logic, orchestration
                          |
Security Services     Crypto engine, KDF, vault locking
                          |
Repositories          Data access, field-level encrypt/decrypt
                          |
Database              SQLAlchemy ORM + SQLite
```

Each layer depends only on the layer directly below it. The UI layer never accesses repositories or the database directly. All sensitive data is encrypted at the application layer before being written to SQLite.

---

## Tech Stack

| Component        | Technology                                |
| ---------------- | ----------------------------------------- |
| Language         | Python 3.13+                              |
| GUI Framework    | PySide6 6.11+                             |
| ORM              | SQLAlchemy 2.0+                           |
| Database         | SQLite (app-layer encryption)             |
| Migrations       | Alembic                                   |
| Symmetric Crypto | cryptography (AES-256-GCM, ChaCha20-Poly1305) |
| Asymmetric Crypto| cryptography (RSA-4096, Ed25519, X25519)  |
| Hashing          | cryptography (SHA-2, SHA-3, BLAKE2)       |
| KDF              | argon2-cffi (Argon2id), scrypt, HKDF, PBKDF2 |
| Secure Random    | cryptography, PyNaCl                      |
| Clipboard        | pyperclip                                 |
| PDF Reports      | reportlab                                 |
| Excel Reports    | openpyxl                                  |
| Logging          | loguru                                    |
| Testing          | pytest, pytest-qt, hypothesis             |
| Linting          | ruff, black, mypy                         |
| Build            | setuptools                                |

---

## Getting Started

### Prerequisites

- Python 3.13 or later
- pip (latest recommended)

### Installation

Clone the repository and install in editable mode with development dependencies:

```bash
git clone <repository-url>
cd "Secure Vault Application"
pip install -e ".[dev]"
```

### Running the Application

```bash
python main.py
```

On first launch, the vault creation wizard will guide you through setting a master password. Subsequent launches will present the unlock dialog.

### Running Tests

```bash
pytest
```

Tests are located in `app/tests/` and include unit, integration, and GUI test suites.

---

## Project Structure

```
.
├── main.py                         Application entry point
├── pyproject.toml                  Project metadata and dependencies
├── alembic.ini                     Alembic migration configuration
├── requirements.txt                Pinned dependencies
├── docs/
│   └── IMPLEMENTATION_PLAN.md      Development roadmap
├── resources/                      Static assets (icons, images)
└── app/
    ├── authentication/             Master password, vault lock/unlock, recovery
    │   ├── master_password.py
    │   ├── vault_lock.py
    │   ├── vault_unlock.py
    │   ├── password_change.py
    │   └── recovery_key.py
    ├── config/                     Application configuration
    ├── core/                       Constants, exceptions, session, DI container
    │   ├── constants.py
    │   ├── config.py
    │   ├── session.py
    │   ├── app_container.py
    │   ├── crash_handler.py
    │   └── exceptions.py
    ├── database/                   SQLAlchemy engine, session factory, base model
    │   ├── engine.py
    │   ├── session_factory.py
    │   └── base.py
    ├── logging/                    Loguru-based logging with security filters
    │   └── logger.py
    ├── models/                     ORM models
    │   ├── vault.py
    │   ├── password.py
    │   ├── password_history.py
    │   ├── secure_note.py
    │   ├── file_metadata.py
    │   ├── category.py
    │   ├── tag.py
    │   ├── ssh_key.py
    │   ├── api_key.py
    │   ├── software_licence.py
    │   ├── audit_log.py
    │   ├── security_event.py
    │   ├── backup_history.py
    │   ├── recovery_key.py
    │   └── user_settings.py
    ├── repositories/               Data access layer with generic CRUD
    │   ├── base_repository.py
    │   ├── vault_repository.py
    │   ├── password_repository.py
    │   ├── note_repository.py
    │   ├── file_repository.py
    │   ├── category_repository.py
    │   ├── tag_repository.py
    │   ├── ssh_key_repository.py
    │   ├── api_key_repository.py
    │   ├── software_licence_repository.py
    │   ├── audit_repository.py
    │   └── settings_repository.py
    ├── security/                   Cryptographic engine and utilities
    │   ├── crypto_engine.py        Unified crypto facade
    │   ├── symmetric.py            AES-256-GCM, ChaCha20-Poly1305
    │   ├── asymmetric.py           RSA-4096, Ed25519, X25519
    │   ├── kdf.py                  Argon2id, scrypt, HKDF, PBKDF2
    │   ├── hashing.py              SHA-2, SHA-3, BLAKE2
    │   ├── vault_crypto.py         Versioned vault encryption
    │   ├── secure_random.py        Cryptographic random generation
    │   ├── secure_memory.py        Sensitive data handling
    │   ├── clipboard_manager.py    Auto-clearing clipboard
    │   └── integrity.py            Data integrity verification
    ├── services/                   Business logic layer
    │   ├── password_service.py
    │   ├── note_service.py
    │   ├── file_service.py
    │   ├── backup_service.py
    │   ├── audit_service.py
    │   ├── search_service.py
    │   ├── report_service.py
    │   ├── import_export_service.py
    │   └── security_analysis.py
    ├── ui/                         PySide6 presentation layer
    │   ├── main_window.py
    │   ├── splash_screen.py
    │   ├── dialogs/                Modal dialogs (create vault, unlock, generator)
    │   ├── widgets/                Reusable widgets (markdown editor, notifications)
    │   ├── views/                  Main workspace views (dashboard, passwords, notes, files, etc.)
    │   ├── viewmodels/             State management for each view
    │   └── themes/                 Dark/light theme manager
    ├── utils/                      Validators, formatters, platform utilities
    │   ├── validators.py
    │   ├── formatters.py
    │   ├── platform_utils.py
    │   ├── secure_delete.py
    │   └── constants.py
    ├── workers/                    Background thread workers
    │   ├── base_worker.py
    │   ├── thread_pool.py
    │   ├── encryption_worker.py
    │   ├── backup_worker.py
    │   ├── scheduled_backup_worker.py
    │   ├── report_worker.py
    │   └── analysis_worker.py
    └── tests/                      Test suites
        ├── conftest.py
        ├── unit/
        ├── integration/
        └── gui/
```

---

## Security

### Encryption at Rest

All sensitive data is encrypted at the application layer before being written to the SQLite database. Fields such as passwords, notes, file data, and API keys are individually encrypted with per-entry random nonces.

### Algorithms

- **AES-256-GCM** -- Default symmetric cipher (crypto version 1). Provides authenticated encryption with associated data.
- **ChaCha20-Poly1305** -- Alternative symmetric cipher (crypto version 2). Preferred on systems without AES-NI hardware acceleration.
- **RSA-4096, Ed25519, X25519** -- Asymmetric primitives for key wrapping, digital signatures, and key exchange.
- **SHA-256, SHA-512, SHA-3, BLAKE2** -- Hashing for checksums, commitments, and fingerprinting.

### Key Derivation

- **Argon2id** -- Primary KDF for deriving the vault encryption key from the master password. Configured with time cost 3, memory cost 64 MB, parallelism 4, and 32-byte output.
- **scrypt, HKDF, PBKDF2** -- Available for specific derivation and key expansion tasks.

### Vault Crypto Versioning

The vault supports algorithm versioning to enable future migrations without data loss. The current default is version 1 (AES-256-GCM), with version 2 (ChaCha20-Poly1305) available.

### Additional Protections

- Master password verification uses a separate Argon2id hash stored alongside the salt, independent of the vault encryption key derivation.
- 24-word recovery key generated from 256 bits of entropy for emergency vault access.
- Clipboard contents are automatically cleared after a configurable timeout (default 30 seconds).
- Secure delete overwrites file data before removal.
- Auto-lock timer secures the vault after a period of inactivity (default 5 minutes).
- All security events are recorded in an immutable audit log.

---

## License

This software is proprietary. All rights reserved. Unauthorized copying, modification, distribution, or use of this software is strictly prohibited.
