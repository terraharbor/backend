import logging

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

            return {"OK": "Project created successfully"}


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
                return []


def update_project(project_id: int, name: str, desc: str) -> dict:
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE projects 
            SET name = %s, description = %s 
            WHERE id = %s""", (name, desc, project_id))

            return {"OK": "Project updated successfully"}


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
            "ID": pid,
            "name": name,
            "description": desc,
            "timestamp": timestamp,
            "teamsIds": teams_ids
        })
    return out