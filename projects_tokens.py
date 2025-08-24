import json
import os
from secrets import token_hex

from auth_functions import is_token_valid

# For now, store the project access management in a json
DATA_DIR = os.getenv('STATE_DATA_DIR', 'data')
# Structure of PROJECT_TOKEN_FILE: dict of pairs projectName-[projectTokens]. Simple index to easily know if a user has access
PROJECT_TOKEN_FILE = os.path.join(DATA_DIR, "project_access.json")
# TODO: Shall we perhaps create a file for User store manipulations? Maybe in User file, or will we keep this file solely
# TODO: for modelling the User class?
# TODO: Addendum after seeing new PR on data logic: will perform first PR with this code as-is, since the idea is still
# TODO: the same across SQL or JSON data storage
# TODO: For now, I'm defining access to the user store also here
USER_STORE_FILE = os.path.join(DATA_DIR, "users.json")


def create_project_token_for_user_and_project(username: str, token: str, project_name: str) -> None:
    """
    Creates new token for project for given user
    """
    # Check validity and user existence
    if is_token_valid(token):
        # Create token
        project_token = token_hex(32)

        # Update user project access info
        update_user_project_access(username, token, project_name, project_token)

        # Update project access management info
        update_project_access_management(project_name, project_token)


def update_user_project_access(username: str, token:str, project_name: str, project_token: str) -> None:
    """
    Updates the user data with new token for given project. Creates new dict, appends or creates new entry as needed
    """
    with open(USER_STORE_FILE, "r") as f:
        users_dict = json.load(f)

    for user in users_dict:
        if user.get('username') == username and user.get('token') == token:
            # If no dict defined yet
            if user['username'].get('projects_tokens') is None:
                user['username']['projects_tokens'] = {project_name: [project_token]}
            # If entry already exists
            elif project_name in user['username']['projects_tokens'].keys():
                user['username']['projects_tokens'][project_name].append(project_token)
            # If entry does not exist
            else:
                user['username']['projects_tokens'][project_name] = [project_token]

    with open(USER_STORE_FILE, "w") as f:
        json.dump(users_dict, f, indent=4)


def update_project_access_management(project_name: str, project_token: str) -> None:
    """
    Updates the project access management file with new token for given project.
    """
    with open(PROJECT_TOKEN_FILE, "r") as f:
        project_accesses_dict = json.load(f)

    project_entry = project_accesses_dict.get(project_name, [])
    project_entry.append(project_token)
    project_accesses_dict[project_name] = project_entry

    with open(PROJECT_TOKEN_FILE, "w") as f:
        json.dump(project_accesses_dict, f, indent=4)


def remove_project_token_from_user(username: str, project_name: str, project_token: str) -> None:
    """
    Removes the project-token pair from a user. Assumes existence checks done
    """
    with open(USER_STORE_FILE, "r") as f:
        users_dict = json.load(f)

    # Cleanup
    for user in users_dict:
        if user['username'] == username:
            user['username']['projects_tokens'][project_name].remove(project_token)

    with open(USER_STORE_FILE, "w") as f:
        json.dump(users_dict, f, indent=4)


def remove_token_from_projects_access(project_name: str, project_token: str) -> None:
    """
    Removes the token from the associated project. Assumes existence checks done
    """
    with open(PROJECT_TOKEN_FILE, "r") as f:
        projects_access_dict = json.load(f)

    # Cleanup
    projects_access_dict[project_name].remove(project_token)

    with open(PROJECT_TOKEN_FILE, "w") as f:
        json.dump(projects_access_dict, f, indent=4)


def verify_token_in_projects(project_name: str, project_token: str) -> bool:
    """
    Verifies that the project access management file contains the given token for the given project
    """
    with open(PROJECT_TOKEN_FILE, "r") as f:
        project_accesses_dict = json.load(f)

    project_entry = project_accesses_dict.get(project_name, [])

    return project_entry != [] and project_token in project_entry


def verify_project_token_in_users(username: str, project_name: str, project_token: str) -> bool:
    """
    Verifies that the user data contains the project token for the given project name for the given user
    """
    with open(USER_STORE_FILE, "r") as f:
        users_dict = json.load(f)

    for user in users_dict:
        if user['username'] == username and user['username'].get('projects_tokens') is not None and \
                project_name in user['username']['projects_tokens'].keys() and \
                project_token in user['username']['projects_tokens'][project_name]:
            return True

    return False


def is_authorized_to_access(username: str, project_name: str, project_token: str) -> bool:
    return verify_token_in_projects(project_name, project_token) and verify_project_token_in_users(username, project_name, project_token)


def revoke_project_access(username: str, project_name: str, project_token: str) -> None:
    # Check that user already has access to begin with
    if is_authorized_to_access(username, project_name, project_token):
        # Cleanup
        remove_token_from_projects_access(project_name, project_token)
        remove_project_token_from_user(username, project_name, project_token)