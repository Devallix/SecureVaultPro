"""Tests for cryptographic primitives: symmetric, hashing, KDF, vault_crypto."""

import pytest

from app.core.constants import (
    CRYPTO_VERSION_1_AES_GCM,
    CRYPTO_VERSION_2_CHACHA20,
)
from app.core.exceptions import (
    DecryptionError,
    EncryptionError,
    UnsupportedAlgorithmError,
)
from app.security.hashing import hash_blake2b, hash_sha3_256, hash_sha256
from app.security.kdf import (
    derive_key_argon2id,
    derive_key_hkdf,
    derive_key_pbkdf2,
    derive_key_scrypt,
)
from app.security.secure_random import (
    constant_time_compare,
    generate_api_key,
    generate_nonce,
    generate_recovery_words,
    generate_salt,
)
from app.security.symmetric import (
    decrypt_aes_gcm,
    decrypt_chacha20,
    encrypt_aes_gcm,
    encrypt_chacha20,
)
from app.security.vault_crypto import decrypt_vault_data, encrypt_vault_data

# ── Symmetric Encryption ──


class TestAESGCM:
    def test_roundtrip_basic(self) -> None:
        key = generate_nonce(32)
        nonce = generate_nonce(12)
        plaintext = b"Hello, SecureVault!"
        ct = encrypt_aes_gcm(key, plaintext, nonce)
        pt = decrypt_aes_gcm(key, ct, nonce)
        assert pt == plaintext

    def test_roundtrip_empty(self) -> None:
        key = generate_nonce(32)
        nonce = generate_nonce(12)
        ct = encrypt_aes_gcm(key, b"", nonce)
        assert decrypt_aes_gcm(key, ct, nonce) == b""

    def test_roundtrip_large_data(self) -> None:
        key = generate_nonce(32)
        nonce = generate_nonce(12)
        plaintext = b"x" * 100_000
        ct = encrypt_aes_gcm(key, plaintext, nonce)
        assert decrypt_aes_gcm(key, ct, nonce) == plaintext

    def test_aad_roundtrip(self) -> None:
        key = generate_nonce(32)
        nonce = generate_nonce(12)
        aad = b"metadata"
        ct = encrypt_aes_gcm(key, b"secret", nonce, aad)
        assert decrypt_aes_gcm(key, ct, nonce, aad) == b"secret"

    def test_wrong_key_fails(self) -> None:
        key1 = generate_nonce(32)
        key2 = generate_nonce(32)
        nonce = generate_nonce(12)
        ct = encrypt_aes_gcm(key1, b"secret", nonce)
        with pytest.raises(DecryptionError):
            decrypt_aes_gcm(key2, ct, nonce)

    def test_tampered_ciphertext_fails(self) -> None:
        key = generate_nonce(32)
        nonce = generate_nonce(12)
        ct = bytearray(encrypt_aes_gcm(key, b"secret", nonce))
        ct[-1] ^= 0xFF
        with pytest.raises(DecryptionError):
            decrypt_aes_gcm(key, bytes(ct), nonce)

    def test_wrong_key_size_raises(self) -> None:
        with pytest.raises(EncryptionError):
            encrypt_aes_gcm(b"short", b"data", generate_nonce(12))

    def test_wrong_nonce_size_raises(self) -> None:
        with pytest.raises(EncryptionError):
            encrypt_aes_gcm(generate_nonce(32), b"data", b"short")


class TestChaCha20:
    def test_roundtrip_basic(self) -> None:
        key = generate_nonce(32)
        nonce = generate_nonce(12)
        plaintext = b"ChaCha20 test"
        ct = encrypt_chacha20(key, plaintext, nonce)
        assert decrypt_chacha20(key, ct, nonce) == plaintext

    def test_wrong_key_fails(self) -> None:
        key1 = generate_nonce(32)
        key2 = generate_nonce(32)
        nonce = generate_nonce(12)
        ct = encrypt_chacha20(key1, b"secret", nonce)
        with pytest.raises(DecryptionError):
            decrypt_chacha20(key2, ct, nonce)

    def test_wrong_key_size_raises(self) -> None:
        with pytest.raises(EncryptionError):
            encrypt_chacha20(b"short", b"data", generate_nonce(12))


# ── Hashing ──


