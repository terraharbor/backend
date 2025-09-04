import logging
from secrets import token_hex

from auth_functions import get_db_connection, get_user_id
from team_accesses import fetch_team_token_for_username_and_team

logger = logging.getLogger(__name__)

def create_team(creator_name: str, team_name: str, desc: str) -> str:
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cur:
            # Create org
            cur.execute("""
                        INSERT INTO teams (name, description) VALUES (%s, %s)
                        """, (team_name, desc))

            # Create token, creator is admin
            new_tok = token_hex(32)

            cur.execute("""
            SELECT id FROM teams WHERE name = %s""", (team_name,))

            row = cur.fetchone()
            team_id = row[0]
            user_id = get_user_id(creator_name)

            # Create token
            cur.execute("""
            INSERT INTO team_tokens (token, teamId, userId, administrator, can_add_proj, can_del_proj, can_add_token, can_del_token)
                        VALUES (%s, %s, %s, B'%s', B'%s', B'%s', B'%s', B'%s')""", (new_tok, team_id, user_id, 1, 0, 0, 0, 0))

            return new_tok


def delete_team(deleter_name: str, team_id: str) -> None:
    # Check for permissions
    deleter_perms = fetch_team_token_for_username_and_team(deleter_name, team_id)

    if deleter_perms and deleter_perms.admin:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                            DELETE FROM teams WHERE id = %s""", (team_id,))
    else:
        logger.error("You are not allowed to delete team.")


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
                    out.append({"ID": team_id,
                                "name": name,
                                "description": desc,
                                "userIds": get_users_ids_for_team(team_id)})

                return out
            else:
                logger.error(f"Error when fetching teams for user ID {user_id}")
                return [{"Error": "notFound"}]


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
                    out.append({"ID": team_id,
                                "name": name,
                                "description": desc,
                                "userIds": get_users_ids_for_team(team_id)})

                return out
            else:
                logger.error(f"Error when fetching teams for project ID {project_id}")
                return [{"Error": "notFound"}]


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


def update_team_by_id(updater_name: str, team_id: str, contents: dict) -> None:
    updater_perms = fetch_team_token_for_username_and_team(updater_name, team_id)

    if updater_perms and updater_perms.admin:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                UPDATE teams
                SET name = %s, description = %s
                WHERE id = %s""", (contents['name'], contents['description'], team_id))
