"""Tests for password generation and strength analysis."""

from app.core.constants import DEFAULT_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH
from app.services.password_service import PasswordService


class TestPasswordGeneration:
    def test_default_length(self) -> None:
        pw = PasswordService.generate_password()
        assert len(pw) == DEFAULT_PASSWORD_LENGTH

    def test_custom_length(self) -> None:
        pw = PasswordService.generate_password(length=32)
        assert len(pw) == 32

    def test_min_length_enforced(self) -> None:
        pw = PasswordService.generate_password(length=1)
        assert len(pw) >= MIN_PASSWORD_LENGTH

    def test_max_length_enforced(self) -> None:
        pw = PasswordService.generate_password(length=999)
        assert len(pw) <= MAX_PASSWORD_LENGTH

    def test_uppercase_included(self) -> None:
        pw = PasswordService.generate_password(length=100, use_uppercase=True, use_lowercase=False, use_digits=False, use_symbols=False)
        assert all(c.isupper() for c in pw)

    def test_lowercase_included(self) -> None:
        pw = PasswordService.generate_password(length=100, use_uppercase=False, use_lowercase=True, use_digits=False, use_symbols=False)
        assert all(c.islower() for c in pw)

    def test_digits_included(self) -> None:
        pw = PasswordService.generate_password(length=100, use_uppercase=False, use_lowercase=False, use_digits=True, use_symbols=False)
        assert all(c.isdigit() for c in pw)

    def test_fallback_when_no_options(self) -> None:
        pw = PasswordService.generate_password(
            length=20, use_uppercase=False, use_lowercase=False,
            use_digits=False, use_symbols=False
        )
        assert len(pw) == 20

    def test_unique_passwords(self) -> None:
        passwords = {PasswordService.generate_password() for _ in range(20)}
        assert len(passwords) == 20


class TestPasswordStrength:
    def test_empty_password(self) -> None:
        result = PasswordService.calculate_strength("")
        assert result["score"] == 0
        assert result["label"] == "Weak"

    def test_weak_password(self) -> None:
        result = PasswordService.calculate_strength("abc")
        assert result["label"] == "Weak"

    def test_strong_password(self) -> None:
        result = PasswordService.calculate_strength("MyV3ry$ecureP@ssw0rd!")
        assert result["label"] == "Strong"
        assert result["score"] >= 5

    def test_entropy_increases_with_length(self) -> None:
        short = PasswordService.calculate_strength("Ab1!")
        long = PasswordService.calculate_strength("A" * 20 + "b1!" )
        assert long["entropy"] > short["entropy"]

    def test_score_range(self) -> None:
        result = PasswordService.calculate_strength("TestPass123!")
        assert 0 <= result["score"] <= result["max_score"]
