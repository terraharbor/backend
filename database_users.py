import logging

from fastapi import Response

from auth_functions import get_db_connection

logger = logging.getLogger(__name__)


def get_all_users() -> list[dict[str, str]]:
    conn = get_db_connection()

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT u.id, u.username, u.isAdmin
            FROM users u
            LEFT JOIN team_tokens tt ON tt.userId = u.id
            WHERE TRUE""")

            rows = cur.fetchall()

            if rows:
                out = []
                for row in rows:
                    uid, username, is_admin = row
                    out.append({"ID": uid, "username": username, "isAdmin": is_admin})
                return out
            else:
                return []

def update_user(user_id: int, username: str, is_admin: bool) -> dict:
    if not isinstance(is_admin, bool):
        return Response(status_code=400, details="IsAdmin flag not in valid values set")
    conn = get_db_connection()

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE users
            SET username = %s, isAdmin = %s
            WHERE id = %s""", (username, is_admin, user_id))

            return {"OK": "updated successfully the user"}


def delete_user(user_id: int) -> dict:
    conn = get_db_connection()

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                DELETE FROM users WHERE id = %s""", (user_id,))

                return {"OK": "Deleted user successfully"}
    except Exception as e:
        logger.error(f"Error when deleting user from users table: {e}")
        return {"ERROR": "Error deleting user"}
