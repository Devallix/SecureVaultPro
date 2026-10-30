# SecureVault Pro - User Guide

**Version:** 1.0  
**Last Updated:** October 2025

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Getting Started](#getting-started)
5. [Main Interface](#main-interface)
6. [Password Vault](#password-vault)
7. [Password Generator](#password-generator)
8. [Secure Notes](#secure-notes)
9. [File Encryption](#file-encryption)
10. [Digital Identities](#digital-identities)
11. [Security Centre](#security-centre)
12. [Backup & Restore](#backup--restore)
13. [Audit Log](#audit-log)
14. [Global Search](#global-search)
15. [Import & Export](#import--export)
16. [Settings](#settings)
17. [Security Best Practices](#security-best-practices)
18. [Troubleshooting](#troubleshooting)
19. [Keyboard Shortcuts](#keyboard-shortcuts)
20. [Support](#support)

---

## Introduction

SecureVault Pro is an enterprise-grade file encryption and password management desktop application. It provides a unified, encrypted vault for all your sensitive information - passwords, secure notes, files, digital identities, and more - all protected by a single master password and strong cryptographic primitives.

### Key Features

- **Unified Vault**: Store passwords, notes, files, SSH keys, API keys, and software licenses in one secure location
- **End-to-End Encryption**: All sensitive data encrypted at the application layer with AES-256-GCM
- **Strong Authentication**: Argon2id key derivation and 24-word recovery key for emergency access
- **Comprehensive Security Tools**: Password analysis, health scoring, and audit logging
- **Automatic Security**: Auto-lock, clipboard clearing, and secure file deletion
- **Cross-Platform Ready**: Built with PySide6 for native desktop experience

---

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Processor**: 1 GHz or faster x86_64 processor
- **Memory**: 4 GB RAM
- **Storage**: 200 MB available disk space
- **Display**: 1024 x 768 resolution
- **Python**: 3.13 or later (if running from source)

### Recommended Requirements
- **Memory**: 8 GB RAM or more
- **Storage**: 1 GB+ available space for vault and backups
- **Display**: 1920 x 1080 or higher with high-DPI support

---

## Installation

### From Source

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "Secure Vault Application"
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

---

## Getting Started

### First Launch - Creating Your Vault

When you launch SecureVault Pro for the first time, the **Create Vault Wizard** will appear:

1. **Vault Name**: Enter a name for your vault (e.g., "Personal Vault"). Defaults to "My Vault" if left blank.
2. **Master Password**: Create a strong master password. Requirements:
   - Minimum 8 characters
   - Should include uppercase, lowercase, numbers, and symbols for maximum security
3. **Confirm Password**: Re-enter your master password to confirm
4. **Create**: Click "Create Vault" to proceed

> **IMPORTANT**: Your master password cannot be recovered if lost. There is no "forgot password" option. Store it securely.

### Recovery Key

After creating your vault, you'll be presented with your **24-word recovery key**:

1. **Write it down**: Carefully write all 24 words in order on physical paper
2. **Store securely**: Keep it in a safe place, separate from your computer
3. **Never share**: Do not store it digitally (no screenshots, no cloud storage, no text files)
4. **Confirm**: Click through to acknowledge you've saved it

This recovery key is your only way to regain access if you forget your master password.

### Unlocking Your Vault

On subsequent launches:

1. The **Unlock Dialog** will appear
2. Enter your master password
3. Click "Unlock" to access your vault
4. If authentication fails, check your caps lock and keyboard layout

---

## Main Interface

The main window consists of:

### Sidebar Navigation
- **Dashboard** - Overview and security health
- **Passwords** - Password vault management
- **Generator** - Password/passphrase generator
- **Secure Notes** - Encrypted notes
- **Files** - File encryption/decryption
- **Digital Identities** - SSH keys, API keys, licenses
- **Security Centre** - Security analysis and recommendations
- **Backup & Restore** - Backup management
- **Audit Log** - Security event history
- **Settings** - Application configuration

### Status Bar
- **Vault Name**: Shows current vault name
- **Lock Timer**: Displays time until auto-lock (if configured)
- **Lock Button**: Manually lock the vault

### Header
- **Global Search**: Search across all vault items (Ctrl+F or use search bar)
- **Notifications**: Security alerts and system notifications
- **Theme Toggle**: Switch between dark and light themes

---

## Password Vault

### Adding a Password
1. Navigate to **Passwords** in the sidebar
2. Click **+ Add Password**
3. Fill in the fields:
   - **Title**: Name for this entry (e.g., "Gmail Account")
   - **Username/Email**: Login identifier
   - **Password**: The password (use generator or enter manually)
   - **URL**: Website URL (optional)
   - **Category**: Organize entries
   - **Tags**: Add searchable tags
   - **Notes**: Additional information
   - **Favourite**: Mark for quick access
4. Click **Save**

### Managing Passwords
- **View Details**: Click any entry to view details in the right panel
- **Edit**: Select entry and click **Edit** or double-click
- **Delete**: Select entry and click **Delete** (requires confirmation)
- **Copy Username/Password**: Click the copy icons (auto-clears after timeout)
- **Reveal Password**: Click the eye icon to temporarily reveal
- **Toggle Favourite**: Click the star icon
- **Filter**: Use category dropdown, tags, or favourites filter

### Password History
For entries with password changes tracked:
1. Select a password entry
2. Click **History** in the details panel
3. View previous passwords with timestamps
4. Optionally restore a previous password (use with caution)

### Password Expiration
Entries can have expiration dates. The dashboard and password list will show warnings for:
- Passwords expiring soon (within 7 days)
- Expired passwords
- Very old passwords (configurable threshold)

---

## Password Generator

### Random Character Mode
1. Navigate to **Generator**
2. Select **Random Characters** tab
3. Configure options:
   - **Length**: 8-128 characters (default varies)
   - **Uppercase (A-Z)**: Include/exclude
   - **Lowercase (a-z)**: Include/exclude
   - **Numbers (0-9)**: Include/exclude
   - **Symbols (!@#$...)**: Include/exclude
   - **Exclude ambiguous**: Avoid similar characters (O, 0, l, I)
4. Click **Generate**
5. View entropy and strength meter
6. Click **Copy to Clipboard**

### Passphrase Mode
1. Select **Passphrase** tab
2. Configure:
   - **Number of words**: 4-10 words (default 6)
   - **Separator**: Space, dash, underscore, or custom
   - **Capitalize words**: Optional
   - **Include number**: Optional
   - **Include symbol**: Optional
3. Click **Generate**
4. Passphrases are easier to remember and highly secure

> **Tip**: Aim for at least 80 bits of entropy for strong passwords. Use passphrases for master passwords or when character limits are high.

---

## Secure Notes

### Creating a Note
1. Navigate to **Secure Notes**
2. Click **+ Add Note**
3. Enter **Title**
4. Write content in the markdown editor
5. Click **Save**

### Editing Notes
- **Edit Mode**: Click **Edit** to modify
- **Preview Mode**: Toggle between edit and preview to see rendered markdown
- **Markdown Support**: Headings, bold, italic, lists, code blocks, links, and more

### Features
- **End-to-End Encryption**: Notes are encrypted at rest like all vault data
- **Search**: Notes are included in global search
- **Delete**: Remove notes with confirmation

---

## File Encryption

### Encrypting Files
1. Navigate to **Files**
2. Click **Encrypt Files**
3. Select files or folders:
   - **Add Files**: Select individual files
   - **Add Folder**: Encrypt entire directory recursively
4. Choose output location (defaults to original location with .enc extension)
5. Click **Encrypt**
6. Progress shown for large files (streaming encryption used)

### Decrypting Files
1. Navigate to **Files**
2. Click **Decrypt Files**
3. Select .enc files
4. Choose output location
5. Click **Decrypt**
6. Files are restored to original format

### Secure Delete
When deleting encrypted files:
1. Right-click or use **Secure Delete**
2. Files are overwritten with random data before deletion
3. Default is 3-pass overwrite (configurable)
4. This makes recovery extremely difficult

> **Warning**: Secure delete is permanent and cannot be undone. Use with caution.

---

## Digital Identities

Manage various types of digital credentials:

### SSH Keys
1. Navigate to **Digital Identities** > **SSH Keys**
2. Click **+ Add SSH Key**
3. Enter:
   - **Name**: Identifier for this key
   - **Key Type**: RSA, Ed25519, etc.
   - **Public Key**: Paste public key
   - **Private Key**: Paste private key (encrypted in vault)
   - **Passphrase**: If key is passphrase-protected
   - **Notes**: Additional information
4. Click **Save**

### API Keys
1. Go to **API Keys** tab
2. Click **+ Add API Key**
3. Fill in:
   - **Service**: Name of service (e.g., AWS, GitHub)
   - **Key Name**: Identifier
   - **API Key**: The actual key (encrypted)
   - **Secret**: Secret/token if applicable
   - **Expiry Date**: Optional expiration
   - **Notes**: Usage information
4. Click **Save**

### Software Licenses
1. Go to **Software Licenses** tab
2. Click **+ Add License**
3. Fill in:
   - **Product**: Software name
   - **License Key**: Product key (encrypted)
   - **Vendor**: Company name
   - **Purchase Date**: Date of purchase
   - **Expiry Date**: License expiration (if applicable)
   - **Seats**: Number of licenses
   - **Notes**: Additional details
4. Click **Save**

---

## Security Centre

The Security Centre analyzes your vault for vulnerabilities:

### Security Metrics
- **Overall Health Score**: 0-100 rating of vault security
- **Weak Passwords**: Passwords that are easily guessable or short
- **Duplicate Passwords**: Same password used across multiple sites
- **Reused Passwords**: Passwords used more than once
- **Old Passwords**: Passwords not changed in over 90 days (configurable)
- **Expired Passwords**: Passwords past their expiration date

### Taking Action
1. Navigate to **Security Centre**
2. Review the findings in each category
3. Click on an item to view details
4. Use **Change Password** or **Generate New Password** to remediate
5. The health score updates automatically as you fix issues

### Recommendations
The Security Centre provides actionable recommendations to improve your vault security.

---

## Backup & Restore

### Creating a Backup
1. Navigate to **Backup & Restore**
2. Click **Create Backup**
3. Choose backup location
4. Backup is encrypted with your vault encryption keys
5. A timestamped backup file will created

> **Note**: Backups are encrypted and require your master password and vault to restore.

### Scheduled Backups
1. Go to **Settings** > **Backup**
2. Enable **Automatic Backups**
3. Set schedule:
   - **Daily**: Every day at specified time
   - **Weekly**: Weekly on specified day
   - **Monthly** tags are included in global search
4. Set **Retention**: Number of backups to keep (up to 10)

### Restoring from Backup
1. Navigate to **Backup & Restore** > **Restore**
2. Click **Browse** and select your backup file
3. Enter master password for verification
4. Review restoration details
5. Click **Restore**
6. The vault will be restored to the state at backup time

> **Warning**: Restoring a backup will overwrite your current vault data. Consider creating a current backup before restoring.

---

## Audit Log

All security-relevant events are tracked:

### Event Types
- Vault creation, unlock, lock
- Password add/edit/delete/copy
- File encryption/decryption
- Backup creation/restoration
- Settings changes
- Failed authentication attempts
- Security analysis runs
- Import/export operations

### Viewing Audit Log
1. Navigate to **Audit Log**
2. Use filters:
   - **Date Range**: Filter by time period
   - **Event Type**: Filter by specific event
   - **Search**: Search event descriptions
3. Click on an event for more details

### Retention
- Default retention: 365 days
- Configurable in **Settings** > **Security** > **Audit Log Retention**
- Older entries are automatically purged

---

## Global Search

Search across your entire vault instantly:

1. Use the search bar in the header (or press **Ctrl+F**)
2. Type your search query
3. Results appear as you type, grouped by type:
   - Passwords
   - Secure Notes
   - Files (metadata)
   - Digital Identities (SSH keys, API keys, licenses)
4. Click any result to navigate to it

Search matches against titles, usernames, URLs, notes, and tags.

---

## Import & Export

### Importing Data
1. Navigate to **Settings** > **Import/Export** or use the import option
2. Click **Import**
3. Select format:
   - **CSV**: Comma-separated values
   - **JSON**: JSON format
4. Select file to import
5. Review import preview
6. Confirm import
7. Duplicates may be detected and handled according to settings

### Exporting Data
1. Navigate to **Settings** > **Import/Export**
2. Click **Export**
3. Select format:
   - **CSV**: For spreadsheet applications
   - **JSON**: For backup or migration
4. Choose what to export (all or selected categories)
5. Select destination
6. Exported data is decrypted for export - handle securely

> **Warning**: Exported files contain unencrypted sensitive data in the selected format. Store them securely and delete them when no longer needed.

---

## Settings

### Appearance
- **Theme**: Dark (default) or Light
- **Font Size**: Adjust UI font size
- **High DPI**: Automatic scaling

### Security
- **Auto-Lock Timeout**: Time of inactivity before locking (default: 300 seconds / 5 minutes)
- **Clipboard Clear Timeout**: Auto-clear copied passwords (default: 30 seconds)
- **Audit Log Retention**: Days to keep audit logs (default: 365)
- **Secure Delete Passes**: Number of overwrite passes (default: 3)

### Backup
- **Automatic Backups**: Enable/disable scheduled backups
- **Backup Schedule**: Daily/Weekly/Monthly
- **Backup Time**: Time of day for scheduled backups
- **Backup Location**: Directory for backups
- **Retention Count**: Number of backups to keep

### Notifications
- **Enable Notifications**: Turn notifications on/off
- **Security Alerts**: Notify for weak passwords, breaches, etc.
- **Expiration Warnings**: Notify for expired/expiring passwords
    - **Backup Notifications**: Notify for backup events

### Advanced
- **Language**: UI language (if available)
- **Data Directory**: Location of vault database
- **Clear Recent Searches**: Remove search history

---

## Security Best Practices

### Master Password
- Use a unique, strong master password of at least 12-16 characters
- Include a mix of uppercase, lowercase, numbers, and symbols
- Use a passphrase for easier recall and better entropy
- Never reuse your master password
- Never write it down digitally
- Never share it with anyone

### Recovery Key
- Write the 24-word recovery key on paper
- Store in a fireproof safe or secure location
- Consider storing copies in different secure locations
- Never photograph or store electronically
- Test your understanding of how to use it

### General Usage
- **Lock when away**: Manually lock (or rely on auto-lock) when stepping away
- **Clipboard hygiene**: Copy passwords only when needed; they'll auto-clear
- **Regular updates**: Keep SecureVault Pro updated
- **Backup regularly**: Create backups and store them securely offsite
- **Review Security Centre**: Check weekly for vulnerabilities
- **Audit regularly**: Review audit logs for suspicious activity
- **Secure your device**: Use disk encryption, screen lock, and antivirus
- **Unique passwords**: Use different passwords for every account
- **Two-factor auth**: Enable 2FA where available

### File Encryption
- Use secure delete for sensitive files when done
- Store encrypted files and keys separately if highly sensitive
- Be cautious when decrypting on shared computers

---

## Troubleshooting

### Cannot Unlock Vault
- **Check password**: Ensure caps lock is off and correct keyboard layout
- **Try recovery key**: If master password forgotten, use recovery key (if configured)
- **Check database**: Ensure vault database file isn't corrupted
- **Permissions**: Check file permissions on vault directory

### Application Won't Start
- **Dependencies**: Reinstall dependencies with `pip install -e ".[dev]"`
- **Python version**: Verify Python 3.13+ is installed
- **Display issues**: Try disabling high-DPI scaling
- **Logs**: Check logs in the application data directory

### Performance Issues
- **Large vaults**: Search and operations may slow with thousands of entries
- **File encryption**: Large files use streaming; ensure sufficient disk space
- **Memory**: Close other applications if low on RAM
- **Database**: Consider regular maintenance

### Backup/Restore Issues
- **Corrupted backup**: Try an older backup version
- **Wrong password**: Must use the master password that was active when backup was created
- **Disk space**: Ensure sufficient space for restore
- **Permissions**: Check read/write permissions

### Clipboard Not Clearing
- **Check settings**: Verify clipboard clear timeout is enabled
- **Permissions**: Some systems restrict clipboard access
- **Restart**: Restart the application

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | Add new item (context-dependent) |
| `Ctrl+F` | Open global search |
| `Ctrl+L` | Lock vault |
| `Ctrl+Q` | Quit application |
| `Ctrl+,` | Open settings |
| `F5` | Refresh current view |
| `Esc` | Close dialog/cancel |
| `Ctrl+C` | Copy selected item (where applicable) |
| `Delete` | Delete selected item (with confirmation) |

*Shortcuts may vary by view. Check context menus for additional options.*

---

## Support

### Documentation
- **README**: See `README.md` for technical overview
- **Implementation Plan**: See `docs/IMPLEMENTATION_PLAN.md` for development details
- **Source Code**: Review code comments for implementation details

### Reporting Issues
If you encounter bugs or have feature requests:
1. Check the troubleshooting section first
2. Review audit logs for relevant information
3. Document steps to reproduce
4. Include system information (OS, Python version, app version)

### Security Vulnerabilities
If you discover a security vulnerability:
- **Do not** disclose publicly
- Report privately through appropriate channels
- Include detailed description and reproduction steps
- Allow time for patching before disclosure

---

**Remember**: The security of your vault depends on your master password. Choose it wisely, store it securely, and protect your recovery key. Your data is only as secure as your weakest link.