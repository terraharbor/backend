import logging
from secrets import token_hex

from pydantic import BaseModel

from auth_functions import get_db_connection, get_user_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserPermissions(BaseModel):
    username: str
    organisation: str
    admin: bool
    can_add_proj: bool
    can_del_proj: bool
    can_add_token: bool
    can_del_token: bool


def can_access(username: str, org_name: str) -> bool:
    """
    Checks if given user has access to given organisation
    """

    user_id = get_user_id(username)

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT userId, organisationId
                FROM organisation_tokens
                WHERE userId = %s
                AND organisationId = %s""", (user_id, org_name))
                row = cur.fetchone()
                if row:
                    return True
                else:
                    return False
    except Exception as e:
        logger.error(e)
        raise RuntimeError("Error on fetching access right by username and org_name")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")


def fetch_org_token_for_username_and_org(username: str, org_name: str) -> UserPermissions:
    user_id = get_user_id(username)
    org_id = get_org_id_by_name(org_name)

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT administrator, can_add_proj, can_del_proj, can_add_token, can_del_token
                FROM organisation_tokens
                WHERE userId = %s
                AND organisation = %s""", (user_id, org_name))
                row = cur.fetchone()
                if row:
                    admin, can_add_proj, can_del_proj, can_add_token, can_del_token = row
                    return UserPermissions(
                        username=username,
                        organisation=org_name,
                        admin=bool(int(admin)),
                        can_add_proj=bool(int(can_add_proj)),
                        can_del_proj=bool(int(can_del_proj)),
                        can_add_token=bool(int(can_add_token)),
                        can_del_token=bool(int(can_del_token))
                    )
    except Exception as e:
        logger.error(e)
        raise RuntimeError("Error on fetching organisation id by name")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")


def fetch_org_tokens_for_username(username: str) -> list[UserPermissions]:
    """
    Fetches allowed organisations for given user
    """

    user_id = get_user_id(username)

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT organisationId, administrator, can_add_proj, can_del_proj, can_add_token, can_del_token
                FROM organisation_tokens
                WHERE userId = %s""", (user_id,))

                rows = cur.fetchall()
                if rows:
                    out = []
                    for row in rows:
                        organisation_id, admin, can_add_proj, can_del_proj, can_add_token, can_del_token = row
                        out.append(UserPermissions(username=username, organisation=get_org_name_by_id(organisation_id),
                                                   admin=bool(int(admin)),
                                                   can_add_proj=bool(int(can_add_proj)),
                                                   can_del_proj=bool(int(can_del_proj)),
                                                   can_add_token=bool(int(can_add_token)),
                                                   can_del_token=bool(int(can_del_token))))
                    return out

    except Exception as e:
        logger.error(e)
        raise RuntimeError("Error on fetching accessible organisations by username")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")


def add_access_for_username(user_adder: str, user_to_add: str, org_name: str) -> str:
    """
    Adds given user to given organisation. user_adder must be an administrator. Returns the token of the added user
    """
    adder_perms = fetch_org_token_for_username_and_org(user_adder, org_name)
    if adder_perms.admin:
        new_token = add_access(get_user_id(user_to_add), get_org_id_by_name(org_name))
        return new_token
    else:
        logger.error("Insufficient permissions to add user")
        return None


def revoke_access_for_username(user_revoker: str, user_to_remove: str, org_name: str) -> None:
    """
    Removes given user from given organisation. Revoker must be an admin
    """
    revoker_perms = fetch_org_token_for_username_and_org(user_revoker, org_name)
    if revoker_perms.admin:
        remove_access(get_user_id(user_to_remove), get_org_id_by_name(org_name))
    else:
        logger.error("Insufficient permissions to remove user")
        return None


def update_permissions_for_username(user_updater: str, user_to_update: str, org_name: str,
                                    admin: str, can_add_proj: str, can_del_proj: str,
                                    can_add_token: str, can_del_token: str) -> None:
    """
    Updates given user's permissions. Updater must be an admin
    """
    updater_perms = fetch_org_token_for_username_and_org(user_updater, org_name)
    if updater_perms.admin:
        update_access(get_user_id(user_to_update), get_org_id_by_name(org_name), admin, can_add_proj, can_del_proj,
                      can_add_token, can_del_token)
    else:
        logger.error("Insufficient permissions to update user permissions")



def add_access(user_id: str, org_id: str) -> str:
    auto_admin = False

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                # Quick check: if the org has no one, the user added is automatically admin
                cur.execute("""
                SELECT token
                FROM organisation_tokens
                WHERE organisationId = %s""", (org_id,))
                rows = cur.fetchall()

                if len(rows) == 0:
                    auto_admin = True

                # Add user
                token = token_hex(32)
                cur.execute("""
                INSERT INTO organisation_tokens VALUES (%s, %s, %s, B'%s', B'0', B'0', B'0', B'0')""",
                            (token, user_id, org_id, 1 if auto_admin else 0))
                return token
    except Exception as e:
        logger.error(e)
        raise RuntimeError(f"Error on adding user of ID {user_id}")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")


def remove_access(user_id: str, org_id: str) -> None:
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                DELETE FROM organisation_tokens
                WHERE userId = %s
                AND organisationId = %s""", (user_id, org_id))
    except Exception as e:
        logger.error(e)
        raise RuntimeError(f"Error on removing user of ID {user_id}")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")


def update_access(user_id: str, org_id: str, admin: str, can_add_proj: str, can_del_proj: str, can_add_token: str, can_del_token: str) -> None:
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                UPDATE organisation_tokens
                SET administrator = %s,
                    can_add_proj = %s,
                    can_del_proj = %s,
                    can_add_token = %s,
                    can_del_token = %s
                WHERE userId = %s
                AND organisationId = %s""", (admin, can_add_proj, can_del_proj, can_add_token, can_del_token, user_id, org_id))
    except Exception as e:
        logger.error(e)
        raise RuntimeError("Error on updating user permissions")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")

# TODO: refactor cleanly the methods and all
def get_org_id_by_name(org_name: str) -> str:
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT id
                FROM organisations
                WHERE name = %s""", (org_name,))

                return cur.fetchone()[0]
    except Exception as e:
        logger.error(e)
        raise RuntimeError("Error on fetching organisation id by name")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")


def get_org_name_by_id(org_id: str) -> str:
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT name
                FROM organisations
                WHERE id = %s""", (org_id,))

                return cur.fetchone()[0]
    except Exception as e:
        logger.error(e)
        raise RuntimeError("Error on fetching organisation name by id")
    finally:
        try:
            conn.close()
        except Exception as e:
            logger.error("Failed to close database connection")
