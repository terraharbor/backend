from http import HTTPStatus
from tabnanny import check
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException, status, Depends
from fastapi.security import HTTPBasic, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse

from auth_functions import *
from database_users import get_all_users, update_user, delete_user
from fastapi_custom_dependancy import get_auth_user
import os, json
from secrets import token_hex
from fastapi.middleware.cors import CORSMiddleware
import logging
from lock_helpers import check_lock_id
from path_tools import _state_dir, _latest_state_path, _versioned_state_path

from team_accesses import fetch_team_tokens_for_username
from projects_tokens import create_project_token, revoke_project_token, has_read_access, has_write_access, \
    get_accessible_projects_for_user_id, get_all_project_tokens, delete_project_token

from projects import get_projects_for_user_id, get_all_projects, get_project_for_project_id, update_project, \
    delete_project, create_project
from teams import get_teams_for_user, get_teams_for_project_id, get_all_teams, get_team_for_team_id, \
    get_users_for_team_id, get_projects_for_team_id, update_team_by_team_id, delete_team, create_team

app = FastAPI(title="TerraHarbor")

# Add CORS middleware to fix communication between frontend and backend:
# browser was refusing backend response
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT", "LOCK", "UNLOCK"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
basic_auth = HTTPBasic()
logger = logging.getLogger(__name__)



@app.get("/health")
async def health() -> dict:
    """
    Health check endpoint.
    """
    return {"status": "ok"}

@app.post("/register")
async def register(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Response:
    """
    Register a new user.
    This endpoint creates a new user with the provided username, password, full name, and email.
    The password is hashed using SHA-512.
    """
    if not form_data.username or not form_data.password:
        raise HTTPException(status_code=400, detail="All fields are required")

    salt = os.urandom(32).hex()
    salted_password = salt + form_data.password
    user = User(username=form_data.username.strip(), disabled=False, sha512_hash=sha512(salted_password.encode()).hexdigest(), salt=salt)
    if user_exists(user):
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        register_user(user)
        return {"message": "User registered successfully", "user": user}

@app.post("/token")
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    """
    Authenticates a user and returns an access token.
    """
    user = get_user(form_data.username)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    salted_password = user.salt + form_data.password

    if user.sha512_hash != sha512(salted_password.encode()).hexdigest():
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Check if the user is online already
    access_token = is_logged_in(user)
    if not access_token:
        access_token = token_hex(32)
        update_user_token(user.username, access_token)

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    """
    Authenticates a user and returns an access token.
    """
    return await token(form_data)


@app.post("/logout", tags=["auth"])
async def logout(user: Annotated[User, Depends(get_auth_user)]) -> Response:
    """
    Disconnects current user
    """
    try:
        disable_user(user.username, is_logged_in(user))
    except Exception as e:
        logger.error(f"Error on logout: {e}")
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status_code=status.HTTP_200_OK)


@app.get("/me", tags=["auth"])
async def me(user: Annotated[User, Depends(get_auth_user)]) -> User:
    """
    Retrieve the currently authenticated user (Bearer ou Basic).
    """
    return user


# Users endpoints
@app.get("/users")
async def get_users(user: Annotated[User, Depends(get_auth_user)]) -> list[dict]:
    return get_all_users()


@app.get("/users/{user_id}/projects")
async def get_user_projects(user: Annotated[User, Depends(get_auth_user)], user_id: str) -> list[dict]:
    return get_projects_for_user_id(user_id)


@app.get("/users/{user_id}/teams")
async def get_user_teams(user: Annotated[User, Depends(get_auth_user)], user_id: str) -> list[dict]:
    return get_teams_for_user(int(user_id))


@app.patch("/users/{user_id}")
async def update_user_id(
        user: Annotated[User, Depends(get_auth_user)],
        user_id: str,
        request: Request) -> dict:
    body = (await request.body()).decode() or "{}"

    data_dict = json.loads(body)

    if data_dict.get('username') is None or data_dict.get('isAdmin') is None:
        raise HTTPException(status_code=400, detail="Incomplete form data")

    if user.isAdmin:
        return update_user(int(user_id), data_dict['username'], data_dict['isAdmin'])
    else:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Must be admin to update user")


