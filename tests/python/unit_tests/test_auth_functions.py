import pytest
import time
from unittest.mock import patch, MagicMock
from backend.auth_functions import (
    decode_token, get_user, get_authenticated_user,
    user_exists, register_user, update_user_token, disable_user
)
from backend.user import User

@pytest.fixture
def mock_db_conn(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    monkeypatch.setattr('backend.auth_functions.get_db_connection', lambda: mock_conn)
    return mock_cursor

def test_user_exists_true(monkeypatch):
    monkeypatch.setattr('backend.auth_functions.get_user', lambda username: User(username='user', sha512_hash='hash', salt='salt'))
    assert user_exists(User(username='user', sha512_hash='hash', salt='salt'))

def test_user_exists_false(monkeypatch):
    monkeypatch.setattr('backend.auth_functions.get_user', lambda username: None)
    assert not user_exists(User(username='nouser', sha512_hash='hash', salt='salt'))

def test_register_user_success(mock_db_conn):
    user = User(username='user', sha512_hash='hash', salt='salt')
    try:
        register_user(user)
    except Exception:
        pytest.fail('register_user raised Exception unexpectedly!')

# Ajoute d'autres tests pour update_user_token, disable_user, etc.
