# SecureVault Pro — Implementation Plan

## Overview

Enterprise File Encryption & Password Management Desktop Application built with Python 3.13+ and PySide6.

**Tagline:** Protect Everything. Trust Nothing.

## Environment

| Item | Value |
|------|-------|
| Python | 3.14.6 (win32, 64-bit) |
| GUI | PySide6 6.11.x |
| ORM | SQLAlchemy 2.0.x |
| Database | SQLite (app-layer encryption, SQLCipher upgrade path) |
| Crypto | cryptography 49.x, argon2-cffi 25.x, PyNaCl 1.6.x |
| Logging | loguru 0.7.x |
| Testing | pytest, pytest-qt, hypothesis |

## Architecture

```
Presentation (PySide6 Widgets/Dialogs)
    ↓
ViewModels (State management, signals)
    ↓
Application Services (Business logic)
    ↓
Security Services (Crypto, KDF, vault lock)
    ↓
Repositories (Data access, encrypt/decrypt fields)
    ↓
Database (SQLAlchemy + SQLite)
```

## Implementation Milestones

### Milestone 1: Project Scaffold + Dependencies ✅
- Git init, directory structure, pyproject.toml, requirements.txt
- Core modules: config, constants, exceptions, session, container, crash handler
- Logging with security filters
- Utils: validators, formatters, platform utils, secure delete
- Basic UI stubs: splash screen, unlock dialog, main window

### Milestone 2: Database Layer ✅
- SQLAlchemy engine + session factory
- All ORM models (vault, passwords, notes, files, etc.)
- Base repository with generic CRUD
- Specific repositories
- Alembic setup + initial migration

### Milestone 3: Security & Crypto Engine ✅
- CryptoEngine facade
- Symmetric: AES-256-GCM, ChaCha20-Poly1305
- Asymmetric: RSA-4096, Ed25519, X25519
- Hashing: SHA-2, SHA-3, BLAKE2
- KDF: Argon2id, scrypt, HKDF, PBKDF2
- Versioned vault crypto
- Clipboard manager, secure memory, integrity checks

### Milestone 4: Authentication System ✅
- Master password creation + verification
- Vault unlock/lock lifecycle
- Auto-lock timer
- Recovery key generation
- Password change wizard

### Milestone 5: Application Framework UI ✅
- Main window with sidebar, workspace
- Theme manager (dark/light) with switching
- Enhanced status bar with vault name and lock timer
- Notification center with severity levels
- High-DPI support

### Milestone 6: Vault Unlock UI + Dashboard ✅
- Create vault wizard
- Unlock screen
- Dashboard with stats, health score, and recent activity feed

### Milestone 7: Password Vault ✅
- Full CRUD with detail/edit panel
- Categories, tags, search
- Password history viewer
- Expiry warning display
- Favourites filter, category filter
- Copy username/password to clipboard
- Password reveal toggle

### Milestone 8: Password Generator ✅
- Random character mode
- Passphrase mode (BIP39-style words)
- Entropy calculation, strength meter
- Copy to clipboard

### Milestone 9: Secure Notes ✅
- Markdown rendering with edit/preview toggle
- Encryption
- Rich text support via markdown

### Milestone 10: File Encryption ✅
- Single/batch/folder encrypt/decrypt
- Streaming for large files (>10MB auto-chunked)
- Secure delete (3-pass overwrite)

### Milestone 11: Digital Identity ✅
- SSH keys, API keys, software licences

### Milestone 12: Security Centre ✅
- Weak/duplicate/reused password detection
- Background analysis via AnalysisWorker

### Milestone 13: Backup & Restore ✅
- Encrypted backup, versioning
- Scheduled auto-backup via QTimer
- Restore wizard with confirmation

### Milestone 14: Audit System ✅
- Track all security-relevant events

### Milestone 15: Reporting ✅
- CSV, PDF, Excel reports
- Password vault, audit log, and security reports

### Milestone 16: Settings System ✅
- Appearance: theme, font size, animations
- Security: auto-lock, clipboard clear, max login attempts, screensaver lock, crypto version
- Vault: password history count, expiry days
- Backup: auto-backup, interval, max versions
- Notifications: enabled, expiry warning days

### Milestone 17: Search & Import/Export ✅
- Global search with clickable, navigable results
- CSV import/export
- JSON export

### Milestone 18: Testing ✅
- 95 unit tests across 11 test files
- Crypto, database, session, password service, note service, file service, backup service, search service, audit service, import/export, security analysis

### Milestone 19: Documentation + Polish ✅
- README with setup instructions, architecture, features, tech stack
- Security documentation in README

## Deferred (Post-MVP)
- Plugin architecture
- Certificate management
- KeePass import
- CSV column mapping/field selection

## Crypto Algorithm Versioning
- Version 1: AES-256-GCM (default)
- Version 2: ChaCha20-Poly1305
- Version 3: XChaCha20-Poly1305 (future)

## Database Strategy
Primary: Application-layer encryption (encrypt fields before SQLite write).
Upgrade path: SQLCipher if binary wheels are available.
