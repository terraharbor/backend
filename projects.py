import logging
from http import HTTPStatus

from fastapi import HTTPException

from auth_functions import get_db_connection
from teams_tokens import get_teams_ids_of_project_id

logger = logging.getLogger(__name__)

def create_project(project_name: str, desc: str) -> dict:
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                        INSERT INTO projects (name, description) VALUES (%s, %s)
                        """, (project_name, desc))

            cur.execute("""
            SELECT id, updated_at
            FROM projects
            WHERE name = %s AND description = %s""", (project_name, desc))

            row = cur.fetchone()
            if row:
                pid, timestamp = row
                return {
                    "id": pid,
                    "name": project_name,
                    "description": desc,
                    "lastUpdated": timestamp,
                    "teamIds": get_teams_ids_of_project_id(pid)
                }
            else:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Project not found in DB after creation")


def delete_project(project_id: int) -> dict:
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            DELETE FROM projects 
            WHERE id = %s""", (project_id,))

            return {"OK": "Successfully deleted project"}


def get_project_for_project_id(project_id: str) -> list[dict]:
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT p.name, p.id, p.description, f.uploaded_at
                        FROM projects p
                                 LEFT JOIN files f ON f.project_id = p.id
                        WHERE p.id = %s""", (project_id,))

            rows = cur.fetchall()
            if rows:
                return generate_project_entities(rows)
            else:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Project not found")


def update_project(project_id: int, name: str, desc: str, team_ids: list) -> dict:
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                UPDATE projects 
                SET name = %s, description = %s 
                WHERE id = %s""", (name, desc, project_id))

                # Get the difference between DB teams and query teams
                cur.execute("""
                SELECT team_id
                FROM project_teams
                WHERE project_id = %s""", (project_id,))

                project_rows = cur.fetchall()

                if project_rows:
                    for row in project_rows:
                        tid = row[0]
                        if tid in team_ids:
                            team_ids.remove(remove_team_id_from_project(tid, str(project_id)))

                # Add unregistered teams
                for to_reg_id in team_ids:
                    add_team_to_project(to_reg_id, str(project_id))

                cur.execute("""
                            SELECT created_at
                            FROM projects
                            WHERE id = %s""", (project_id,))

                row = cur.fetchone()

                return {
                    "id": project_id,
                    "name": name,
                    "description": desc,
                    "lastUpdated": row[0] if row else None,
                    "teamIds": get_teams_ids_of_project_id(str(project_id))
                }
    except Exception as ex:
        logger.error(f"Exception while updating project: {ex}")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Project to update not found")


def remove_team_id_from_project(team_id: str, project_id: str) -> str:
    conn = get_db_connection()

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                            DELETE FROM project_teams
                            WHERE team_id = %s AND project_id = %s""", (team_id, project_id))

                return team_id
    except Exception as e:
        logger.error(f"Failed to remove team from project")
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Team removal from project failed")


def add_team_to_project(team_id: str, project_id: str) -> None:
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                            INSERT INTO project_teams VALUES (2, %s, %s)""",
                            (team_id, project_id))
    except Exception as e:
        logger.error(e)
        raise RuntimeError(f"Error on adding team of ID {team_id} to project")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")


def get_projects_for_user_id(user_id: str) -> list[dict]:
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT p.name, p.id, p.description, f.uploaded_at
                        FROM projects p
                                 JOIN project_tokens pt ON pt.projectId = p.id
                                 JOIN files f ON f.project_id = p.id
                        WHERE pt.userId = %s""", (user_id,))

            rows = cur.fetchall()
            if rows:
                return generate_project_entities(rows)
            else:
                return []


def get_all_projects() -> list[dict]:
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT p.name, p.id, p.description, f.uploaded_at
                        FROM projects p
                                 LEFT JOIN files f ON f.project_id = p.id
                        WHERE TRUE""")

            rows = cur.fetchall()
            if rows:
                return generate_project_entities(rows)
            else:
                return []


def generate_project_entities(rows) -> list[dict]:
    out = []
    for row in rows:
        name, pid, desc, timestamp = row
        teams_ids = get_teams_ids_of_project_id(pid)
        out.append({
            "id": pid,
            "name": name,
            "description": desc,
            "lastUpdated": timestamp,
            "teamIds": teams_ids
        })
    return out