# tests/test_token_creation.py
import pytest
from accounts.create_tokens import create_tokens_for_user

@pytest.mark.django_db
def test_create_tokens_returns_valid_tokens(student_user):
    tokens = create_tokens_for_user(student_user.user)
    assert "refresh" in tokens
    assert "access" in tokens
    assert isinstance(tokens["refresh"], str)
    assert isinstance(tokens["access"], str)
