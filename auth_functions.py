
from functools import wraps

from user import User
import psycopg2
import os
import time

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
                    SELECT u.username, u.password_hash, u.disabled, t.token, t.created_at, t.ttl
                    FROM users u
                    JOIN auth_tokens t ON u.id = t.user_id
                    WHERE t.token = %s
                """, (token,))
                row = cur.fetchone()
                if row:
                    username, password_hash, disabled, token, created_at, ttl = row
                    # Calculate token expiration timestamp as an integer (Unix timestamp)
                    expiration_time = int(time.mktime((created_at + ttl).timetuple()))
                    return User(
                        username=username,
                        sha512_hash=password_hash,
                        disabled=disabled,
                        token=token,
                        token_validity=expiration_time
                    )
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

def get_current_user(token) -> str | None:
    """
    Retrieve the currently authenticated user from the request context.
    """
    if not is_token_valid(token):
        return "Token not valid"
    user: User = decode_token(token)
    return user

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
    token_validity: int = 3600  # 1 hour
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
                    "INSERT INTO auth_tokens (user_id, token, created_at, ttl) VALUES (%s, %s, NOW(), %s::INTERVAL)",
                    (user_id, token, f'{token_validity} seconds')
                )
    except Exception as e:
        raise RuntimeError(f"Failed to update user token: {e}")
    finally:
        try:
            conn.close()
        except:
            pass



def disable_user(username: str, token: str) -> None:
    """
    Disable a given user in the system. Needs its last token for safety (preventing user delog solely through name)
    """
    try:
        with open(USERS_FILE, "r") as f:
            users_dict = json.load(f)

        # Doubly check
        if users_dict[username]["token"] != token:
            raise ValueError("Provided token does not match user token in store")

        users_dict[username]["disabled"] = True

        with open(USERS_FILE, "w") as s:
            json.dump(users_dict, s, indent=4)

    except Exception as e:
        raise RuntimeError(f"Failed to disable user: {e}")


def is_token_valid(token: str) -> bool:
    """
    Check if the provided token is valid (exists and not expired).
    """
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT t.created_at, t.ttl, u.disabled
                    FROM auth_tokens t
                    JOIN users u ON u.id = t.user_id
                    WHERE t.token = %s
                """, (token,))
                row = cur.fetchone()
                if not row:
                    return False
                created_at, ttl, disabled = row
                if disabled:
                    return False
                # Vérifie que le token n'est pas expiré
                cur.execute("SELECT NOW() < (%s + %s)", (created_at, ttl))
                valid = cur.fetchone()[0]
                return valid
    except Exception as e:
        print(f"Error validating token: {e}")
        return False
    finally:
        try:
            conn.close()
        except:
            pass