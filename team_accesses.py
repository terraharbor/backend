import logging
from secrets import token_hex

from pydantic import BaseModel

from auth_functions import get_db_connection, get_user_id
from teams_tokens import get_teams_ids_of_project_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserPermissions(BaseModel):
    username: str
    team: str
    admin: bool
    can_add_proj: bool
    can_del_proj: bool
    can_add_token: bool
    can_del_token: bool


def can_access_with_team_id(username: str, team_id: str) -> bool:
    """
    Checks if given user has access to given team
    """

    user_id = get_user_id(username)

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT userId, teamId
                FROM team_tokens
                WHERE userId = %s
                AND teamId = %s""", (user_id, team_id))
                row = cur.fetchone()
                if row:
                    return True
                else:
                    return False
    except Exception as e:
        logger.error(e)
        raise RuntimeError("Error on fetching access right by username and team_id")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")

def can_access_with_project_id(username: str, project_id: str) -> bool:
    try:
        # Fetch team IDs associated to project_id
        team_ids = get_teams_ids_of_project_id(project_id)

        # Fetch team tokens for current user
        user_id = get_user_id(username)
        acc_team_ids = fetch_accessible_team_ids_for_user(user_id)

        return bool(set(team_ids) & set(acc_team_ids))
    except Exception as e:
        logger.error(e)
        return False



def fetch_team_token_for_username_and_team(username: str, team_id: str) -> UserPermissions:
    user_id = get_user_id(username)

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT tt.administrator, tt.can_add_proj, tt.can_del_proj, tt.can_add_token, tt.can_del_token, t.name
                FROM team_tokens tt
                JOIN teams t ON t.id = tt.teamId
                WHERE userId = %s
                AND teamId = %s""", (user_id, team_id))
                row = cur.fetchone()
                if row:
                    admin, can_add_proj, can_del_proj, can_add_token, can_del_token, name = row
                    return UserPermissions(
                        username=username,
                        team=name,
                        admin=bool(int(admin)),
                        can_add_proj=bool(int(can_add_proj)),
                        can_del_proj=bool(int(can_del_proj)),
                        can_add_token=bool(int(can_add_token)),
                        can_del_token=bool(int(can_del_token))
                    )
    except Exception as e:
        logger.error(e)
        raise RuntimeError("Error on fetching team id by name")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")


def fetch_team_tokens_for_username(username: str) -> list[UserPermissions]:
    """
    Fetches allowed teams for given user
    """

    user_id = get_user_id(username)

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT tt.teamId, tt.administrator, tt.can_add_proj, tt.can_del_proj, tt.can_add_token, tt.can_del_token, t.name
                FROM team_tokens tt
                JOIN teams t ON tt.teamId = t.id
                WHERE userId = %s""", (user_id,))

                rows = cur.fetchall()
                if rows:
                    out = []
                    for row in rows:
                        team_id, admin, can_add_proj, can_del_proj, can_add_token, can_del_token, name = row
                        out.append(UserPermissions(username=username, team=name,
                                                   admin=bool(int(admin)),
                                                   can_add_proj=bool(int(can_add_proj)),
                                                   can_del_proj=bool(int(can_del_proj)),
                                                   can_add_token=bool(int(can_add_token)),
                                                   can_del_token=bool(int(can_del_token))))
                    return out

    except Exception as e:
        logger.error(e)
        raise RuntimeError("Error on fetching accessible teams by username")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")


def fetch_accessible_team_ids_for_user(user_id: str) -> list[str]:
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT teamId
                FROM team_tokens
                WHERE userId = %s""", (user_id,))

                rows = cur.fetchall()
                if rows:
                    return [row[0] for row in rows]
                else:
                    return []
    except Exception as e:
        logger.error(f"Error while fetching accessible team ids for user: {e}")
        return []


def add_access_for_username(user_adder: str, user_to_add: str, team_id: str) -> str:
    """
    Adds given user to given team. user_adder must be an administrator. Returns the token of the added user
    """
    adder_perms = fetch_team_token_for_username_and_team(user_adder, team_id)
    if adder_perms.admin:
        new_token = add_access(get_user_id(user_to_add), team_id)
        return new_token
    else:
        logger.error("Insufficient permissions to add user")
        return None


def revoke_access_for_username(user_revoker: str, user_to_remove: str, team_id: str) -> None:
    """
    Removes given user from given team. Revoker must be an admin
    """
    revoker_perms = fetch_team_token_for_username_and_team(user_revoker, team_id)
    if revoker_perms.admin:
        remove_access(get_user_id(user_to_remove), team_id)
    else:
        logger.error("Insufficient permissions to remove user")
        return None


def update_permissions_for_username(user_updater: str, user_to_update: str, team_id: str,
                                    admin: str, can_add_proj: str, can_del_proj: str,
                                    can_add_token: str, can_del_token: str) -> None:
    """
    Updates given user's permissions. Updater must be an admin
    """
    updater_perms = fetch_team_token_for_username_and_team(user_updater, team_id)
    if updater_perms.admin:
        update_access(get_user_id(user_to_update), team_id, admin, can_add_proj, can_del_proj,
                      can_add_token, can_del_token)
    else:
        logger.error("Insufficient permissions to update user permissions")



def add_access(user_id: str, team_id: str) -> str:
    auto_admin = False

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                # Quick check: if the team has no one, the user added is automatically admin
                cur.execute("""
                SELECT token, userId
                FROM team_tokens
                WHERE teamId = %s""", (team_id,))
                rows = cur.fetchall()
                user_ids = [row[1] for row in rows]

                if len(rows) == 0:
                    auto_admin = True

                if user_id not in user_ids:
                    # Add user
                    token = token_hex(32)
                    cur.execute("""
                    INSERT INTO team_tokens VALUES (%s, %s, %s, B'%s', B'0', B'0', B'0', B'0')""",
                                (token, team_id, user_id, 1 if auto_admin else 0))
                    return token
    except Exception as e:
        logger.error(e)
        raise RuntimeError(f"Error on adding user of ID {user_id}")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")


def remove_access(user_id: str, team_id: str) -> None:
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                DELETE FROM team_tokens
                WHERE userId = %s
                AND teamId = %s""", (user_id, team_id))
    except Exception as e:
        logger.error(e)
        raise RuntimeError(f"Error on removing user of ID {user_id}")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")


def update_access(user_id: str, team_id: str, admin: str, can_add_proj: str, can_del_proj: str, can_add_token: str, can_del_token: str) -> None:
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                UPDATE team_tokens
                SET administrator = %s,
                    can_add_proj = %s,
                    can_del_proj = %s,
                    can_add_token = %s,
                    can_del_token = %s
                WHERE userId = %s
                AND teamId = %s""", (admin, can_add_proj, can_del_proj, can_add_token, can_del_token, user_id, team_id))
    except Exception as e:
        logger.error(e)
        raise RuntimeError("Error on updating user permissions")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")

# TODO: refactor cleanly the methods and all
def get_team_id_by_name(team_name: str) -> str:
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT id
                FROM teams
                WHERE name = %s""", (team_name,))

                return cur.fetchone()[0]
    except Exception as e:
        logger.error(e)
        raise RuntimeError("Error on fetching team id by name")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")


def get_team_name_by_id(team_id: str) -> str:
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT name
                FROM teams
                WHERE id = %s""", (team_id,))

                return cur.fetchone()[0]
    except Exception as e:
        logger.error(e)
        raise RuntimeError("Error on fetching team name by id")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")
