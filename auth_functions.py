
from functools import wraps
from math import log

from user import User
import psycopg2
import os
import time
import logging
import time

logging.basicConfig(filename="global.log", level=logging.INFO, format="%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
}

def get_db_connection():
    logger.info("Connecting to the database...")
    connection = psycopg2.connect(**DB_CONFIG)
    logger.info("Database connection established.")
    return connection


def decode_token(token: str) -> User | None:
    """
    Decode the token and return the user information from DB.
    """
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT u.username, u.password_hash, u.salt, u.disabled, t.token, t.created_at, t.ttl
                    FROM users u
                    JOIN auth_tokens t ON u.id = t.user_id
                    WHERE t.token = %s
                """, (token,))
                row = cur.fetchone()
                if row:
                    username, password_hash, salt, disabled, token, created_at, ttl = row
                    # Calculate token expiration timestamp as an integer (Unix timestamp)
                    expiration_time = int(time.mktime((created_at + ttl).timetuple()))
                    logger.info(f"Decoded token: {token} for user: {username}, expires at {expiration_time}")
                    return User(
                        username=username,
                        sha512_hash=password_hash,
                        disabled=disabled,
                        token=token,
                        token_validity=expiration_time,
                        salt=salt
                    )
    except Exception as e:
        print(f"Error decoding token: {e}")
    finally:
        try:
            conn.close()
        except:
            logger.error(f"Error closing database connection after decoding token {token}")
    return None


def get_user(username: str) -> User | None:
    """
    Retrieve the user information from DB.
    """
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT username, password_hash, salt, disabled FROM users WHERE username = %s", (username,)) # Need the input of the query to be a tuple.
                row = cur.fetchone()
                if row:
                    username, password_hash, salt, disabled = row
                    logger.info(f"Retrieved user: {username}, disabled: {disabled}")
                    return User(username=username, sha512_hash=password_hash, disabled=disabled, salt=salt)
    except Exception as e:
        logger.error(f"Error retrieving user '{username}': {e}")
        return None
    finally:
        try:
            conn.close()
        except:
            logger.error(f"Error closing database connection after trying to retrieve user {username}")
    return None

def get_current_user(token) -> User | None:
    """
    Retrieve the currently authenticated user from the request context.
    """
    if not is_token_valid(token):
        logger.warning(f"Current user asked. Token not valid. Token: {token}")
        return None
    user: User = decode_token(token)
    return user

def user_exists(user: User) -> bool:
    """
    Verify if the user already exists in the DB.
    """
    logger.info(f"Checking if user exists: {user.username}")
    return bool(get_user(user.username))


def register_user(user: User) -> None:
    """
    Register a new user in the DB.
    """
    logger.info(f"Registering user: {user.username}")
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password_hash, salt) VALUES (%s, %s, %s)",
                    (user.username, user.sha512_hash, user.salt)
                )
    except Exception as e:
        logger.error(f"Error registering user {user.username}: {e}")
        raise RuntimeError(f"Failed to register user: {e}")
    finally:
        try:
            conn.close()
        except:
            logger.error(f"Error closing database connection after registering user {user.username}")


def update_user_token(username: str, token: str) -> None:
    """
    Update the user's token in the DB (insert new token for user).
    """
    logger.info(f"Updating token for user: {username}")
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
                logger.info(f"Token updated for user: {username}")
    except Exception as e:
        logger.error(f"Error updating token for user {username}: {e}")
        raise RuntimeError(f"Failed to update user token: {e}")
    finally:
        try:
            conn.close()
        except:
            logger.error(f"Error closing database connection after updating token for user {username}")



def is_token_valid(token: str) -> bool:
    """
    Check if the provided token is valid (exists and not expired).
    """
    logger.info(f"Checking if token is valid: {token}")
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
                    logger.info(f"Token {token} not found.")
                    return False
                created_at, ttl, disabled = row
                if disabled:
                    logger.info(f"Token {token} is associated with a disabled user.")
                    return False
                # Verifies that the token has not expired
                cur.execute("SELECT NOW() < (%s + %s)", (created_at, ttl))
                valid = cur.fetchone()[0]
                logger.info(f"Checked token {token}: valid={valid}")
                return valid
    except Exception as e:
        logger.error(f"Error validating token: {e}")
        return False
    finally:
        try:
            conn.close()
        except:
            pass