import logging
from secrets import token_hex

from http import HTTPStatus

from auth_functions import get_db_connection, get_user_id
from projects import generate_project_entities
from fastapi import Response, HTTPException
from team_accesses import fetch_team_token_for_username_and_team

logger = logging.getLogger(__name__)

def create_team(name: str, description: str) -> dict:
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            # Create org
            cur.execute("""
                        INSERT INTO teams (name, description) VALUES (%s, %s)
                        """, (name, description))

            return {"OK": "Created new team"}


def delete_team(team_id: int) -> dict:
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            DELETE FROM teams WHERE id = %s""", (team_id,))

            return {"OK": "Deletion successful"}


def get_team_for_team_id(team_id: int) -> dict:
    conn = get_db_connection()

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT o.name, o.description
                        FROM teams o
                        WHERE id = %s
                        """, (team_id,))

            row = cur.fetchone()
            if row:
                name, desc = row
                return {"id": team_id,
                        "name": name,
                        "description": desc,
                        "userIds": get_users_ids_for_team(team_id)}
            else:
                logger.error(f"Error when fetching team ID {team_id}")
                return Response(status_code=HTTPStatus.FORBIDDEN, content="Team not found by ID")


def get_teams_for_user(user_id: int) -> list[dict]:
    conn = get_db_connection()

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT o.id, o.name, o.description
            FROM teams o
            JOIN team_tokens ot ON o.id = ot.teamId
            WHERE ot.userId = %s
            """, (user_id,))

            rows = cur.fetchall()
            if rows:
                out = []
                for row in rows:
                    team_id, name, desc = row
                    out.append({"id": team_id,
                                "name": name,
                                "description": desc,
                                "userIds": get_users_ids_for_team(team_id)})

                return out
            else:
                logger.error(f"Error when fetching teams for user ID {user_id}")
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Team not found")


def get_teams_for_project_id(project_id: str) -> list[dict]:
    conn = get_db_connection()

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT o.id, o.name, o.description
                        FROM teams o
                                 JOIN project_teams pt ON o.id = pt.team_id
                        WHERE pt.project_id = %s
                        """, (project_id,))

            rows = cur.fetchall()
            if rows:
                out = []
                for row in rows:
                    team_id, name, desc = row
                    out.append({"id": team_id,
                                "name": name,
                                "description": desc,
                                "userIds": get_users_ids_for_team(team_id)})

                return out
            else:
                logger.error(f"Error when fetching teams for project ID {project_id}")
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Team not found")


def get_users_ids_for_team(team_id: int) -> list[int]:
    conn = get_db_connection()

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT tt.userId
            FROM team_tokens tt
            JOIN teams t ON t.id = tt.teamid
            WHERE t.id = %s""", (team_id,))

            rows = cur.fetchall()
            if rows:
                return [row[0] for row in rows]
            else:
                return []


def update_team_by_team_id(team_id: int, name: str, description: str) -> dict:
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE teams
            SET name = %s, description = %s
            WHERE id = %s""", (name, description, team_id))

            return {"OK": "Team updated successfully"}


def get_all_teams() -> list[dict]:
    conn = get_db_connection()

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT o.id, o.name, o.description
                        FROM teams o
                        WHERE TRUE
                        """)

            rows = cur.fetchall()
            if rows:
                out = []
                for row in rows:
                    team_id, name, desc = row
                    out.append({"id": team_id,
                                "name": name,
                                "description": desc,
                                "userIds": get_users_ids_for_team(team_id)})

                return out
            else:
                logger.error("Error when fetching all teams")
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Teams not found")


def get_users_for_team_id(team_id: int) -> list[dict]:
    conn = get_db_connection()

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT u.id, u.username, u.isAdmin
                        FROM users u
                                 LEFT JOIN team_tokens tt ON tt.userId = u.id
                        WHERE tt.teamId = %s""", (team_id,))

            rows = cur.fetchall()
            if rows:
                out = []
                for row in rows:
                    uid, name, is_admin = row
                    out.append(
                        {"id": uid,
                         "username": name,
                         "isAdmin": is_admin})
                return out
            else:
                logger.error(f"Error when fetching users for team ID {team_id}")
                return []


def get_projects_for_team_id(team_id: int) -> list[dict]:
    conn = get_db_connection()

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT p.name, p.id, p.description, f.uploaded_at
            FROM projects p
                        LEFT JOIN project_teams pt ON p.id = pt.project_id
                    WHERE pt.team_id = %s""", (team_id,))

            rows = cur.fetchall()
            if rows:
                return generate_project_entities(rows)
            else:
                return []