class TestHashing:
    def test_sha256_deterministic(self) -> None:
        data = b"test data"
        assert hash_sha256(data) == hash_sha256(data)

    def test_sha256_length(self) -> None:
        assert len(hash_sha256(b"test")) == 32

    def test_sha3_256_length(self) -> None:
        assert len(hash_sha3_256(b"test")) == 32

    def test_blake2b_length(self) -> None:
        assert len(hash_blake2b(b"test", digest_size=32)) == 32

    def test_different_inputs_different_hashes(self) -> None:
        assert hash_sha256(b"a") != hash_sha256(b"b")


# ── KDF ──


class TestKDF:
    def test_argon2id_deterministic(self) -> None:
        password = b"master_password"
        salt = generate_salt(16)
        key1 = derive_key_argon2id(password, salt)
        key2 = derive_key_argon2id(password, salt)
        assert key1 == key2

    def test_argon2id_length(self) -> None:
        key = derive_key_argon2id(b"pw", generate_salt(16), hash_len=32)
        assert len(key) == 32

    def test_argon2id_different_salts(self) -> None:
        password = b"master_password"
        key1 = derive_key_argon2id(password, generate_salt(16))
        key2 = derive_key_argon2id(password, generate_salt(16))
        assert key1 != key2

    def test_scrypt_deterministic(self) -> None:
        key1 = derive_key_scrypt(b"pw", b"salt" * 4)
        key2 = derive_key_scrypt(b"pw", b"salt" * 4)
        assert key1 == key2

    def test_hkdf(self) -> None:
        key = derive_key_hkdf(b"material", b"salt", b"info")
        assert len(key) == 32

    def test_pbkdf2(self) -> None:
        key = derive_key_pbkdf2(b"password", b"salt")
        assert len(key) == 32


# ── Vault Crypto ──


class TestVaultCrypto:
    def test_aes_roundtrip(self) -> None:
        key = generate_nonce(32)
        plaintext = b"vault secret data"
        encoded = encrypt_vault_data(key, plaintext, CRYPTO_VERSION_1_AES_GCM)
        result = decrypt_vault_data(key, encoded)
        assert result == plaintext

    def test_chacha20_roundtrip(self) -> None:
        key = generate_nonce(32)
        plaintext = b"vault secret data"
        encoded = encrypt_vault_data(key, plaintext, CRYPTO_VERSION_2_CHACHA20)
        result = decrypt_vault_data(key, encoded)
        assert result == plaintext

    def test_unsupported_version_encrypt(self) -> None:
        with pytest.raises(UnsupportedAlgorithmError):
            encrypt_vault_data(generate_nonce(32), b"data", version=99)

    def test_corrupted_payload_fails(self) -> None:
        key = generate_nonce(32)
        encoded = encrypt_vault_data(key, b"secret")
        import base64
        raw = bytearray(base64.b64decode(encoded))
        raw[-1] ^= 0xFF
        corrupted = base64.b64encode(bytes(raw)).decode()
        with pytest.raises(DecryptionError):
            decrypt_vault_data(key, corrupted)

    def test_empty_plaintext(self) -> None:
        key = generate_nonce(32)
        encoded = encrypt_vault_data(key, b"")
        assert decrypt_vault_data(key, encoded) == b""

    def test_different_keys_fail(self) -> None:
        key1 = generate_nonce(32)
        key2 = generate_nonce(32)
        encoded = encrypt_vault_data(key1, b"secret")
        with pytest.raises(DecryptionError):
            decrypt_vault_data(key2, encoded)


# ── Secure Random ──


class TestSecureRandom:
    def test_generate_salt_length(self) -> None:
        assert len(generate_salt(16)) == 16
        assert len(generate_salt(32)) == 32

    def test_generate_nonce_length(self) -> None:
        assert len(generate_nonce()) == 12
        assert len(generate_nonce(16)) == 16

    def test_generate_api_key_unique(self) -> None:
        keys = {generate_api_key() for _ in range(50)}
        assert len(keys) == 50

    def test_generate_recovery_words_count(self) -> None:
        words = generate_recovery_words(24)
        assert len(words) == 24
        assert all(isinstance(w, str) for w in words)

    def test_constant_time_compare_equal(self) -> None:
        assert constant_time_compare(b"abc", b"abc") is True

    def test_constant_time_compare_not_equal(self) -> None:
        assert constant_time_compare(b"abc", b"abd") is False