@app.delete("/users/{user_id}")
async def delete_user_by_id(
        user: Annotated[User, Depends(get_auth_user)],
        user_id: str) -> dict:
    if user.isAdmin:
        return delete_user(int(user_id))
    else:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Must be admin to remove user")


# GET  /state/{project}/{state_name}
@app.get("/state/{project}/{state_name}", response_class=FileResponse, tags=["auth"])
async def get_state(
    project: str,
    state_name: str,
    user: Annotated[User, Depends(get_auth_user)],
    version: int = None
) -> FileResponse:
    if version is not None:
        path = _versioned_state_path(project, state_name, version)
    else:
        path = _latest_state_path(project, state_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="State not found")
    return FileResponse(path, media_type="application/octet-stream")

# POST /state/{project}/{state_name}
@app.post("/state/{project}/{state_name}", response_class=Response, tags=["auth"])
async def put_state(
    project: str,
    state_name: str,
    request: Request,
    user: Annotated[User, Depends(get_auth_user)],
    ID: str = None
) -> Response:
    logger.info(f"PUT state called for project={project} state_name={state_name} user={user.username} ID={ID}")
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Empty body")
    # Get the serial from the query parameter or the JSON body

    try:
        json_body = json.loads(body)
        serial = json_body.get("serial")
    except Exception:
            pass
    if serial is None:
        raise HTTPException(status_code=400, detail="Missing state serial")
    if ID:
        if not check_lock_id(project, state_name, ID):
            raise HTTPException(status_code=409, detail="State is locked with a different ID")
    version_path = _versioned_state_path(project, state_name, serial)
    latest_path = _latest_state_path(project, state_name)
    with open(version_path, "wb") as f:
        f.write(body)
    with open(latest_path, "wb") as f:
        f.write(body)
    return Response(status_code=status.HTTP_200_OK)


# LOCK  /state/{project}
@app.api_route("/state/{project}/{state_name}", methods=["LOCK"], response_class=Response, tags=["auth"])
async def lock_state(
    project: str,
    state_name: str,
    request: Request,
    user: Annotated[User, Depends(get_auth_user)]
) -> Response:
    lock_path = os.path.join(_state_dir(project, state_name), ".lock")
    body = (await request.body()).decode() or "{}"
    if os.path.exists(lock_path):
        with open(lock_path, "r") as f:
            return Response(f.read(), status_code=status.HTTP_423_LOCKED, media_type="application/json")
    with open(lock_path, "w") as f:
        f.write(body)
    return Response(status_code=status.HTTP_200_OK)

# UNLOCK /state/{project}
@app.api_route("/state/{project}/{state_name}", methods=["UNLOCK"], response_class=Response, tags=["auth"])
async def unlock_state(
    project: str,
    state_name: str,
    request: Request,
    user: Annotated[User, Depends(get_auth_user)]
) -> Response:
    lock_path = os.path.join(_state_dir(project, state_name), ".lock")
    if not os.path.exists(lock_path):
        # idempotent : ok even if not locked
        return Response(status_code=status.HTTP_200_OK)

    req_info = json.loads((await request.body()).decode() or "{}")

    with open(lock_path, "r") as f:
        cur_info = json.loads(f.read() or "{}")

    # if the request ID is provided and does not match the current lock ID, return error 409 Conflict
    if req_info.get("ID") and req_info["ID"] != cur_info.get("ID"):
        return Response(json.dumps(cur_info), status_code=status.HTTP_409_CONFLICT, media_type="application/json")

    os.remove(lock_path)
    return Response(status_code=status.HTTP_200_OK)

