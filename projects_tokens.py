import enum
import logging

from secrets import token_hex
from typing import Union

from pydantic import BaseModel

from auth_functions import get_db_connection, get_user_id

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
    projectName: str
    permission: int


def create_project_token(username: str, project_name: str, permission: Union[PERMISSION, int]) -> str:
    """
    Creates new token for project
    """
    # TODO(#13): verify user's auth and perms to create tokens (projectOwner/admin)
    # Create token
    project_token = token_hex(32)

    if permission is None:
        raise ValueError("Permission must be specified on creation of new project token")

    perm_val = permission.value if isinstance(permission, PERMISSION) else permission

    user_id = get_user_id(username)
    project_id = get_project_id_from_name(project_name)

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                               INSERT INTO project_tokens (token, projectId, userId, read, write) VALUES 
                                   (%s, %s, %s, B'%s', B'%s')""", (project_token, project_id, user_id,
                                                         1 if perm_val in [1, 3] else 0,
                                                         1 if perm_val in [2, 3] else 0))
    except Exception as e:
        raise RuntimeError(f"Failed to update project access for project {project_name}: {e}")
    finally:
        try:
            conn.close()
        except:
            logger.error("Error closing DB connection")

    return project_token


def revoke_project_token(project_name: str, project_token: str) -> None:
    """
    Removes the project-token pair from a user.
    """
    # TODO(#13): Verify user's auth and perms to remove tokens (projectOwner/admin)
    project_id = get_project_id_from_name(project_name)
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                DELETE FROM project_tokens
                WHERE token = %s
                AND projectId = %s""", (project_token, project_id))
    except Exception as e:
        raise RuntimeError(f"Failed to update project access for project {project_name}: {e}")
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
                                        projectName=get_project_name_from_id(pid),
                                        permission=parse_permission_flags(read, write))
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve token for token {project_token}: {e}")
    finally:
        try:
            conn.close()
        except:
            logger.error("Error closing DB connection")



def has_read_access(project_name: str, project_token: str) -> bool:
    token = get_token_in_projects(project_token)
    return token.permission in [PERMISSION.READ.value, PERMISSION.RW.value] and token.projectName == project_name

def has_write_access(project_name: str, project_token: str) -> bool:
    token = get_token_in_projects(project_token)
    return token.permission in [PERMISSION.WRITE.value, PERMISSION.RW.value] and token.projectName == project_name



def get_project_name_from_id(id: int) -> str:
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT name
                FROM projects
                WHERE id = %s""", (id,))
                row = cur.fetchone()
                if row:
                    return row[0]
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve project name for id {id}: {e}")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Error closing DB connection")


def get_project_id_from_name(name: str) -> int:
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT id
                FROM projects
                WHERE name = %s""", (name,))
                row = cur.fetchone()
                if row:
                    return row[0]
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve project id for name {name}: {e}")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Error closing DB connection")