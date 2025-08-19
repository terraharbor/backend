
from user import User
import psycopg2
import os
import time

# DB config from env vars or defaults
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def decode_token(token: str) -> User | None:
    """
    Decode the token and return the user information from DB.
    """
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT u.username, u.password_hash, u.disabled, t.token, t.created_at
                    FROM users u
                    JOIN auth_tokens t ON u.id = t.user_id
                    WHERE t.token = %s
                """, (token,))
                row = cur.fetchone()
                if row:
                    username, password_hash, disabled, token, created_at = row
                    # Token validity: 1h
                    token_validity = int(created_at.timestamp()) + 3600 if created_at else None
                    return User(username=username, sha512_hash=password_hash, disabled=disabled, token=token, token_validity=token_validity)
    except Exception as e:
        print(f"Error decoding token: {e}")
    finally:
        try:
            conn.close()
        except:
            pass
    return None


def get_user(username: str) -> User | None:
    """
    Retrieve the user information from DB.
    """
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT username, password_hash, disabled FROM users WHERE username = %s", (username,))
                row = cur.fetchone()
                if row:
                    username, password_hash, disabled = row
                    return User(username=username, sha512_hash=password_hash, disabled=disabled)
    except Exception as e:
        return None
    finally:
        try:
            conn.close()
        except:
            pass
    return None


def user_exists(user: User) -> bool:
    """
    Verify if the user already exists in the DB.
    """
    return bool(get_user(user.username))


def register_user(user: User) -> None:
    """
    Register a new user in the DB.
    """
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                    (user.username, user.sha512_hash)
                )
    except Exception as e:
        raise RuntimeError(f"Failed to register user: {e}")
    finally:
        try:
            conn.close()
        except:
            pass


def update_user_token(username: str, token: str) -> None:
    """
    Update the user's token in the DB (insert new token for user).
    """
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                # Get user id
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                row = cur.fetchone()
                if not row:
                    raise ValueError("User does not exist")
                user_id = row[0]
                # Insert token
                cur.execute(
                    "INSERT INTO auth_tokens (user_id, token, created_at) VALUES (%s, %s, NOW())",
                    (user_id, token)
                )
    except Exception as e:
        raise RuntimeError(f"Failed to update user token: {e}")
    finally:
        try:
            conn.close()
        except:
            pass


def is_token_valid(token: str) -> bool:
    """
    Check if the provided token is valid (exists and not expired).
    """
    user = decode_token(token)
    if user is None or user.disabled:
        return False
    current_time = int(time.time())
    return user.token_validity is not None and user.token_validity > current_time