# DELETE /state/{project}
@app.delete("/state/{project}/{state_name}", response_class=Response, tags=["auth"])
async def delete_state(
    project: str,
    state_name: str,
    user: Annotated[User, Depends(get_auth_user)],
    version: int = None
) -> Response:
    state_dir = _state_dir(project, state_name)
    logger.info(f"State asked to delete: {state_dir}")
    if version is not None:
        path = _versioned_state_path(project, state_name, version)
        if os.path.exists(path):
            logger.info(f"Deleting state version: {path}")
            os.remove(path)
            # If the latest version is deleted, update latest.tfstate
            versions = [int(f.split('.tfstate')[0]) for f in os.listdir(state_dir) if f.endswith('.tfstate') and f != 'latest.tfstate']
            if versions:
                last_version = max(versions)
                last_path = _versioned_state_path(project, state_name, last_version)
                latest_path = _latest_state_path(project, state_name)
                with open(last_path, "rb") as src, open(latest_path, "wb") as dst:
                    dst.write(src.read())
            else:
                # If there are no more versions, delete latest.tfstate
                latest_path = _latest_state_path(project, state_name)
                if os.path.exists(latest_path):
                    os.remove(latest_path)
        else:
            raise HTTPException(status_code=404, detail="State version not found")
    else:
        # Remove all versions and latest
        for file in os.listdir(state_dir):
            logger.info(f"Deleting state file: {file}")
            os.remove(os.path.join(state_dir, file))
    return Response(status_code=status.HTTP_200_OK)



# Project token endpoints
@app.get("/token/project/{project_id}")
async def create_proj_token(user: Annotated[User, Depends(get_auth_user)], project_id: str, permissions: int) -> dict:
    try:
        project_token = create_project_token(user.username, project_id, permissions)
    except Exception as e:
        logger.error(f"Failed to create project token: {e}")
        raise HTTPException(status_code=403, detail="Failed to create project token")

    return {"project_token": project_token}


@app.delete("/token/project/{project_id}/{project_token}", response_class=Response)
async def delete_proj_token(user: Annotated[User, Depends(get_auth_user)], project_id: str, project_token: str) -> Response:
    try:
        revoke_project_token(user.username, project_id, project_token)
    except Exception as e:
        logger.error(f"Failed to revoke project token: {e}")
        raise HTTPException(status_code=403, detail="Failed to revoke project token")

    return Response(status_code=status.HTTP_200_OK)


@app.get("/state/{project_id}/{project_token}/canRead", response_class=Response)
async def has_read_rights(user: Annotated[User, Depends(get_auth_user)], project_id: str, project_token: str) -> Response:
    if not has_read_access(project_id, project_token):
        return Response(status_code=status.HTTP_403_FORBIDDEN)
    else:
        return Response(status_code=status.HTTP_200_OK)


@app.get("/state/{project_id}/{project_token}/canWrite", response_class=Response)
async def has_write_rights(user: Annotated[User, Depends(get_auth_user)], project_id: str, project_token: str) -> Response:
    if not has_write_access(project_id, project_token):
        return Response(status_code=status.HTTP_403_FORBIDDEN)
    else:
        return Response(status_code=status.HTTP_200_OK)


@app.get("/teams/list")
async def list_accesses(user: Annotated[User, Depends(get_auth_user)]) -> dict:
    perms = fetch_team_tokens_for_username(user.username)

    res = {}
    for perm in perms:
        perm_dict = {perm.team : {
            "Admin": perm.admin,
            "CanAddProject": perm.can_add_proj,
            "CanRemoveProject": perm.can_del_proj,
            "CanCreateProjectToken": perm.can_add_token,
            "CanRemoveProjectToken": perm.can_del_token
        }}
        res.update(perm_dict)

    return res


@app.get("/state/list")
async def list_project_accesses(user: Annotated[User, Depends(get_auth_user)]) -> list[dict]:
    user_id = get_user_id(user.username)

    perms = get_accessible_projects_for_user_id(user_id)

    res: list[dict[str, str]] = []

    for perm in perms:
        res.append({f"{perm.projectId} - {perm.projectName}": "READ" if perm.permission == 1 else "WRITE" if perm.permission == 2 else "READ-WRITE"})

    return res


@app.get("/tokens")
async def list_project_tokens(user: Annotated[User, Depends(get_auth_user)]) -> list[dict]:
    if user.isAdmin:
        return get_all_project_tokens()
    else:
        raise HTTPException(status_code=403, detail="Must be admin to fetch project tokens")

@app.delete("/tokens/{project_token_id}")
async def delete_token_by_id(project_token_id: str, user: Annotated[User, Depends(get_auth_user)]) -> dict:
    if user.isAdmin:
        return delete_project_token(project_token_id)
    else:
        raise HTTPException(status_code=403, detail="Must be admin to delete project tokens")


