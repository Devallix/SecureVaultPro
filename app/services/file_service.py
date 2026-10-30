"""File encryption service for SecureVault Pro."""

import contextlib
import hashlib
import os
import stat
import struct
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.constants import MAX_FILE_SIZE_MB
from app.core.exceptions import DecryptionError, FileTooLargeError
from app.logging.logger import get_logger
from app.security.crypto_engine import CryptoEngine
from app.security.secure_random import generate_nonce
from app.utils.secure_delete import secure_delete_file

logger = get_logger(__name__)

_STREAMING_THRESHOLD = 10 * 1024 * 1024  # 10 MB


def _derive_chunk_nonce(base_nonce: bytes, chunk_index: int) -> bytes:
    """Derive a unique per-chunk nonce from the base nonce and chunk index.

    Encodes the chunk index into the last 4 bytes of the 12-byte nonce
    so each chunk gets a unique (base_nonce, counter) pair.
    """
    prefix = base_nonce[:8]
    counter_bytes = struct.pack(">I", chunk_index)
    return prefix + counter_bytes


class FileService:
    """Service for encrypting and decrypting files."""

    def __init__(self, vault_key: bytes, file_repo) -> None:
        self._key = vault_key
        self._repo = file_repo
        self._crypto = CryptoEngine()

    # ── helpers ──

    def _create_metadata(
        self, vault_id: str, path: Path, encrypted_path: Path, nonce: bytes, ciphertext: bytes,
        checksum: str | None = None,
    ) -> dict:
        """Build a FileMetadata, persist it, and return the result dict."""
        file_size = path.stat().st_size
        if checksum is None:
            checksum = hashlib.sha256(ciphertext).hexdigest()

        from app.models.file_metadata import FileMetadata

        metadata = FileMetadata(
            vault_id=vault_id,
            original_name_enc=self._crypto.encrypt_field(self._key, path.name),
            encrypted_path=str(encrypted_path),
            nonce=nonce.hex(),
            hmac_tag="",
            file_size=file_size,
            mime_type_enc=self._crypto.encrypt_field(self._key, "application/octet-stream"),
            checksum=checksum,
        )
        self._repo.create(metadata)

        logger.info("File encrypted: {name} ({size} bytes)", name=path.name, size=file_size)
        return {
            "id": metadata.id,
            "original_name": path.name,
            "encrypted_path": str(encrypted_path),
            "size": file_size,
            "checksum": checksum,
        }

    @staticmethod
    def _restrict_permissions(file_path: Path) -> None:
        """Set restrictive file permissions on encrypted files (owner-only read/write)."""
        with contextlib.suppress(OSError):
            file_path.chmod(stat.S_IRUSR | stat.S_IWUSR)

    def _securely_delete_original(self, file_path: Path) -> None:
        """Securely overwrite and remove the original plaintext file."""
        try:
            secure_delete_file(str(file_path))
            logger.info("Securely deleted original: {path}", path=str(file_path))
        except Exception as e:
            logger.warning("Failed to securely delete original {path}: {err}", path=str(file_path), err=e)

    # ── single-file encrypt / decrypt ──

    def encrypt_file(
        self, vault_id: str, file_path: str, output_dir: str, delete_original: bool = False,
    ) -> dict:
        """Encrypt a single file, using streaming for files > 10 MB."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = path.stat().st_size
        max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise FileTooLargeError(f"File exceeds {MAX_FILE_SIZE_MB}MB limit")

        if file_size > _STREAMING_THRESHOLD:
            result = self.encrypt_file_streaming(vault_id, file_path, output_dir)
        else:
            nonce = generate_nonce(12)
            aesgcm = AESGCM(self._key)

            plaintext = path.read_bytes()
            ciphertext = aesgcm.encrypt(nonce, plaintext, None)

            random_name = hashlib.sha256(os.urandom(32)).hexdigest()
            encrypted_path = Path(output_dir) / random_name
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            encrypted_path.write_bytes(ciphertext)
            self._restrict_permissions(encrypted_path)

            result = self._create_metadata(vault_id, path, encrypted_path, nonce, ciphertext)

        if delete_original:
            self._securely_delete_original(path)

        return result

    def decrypt_file(self, file_metadata_id: str, output_path: str) -> str:
        """Decrypt a single file, using streaming for files > 10 MB."""
        metadata = self._repo.get_by_id(file_metadata_id)
        if metadata is None:
            raise DecryptionError(f"File metadata not found: {file_metadata_id}")

        enc_path = Path(metadata.encrypted_path)
        file_size = enc_path.stat().st_size
        if file_size > _STREAMING_THRESHOLD:
            return self.decrypt_file_streaming(file_metadata_id, output_path)

        nonce = bytes.fromhex(metadata.nonce)
        aesgcm = AESGCM(self._key)

        ciphertext = enc_path.read_bytes()
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)

        computed_checksum = hashlib.sha256(ciphertext).hexdigest()
        if computed_checksum != metadata.checksum:
            raise DecryptionError("File integrity check failed")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(plaintext)

        original_name = self._crypto.decrypt_field(self._key, metadata.original_name_enc)
        logger.info("File decrypted: {name}", name=original_name)
        return output_path

    # ── streaming encrypt / decrypt ──

    def encrypt_file_streaming(
        self, vault_id: str, file_path: str, output_dir: str, chunk_size: int = 65536,
    ) -> dict:
        """Encrypt a file by reading/writing in chunks (constant memory)."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        nonce = generate_nonce(12)
        aesgcm = AESGCM(self._key)

        random_name = hashlib.sha256(os.urandom(32)).hexdigest()
        encrypted_path = Path(output_dir) / random_name
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        hasher = hashlib.sha256()
        aad = None
        with open(path, "rb") as fin, open(encrypted_path, "wb") as fout:
            chunk_index = 0
            while True:
                chunk = fin.read(chunk_size)
                if not chunk:
                    break
                per_chunk_nonce = _derive_chunk_nonce(nonce, chunk_index)
                encrypted_chunk = aesgcm.encrypt(per_chunk_nonce, chunk, aad)
                fout.write(encrypted_chunk)
                hasher.update(encrypted_chunk)
                aad = encrypted_chunk
                chunk_index += 1

        self._restrict_permissions(encrypted_path)

        return self._create_metadata(
            vault_id, path, encrypted_path, nonce, b"", checksum=hasher.hexdigest(),
        )

    def decrypt_file_streaming(
        self, file_metadata_id: str, output_path: str, chunk_size: int = 65536,
    ) -> str:
        """Decrypt a file by reading/writing in chunks (constant memory)."""
        metadata = self._repo.get_by_id(file_metadata_id)
        if metadata is None:
            raise DecryptionError(f"File metadata not found: {file_metadata_id}")

        nonce = bytes.fromhex(metadata.nonce)
        aesgcm = AESGCM(self._key)

        encrypted_path = Path(metadata.encrypted_path)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        aad = None
        with open(encrypted_path, "rb") as fin, open(output_path, "wb") as fout:
            chunk_index = 0
            while True:
                chunk = fin.read(chunk_size)
                if not chunk:
                    break
                per_chunk_nonce = _derive_chunk_nonce(nonce, chunk_index)
                decrypted_chunk = aesgcm.decrypt(per_chunk_nonce, chunk, aad)
                fout.write(decrypted_chunk)
                aad = chunk
                chunk_index += 1

        original_name = self._crypto.decrypt_field(self._key, metadata.original_name_enc)
        logger.info("File decrypted (streaming): {name}", name=original_name)
        return output_path

    # ── batch / folder encryption ──

    def encrypt_folder(
        self, vault_id: str, folder_path: str, output_dir: str,
        delete_original: bool = False,
    ) -> list[dict]:
        """Encrypt all files in *folder_path* (non-recursive, skip .enc files)."""
        folder = Path(folder_path)
        if not folder.is_dir():
            raise NotADirectoryError(f"Not a directory: {folder_path}")

        results: list[dict] = []
        for entry in sorted(folder.iterdir()):
            if not entry.is_file():
                continue
            if entry.suffix == ".enc":
                continue
            try:
                result = self.encrypt_file(vault_id, str(entry), output_dir, delete_original)
                results.append(result)
            except Exception as exc:
                results.append({
                    "original_name": entry.name,
                    "error": str(exc),
                })
        logger.info(
            "Folder encrypted: {folder} ({count} files)",
            folder=folder_path,
            count=len(results),
        )
        return results

    def encrypt_files_batch(
        self, vault_id: str, file_paths: list[str], output_dir: str,
        delete_original: bool = False,
    ) -> list[dict]:
        """Encrypt multiple files at once."""
        results: list[dict] = []
        for fp in file_paths:
            try:
                result = self.encrypt_file(vault_id, fp, output_dir, delete_original)
                results.append(result)
            except Exception as exc:
                results.append({
                    "original_name": Path(fp).name,
                    "error": str(exc),
                })
        logger.info("Batch encrypted {count} files", count=len(results))
        return results

    def get_files(self, vault_id: str) -> list[dict]:
        """Get all file metadata for a vault, sorted alphabetically by name."""
        entries = self._repo.get_by_vault(vault_id)
        result = []
        for e in entries:
            result.append({
                "id": e.id,
                "original_name": self._crypto.decrypt_field(self._key, e.original_name_enc),
                "file_size": e.file_size,
                "checksum": e.checksum,
                "created_at": e.created_at,
            })
        result.sort(key=lambda x: x["original_name"].lower())
        return result

    def get_file_original_name(self, file_metadata_id: str) -> str:
        """Get the decrypted original filename for a file metadata entry."""
        metadata = self._repo.get_by_id(file_metadata_id)
        if metadata is None:
            return ""
        return self._crypto.decrypt_field(self._key, metadata.original_name_enc)

    def delete_file(self, file_metadata_id: str) -> bool:
        """Securely delete an encrypted file and its metadata."""
        metadata = self._repo.get_by_id(file_metadata_id)
        if metadata is None:
            return False

        encrypted_path = Path(metadata.encrypted_path)
        if encrypted_path.exists():
            secure_delete_file(str(encrypted_path))

        return self._repo.delete_by_id(file_metadata_id)

    def delete_all_files(self, vault_id: str) -> int:
        """Securely delete all encrypted files and metadata for a vault. Returns count deleted."""
        entries = self._repo.get_by_vault(vault_id)
        count = 0
        for entry in entries:
            encrypted_path = Path(entry.encrypted_path)
            if encrypted_path.exists():
                secure_delete_file(str(encrypted_path))
            self._repo.delete_by_id(entry.id)
            count += 1
        logger.info("Deleted all encrypted files for vault: {vault} ({count} files)", vault=vault_id, count=count)
        return count

    def decrypt_all_files(self, vault_id: str, output_dir: str) -> list[dict]:
        """Decrypt all files for a vault into output_dir. Returns list of results."""
        entries = self._repo.get_by_vault(vault_id)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        results: list[dict] = []
        for entry in entries:
            try:
                original_name = self._crypto.decrypt_field(self._key, entry.original_name_enc)
                out_path = str(Path(output_dir) / original_name)
                self.decrypt_file(entry.id, out_path)
                results.append({"id": entry.id, "original_name": original_name, "output_path": out_path})
            except Exception as exc:
                results.append({"id": entry.id, "error": str(exc)})
        logger.info("Batch decrypted {count} files for vault: {vault}", count=len(results), vault=vault_id)
        return results
