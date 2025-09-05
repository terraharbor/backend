from auth_functions import get_db_connection


def get_teams_ids_of_project_id(project_id :str) -> list[int]:
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
            SELECT team_id
            FROM project_teams
            WHERE project_id = %s""", (project_id,))

            rows = cur.fetchall()
            if rows:
                out = [row[0] for row in rows]
                return out
    return []