@app.post("/tokens")
async def create_token(user: Annotated[User, Depends(get_auth_user)], request: Request) -> Response:
    body = (await request.body()).decode() or "{}"

    data_dict = json.loads(body)

    if data_dict.get('project_id') is None:
        raise HTTPException(status_code=400, detail="Project ID missing")

    if user.isAdmin:
        return create_project_token(data_dict['project_id'])
    else:
        raise HTTPException(status_code=403, detail="Must be admin to create project tokens")


@app.get("/projects")
async def get_projects(user: Annotated[User, Depends(get_auth_user)]) -> list[dict]:
    # ID, name, desc, last_updated_timestamp, list[teamId]
    return get_all_projects()


@app.get("/projects/{project_id}")
async def get_projects_by_id(user: Annotated[User, Depends(get_auth_user)], project_id: str) -> list[dict]:
    return get_project_for_project_id(project_id)


@app.get("/projects/{project_id}/teams")
async def get_teams_for_project(user: Annotated[User, Depends(get_auth_user)], project_id: str) -> list[dict]:
    return get_teams_for_project_id(project_id)

@app.patch("/projects/{project_id}")
async def update_project_by_id(user: Annotated[User, Depends(get_auth_user)], project_id: str, request: Request) -> dict:
    body = (await request.body()).decode() or "{}"

    data_dict = json.loads(body)

    if data_dict.get('name') is None or data_dict.get('description') is None or data_dict.get('teamIds') is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incomplete form data")

    if user.isAdmin:
        return update_project(int(project_id), data_dict['name'], data_dict['description'], data_dict['teamIds'])
    else:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Must be admin to update project")

@app.delete("/projects/{project_id}")
async def delete_project_by_id(user: Annotated[User, Depends(get_auth_user)], project_id: str) -> dict:
    if user.isAdmin:
        return delete_project(int(project_id))
    else:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Must be admin to remove project")


@app.post("/projects")
async def create_new_project(user: Annotated[User, Depends(get_auth_user)], request: Request) -> dict:
    if user.isAdmin:
        body = (await request.body()).decode() or "{}"

        data_dict = json.loads(body)

        if data_dict.get('name') is None or data_dict.get('description') is None:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Incomplete form data")

        return create_project(data_dict["name"], data_dict["description"])
    else:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Must be admin to create project")

@app.get("/teams")
async def get_teams(user: Annotated[User, Depends(get_auth_user)]) -> list[dict]:
    return get_all_teams()

@app.get("/teams/{team_id}")
async def get_team_by_id(user: Annotated[User, Depends(get_auth_user)], team_id: str) -> dict:
    return get_team_for_team_id(int(team_id))

@app.get("/teams/{team_id}/users")
async def get_users_for_team(user: Annotated[User, Depends(get_auth_user)], team_id: str) -> list[dict]:
    return get_users_for_team_id(int(team_id))

@app.get("/teams/{team_id}/projects")
async def get_projects_for_team(user: Annotated[User, Depends(get_auth_user)], team_id: str) -> list[dict]:
    return get_projects_for_team_id(int(team_id))

@app.patch("/teams/{team_id}")
async def update_team_by_id(user: Annotated[User, Depends(get_auth_user)], team_id: str, request: Request) -> dict:
    body = (await request.body()).decode() or "{}"

    data_dict = json.loads(body)

    if data_dict.get('name') is None or data_dict.get('description') is None or data_dict.get('userIds') is None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Incomplete form data")

    if user.isAdmin:
        return update_team_by_team_id(int(team_id), data_dict['name'], data_dict['description'], data_dict['userIds'])
    else:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Must be admin to update team")


@app.delete("/teams/{team_id}")
async def delete_team_by_id(user: Annotated[User, Depends(get_auth_user)], team_id: str) -> dict:
    if user.isAdmin:
        return delete_team(int(team_id))
    else:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Must be admin to delete team")

@app.post("/teams")
async def create_new_team(user: Annotated[User, Depends(get_auth_user)], request: Request) -> dict:
    body = (await request.body()).decode() or "{}"

    data_dict = json.loads(body)

    if data_dict.get('name') is None or data_dict.get('description') is None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Incomplete form data")

    if user.isAdmin:
        return create_team(data_dict['name'], data_dict['description'])
    else:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Must be admin to create team")

