"""Tests for auth service."""

import pytest

from app.services.auth_service import AuthService


class TestAuthService:
    """Test cases for AuthService."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = AuthService.hash_password(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = AuthService.hash_password(password)

        assert AuthService.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        hashed = AuthService.hash_password(password)

        assert AuthService.verify_password("wrongpassword", hashed) is False

    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "user123"}
        token = AuthService.create_access_token(data)

        assert token is not None
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        data = {"sub": "user123"}
        token = AuthService.create_refresh_token(data)

        assert token is not None
        assert len(token) > 0

    def test_decode_token_valid(self):
        """Test decoding a valid token."""
        data = {"sub": "user123"}
        token = AuthService.create_access_token(data)
        decoded = AuthService.decode_token(token)

        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["type"] == "access"

    def test_decode_token_invalid(self):
        """Test decoding an invalid token."""
        decoded = AuthService.decode_token("invalid.token.here")

        assert decoded is None
