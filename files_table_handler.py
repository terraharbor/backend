import logging
from http import HTTPStatus

from fastapi import HTTPException

from auth_functions import get_db_connection

logger = logging.getLogger(__name__)


def write_state_path_to_db(file_path: str, project_id: str) -> str:
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                # Check if state ID already exists within the table
                cur.execute("""
                SELECT id
                FROM files
                WHERE project_id = %s""", (project_id,))

                row = cur.fetchone()

                if row:
                    # Update the entry
                    cur.execute("""
                    UPDATE files
                    SET file_path = %s
                    WHERE project_id = %s""", (file_path, project_id))
                else:
                    # Insert the entry
                    cur.execute("""
                    INSERT INTO files (file_path, project_id)
                    VALUES (%s, %s)""", (file_path, project_id))

                # Return state ID
                cur.execute("""
                SELECT id
                FROM files
                WHERE project_id = %s""", (project_id,))

                return cur.fetchone()[0]

    except Exception as e:
        logger.error(f"Exception while writing state path: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


def get_state_from_db(file_path: str, project_id: str) -> str | None:
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT id
                FROM files
                WHERE project_id = %s AND file_path = %s""", (project_id, file_path))

                row = cur.fetchone()
                if row:
                    return file_path
                else:
                    logger.error(f"State not found for given path {file_path} and project {project_id}")
                    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"State not found for given path {file_path} and project {project_id}")
    except Exception as e:
        logger.error(f"Exception while getting state from db: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


def get_states_from_db_for_project_id(project_id: str) -> list[dict]:
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                            SELECT id, file_path
                            FROM files
                            WHERE project_id = %s""", (project_id,))

                rows = cur.fetchall()
                if rows:
                    out = []
                    for row in rows:
                        sid, path = row
                        out.append({"id": sid, "path": path})
                    return out
                else:
                    logger.error(f"States not found for given project {project_id}")
                    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"States not found for given project {project_id}")
    except Exception as e:
        logger.error(f"Exception while getting state from db: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


def delete_state_from_db(file_path: str, project_id: str) -> None:
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                            DELETE FROM files
                            WHERE project_id = %s AND file_path = %s""", (project_id, file_path))

                if cur.rowcount == 0:
                    logger.error(f"State could not be deleted from DB for given path {file_path} and project {project_id}")
                    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"State could not be deleted from DB for given path {file_path} and project {project_id}")
    except Exception as e:
        logger.error(f"Exception while deleting state from db: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))