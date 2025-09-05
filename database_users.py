import logging
from http import HTTPStatus

from fastapi import HTTPException, Response

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
                    out.append({"id": uid, "username": username, "isAdmin": is_admin})
                return out
            else:
                return []

def update_user(user_id: int, username: str, is_admin: bool) -> dict:
    if not isinstance(is_admin, bool):
        raise HTTPException(status_code=400, detail="IsAdmin flag not in valid values set")
    conn = get_db_connection()

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                UPDATE users
                SET username = %s, isAdmin = %s
                WHERE id = %s""", (username, is_admin, user_id))

                return {
                    "id": user_id,
                    "username": username,
                    "isAdmin": is_admin
                }
    except:
        raise HTTPException(status_code=404, detail="User not found")


def delete_user(user_id: int) -> dict:
    conn = get_db_connection()

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                DELETE FROM users WHERE id = %s""", (user_id,))

                if cur.rowcount == 0:
                    return Response(status_code=HTTPStatus.NOT_FOUND,
                                    content="user not found")

                return {"OK": "Deleted user successfully"}
    except Exception as e:
        logger.error(f"Error when deleting user from users table: {e}")
        return Response(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                        content="Error deleting user")
