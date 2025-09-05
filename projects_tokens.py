import enum
import logging
from http import HTTPStatus
from http.client import HTTPException

from secrets import token_hex
from typing import Union

from pydantic import BaseModel

from fastapi import Response, HTTPException

from auth_functions import get_db_connection, get_user_id
from team_accesses import fetch_team_token_for_username_and_team
from teams_tokens import get_teams_ids_of_project_id

logger = logging.getLogger(__name__)


class PERMISSION(enum.Enum):
    READ = 1
    WRITE = 2
    RW = 3

def parse_permission_flags(read, write) -> int:
    if read == '1' and write == '1':
        return PERMISSION.RW
    elif read == '1' and not write == '1':
        return PERMISSION.READ
    elif write == '1' and not read == '1':
        return PERMISSION.WRITE
    else:
        raise ValueError('Invalid permission flags')


class ProjectToken(BaseModel):
    token: str
    projectId: int
    projectName: str
    permission: int


def create_project_token(project_id: str) -> dict:
    """
    Creates new token for project
    """

    # Create token
    project_token = token_hex(32)

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                               INSERT INTO project_tokens (token, projectId, userId, read, write) VALUES 
                                   (%s, %s, 1, B'1', B'1')""", (project_token, project_id))

                return {"token": project_token, "project_id": project_id}

    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Failed to create project access for project ID {project_id}: {e}")
    finally:
        try:
            conn.close()
        except:
            logger.error("Error closing DB connection")


def revoke_project_token(username: str, project_id: str, project_token: str) -> None:
    """
    Removes the project-token pair from a user.
    """

    # Check if user is an admin
    team_id = fetch_team_id_given_project_id(project_id)

    perms = fetch_team_token_for_username_and_team(username, team_id)

    if not perms or not perms.admin:
        raise ValueError("Not allowed to create token")

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                DELETE FROM project_tokens
                WHERE token = %s
                AND projectId = %s""", (project_token, project_id))
    except Exception as e:
        raise RuntimeError(f"Failed to update project access for project ID {project_id}: {e}")
    finally:
        try:
            conn.close()
        except:
            logger.error("Error closing DB connection")


def get_token_in_projects(project_token: str) -> ProjectToken:
    """
    Returns the token data if it exists for a project.
    """
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                SELECT projectId, read, write FROM project_tokens
                WHERE token = %s""", (project_token,))
                row = cursor.fetchone()
                if row:
                    pid, read, write = row
                    return ProjectToken(token=project_token,
                                        projectId=pid,
                                        projectName='',
                                        permission=parse_permission_flags(read, write))
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve token for token {project_token}: {e}")
    finally:
        try:
            conn.close()
        except:
            logger.error("Error closing DB connection")



def has_read_access(project_id: str, project_token: str) -> bool:
    token = get_token_in_projects(project_token)
    return token.permission in [PERMISSION.READ.value, PERMISSION.RW.value] and token.projectId == project_id

def has_write_access(project_id: str, project_token: str) -> bool:
    token = get_token_in_projects(project_token)
    return token.permission in [PERMISSION.WRITE.value, PERMISSION.RW.value] and token.projectId == project_id


def fetch_team_id_given_project_id(project_id: str) -> str | None:
    conn = get_db_connection()

    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT team_id
            FROM project_teams
            WHERE project_id = %s""", (project_id,))

            row = cur.fetchone()
            if row:
                return row[0]
            else:
                return None


def get_accessible_projects_for_user_id(user_id: str) -> list[ProjectToken]:
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT p.name, p.id, p.description, pt.read, pt.write
            FROM projects p
            JOIN project_tokens pt ON pt.projectId = p.id
            WHERE pt.userId = %s""", (user_id,))

            rows = cur.fetchall()
            if rows:
                out = []
                for row in rows:
                    name, pid, desc, read, write = row
                    out.append(ProjectToken(token='', projectId=pid, projectName=name, permission=parse_permission_flags(read, write)))

                return out
            else:
                return []


def get_project_tokens_for_team_id(team_id: str) -> list[ProjectToken]:
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT pt.token, p.name, p.id, pt.read, pt.write
            FROM projects p 
            JOIN project_tokens pt ON pt.projectId = p.id
            WHERE p.team_id = %s""", (team_id,))

            rows = cur.fetchall()
            if rows:
                out = []
                for row in rows:
                    token, name, pid, read, write = row
                    out.append(ProjectToken(token=token,
                                            projectId=pid,
                                            projectName=name,
                                            permission=parse_permission_flags(read, write)))
                return out
            else:
                return []


def get_all_project_tokens() -> list[dict]:
    out = []
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT token, projectId
            FROM project_tokens
            WHERE TRUE""")

            rows = cur.fetchall()
            if rows:
                for row in rows:
                    token, project_id = row

                    out.append({"token": token, "project_id": project_id})

                return out
            else:
                return []

def delete_project_token(token_id: str) -> dict:
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                            DELETE FROM project_tokens
                            WHERE token = %s""", (token_id,))

                return Response(status_code=200, content="Deleted project token succesfully")
    except Exception as e:
        logger.error(f"Failed to delete project token: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to delete project token")
