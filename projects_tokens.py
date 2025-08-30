import enum
import json
import logging

from secrets import token_hex
from typing import Union

from pydantic import BaseModel

from auth_functions import get_db_connection

logger = logging.getLogger(__name__)

class PERMISSION(enum):
    READ = 1,
    WRITE = 2,
    RW = 3


class ProjectToken(BaseModel):
    token: str
    permission: PERMISSION


def create_project_token(project_name: str, permission: Union[PERMISSION, int]) -> None:
    """
    Creates new token for project
    """
    # TODO(#13): verify user's auth and perms to create tokens (projectOwner/admin)
    # Create token
    project_token = token_hex(32)

    if permission is None:
        raise ValueError("Permission must be specified on creation of new project token")

    perm_val = permission.value if isinstance(permission, PERMISSION) else permission

    # Update project access info
    new_perm: dict[str, int] = {project_token: perm_val}

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                               UPDATE projects
                               SET tokens = ARRAY_APPEND(tokens, '%s')
                               WHERE name = %s""", (new_perm, project_name))
    except Exception as e:
        raise RuntimeError(f"Failed to update project access for project {project_name}: {e}")
    finally:
        try:
            conn.close()
        except:
            logger.error("Error closing DB connection")


def revoke_project_token(project_name: str, project_token: str) -> None:
    """
    Removes the project-token pair from a user.
    """
    # TODO(#13): Verify user's auth and perms to remove tokens (projectOwner/admin)
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                SELECT tokens FROM projects
                WHERE name = %s""", (project_name))
                row = cursor.fetchone()
                if row:
                    tokens = row
                    for token in tokens:
                        if project_token in token.keys():
                            tokens.remove(token)
                            break

                    cursor.execute("""
                    UPDATE projects
                    SET tokens = '%s'
                    WHERE name = %s""", (tokens, project_name))
    except Exception as e:
        raise RuntimeError(f"Failed to update project access for project {project_name}: {e}")
    finally:
        try:
            conn.close()
        except:
            logger.error("Error closing DB connection")


def get_token_in_projects(project_name: str, project_token: str) -> ProjectToken:
    """
    Returns the token data if it exists for a project.
    """
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cursor:
                conn.execute("""
                SELECT tokens FROM projects
                WHERE name = %s""", (project_name))
                row = cursor.fetchone()
                if row:
                    tokens = row
                    for token in tokens:
                        if project_token in token.keys():
                            token_data = json.load(token)
                            return ProjectToken(**token_data)
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve token for project {project_name}: {e}")
    finally:
        try:
            conn.close()
        except:
            logger.error("Error closing DB connection")



def has_read_access(project_name: str, project_token: str) -> bool:
    token = get_token_in_projects(project_name, project_token)
    return token.permission in [PERMISSION.READ, PERMISSION.RW]

def has_write_access(project_name: str, project_token: str) -> bool:
    token = get_token_in_projects(project_name, project_token)
    return token.permission in [PERMISSION.WRITE, PERMISSION.RW]
