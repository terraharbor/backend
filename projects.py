import logging

from auth_functions import get_db_connection, get_user_id
from team_accesses import fetch_team_token_for_username_and_team
from projects_tokens import get_accessible_projects_for_user_id, PERMISSION
from teams_tokens import get_teams_ids_of_project_id

logger = logging.getLogger(__name__)

def create_project(creator_name: str, project_name: str, desc: str, team_id: str) -> None:
    # Check for permissions
    creator_perms = fetch_team_token_for_username_and_team(creator_name, team_id)

    if creator_perms and (creator_perms.admin or creator_perms.can_add_proj):
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO projects (team_id, name, description) VALUES (%s, %s, %s)
                """, (team_id, project_name, desc))
    else:
        logger.error("You are not allowed to create projects.")


def delete_project(deleter_name: str, project_id: str, team_id: str) -> None:
    # Check for permissions
    deleter_perms = fetch_team_token_for_username_and_team(deleter_name, team_id)

    if deleter_perms and (deleter_perms.admin or deleter_perms.can_del_proj):
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                DELETE FROM projects WHERE id = %s AND team_id = %s
                """, (project_id, team_id))
    else:
        logger.error("You are not allowed to delete projects.")


def get_projects_for_project_id(username: str, project_id: str, team_id: str) -> list[dict]:
    # Check for permissions
    user_perms = fetch_team_token_for_username_and_team(username, team_id)
    # Check read access too
    user_id = get_user_id(username)
    projects_perms = get_accessible_projects_for_user_id(user_id)
    project_perm = None

    for project_perms in projects_perms:
        if project_perms.project_id == project_id:
            project_perm = project_perms
            break

    if user_perms and project_perm and project_perm.permission in [PERMISSION.READ.value, PERMISSION.RW.value]:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT file_path, file_size, uploaded_at
                FROM files
                WHERE project_id = %s""", (project_id,))

                rows = cur.fetchall()
                if rows:
                    # TODO(MAYBE DEPRECATED AS OF THURSDAY): fixme a little, make sure perms are checked for each project (integrate project_perms in here)
                    out = []
                    for row in rows:
                        file_path, file_size, uploaded_at = row
                        out.append({"Path": file_path, "Size": file_size, "Timestamp": uploaded_at})
                    return out

    return [{"Err": "Not found"}]


def update_project_by_id(username: str, project_id: str, team_id: str, contents: dict) -> None:
    # Check for permissions
    user_perms = fetch_team_token_for_username_and_team(username, team_id)
    user_id = get_user_id(username)
    projects_perms = get_accessible_projects_for_user_id(user_id)

    project_perm = None

    for project_perms in projects_perms:
        if project_perms.project_id == project_id:
            project_perm = project_perms
            break

    if user_perms and project_perm and project_perm.permission in [PERMISSION.WRITE.value, PERMISSION.RW.value]:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                UPDATE files
                SET file_path = %s, file_size = %s, uploaded_at = NOW()
                WHERE project_id = %s""", (contents['file_path'], contents['file_size'], project_id,))


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
            else:
                return []
