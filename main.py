from typing import Annotated
from fastapi import FastAPI, Request, Response, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse

from hashlib import sha512
from auth_functions import *
import os, time, json
from secrets import token_hex

from projects_tokens import create_project_token, revoke_project_token, has_read_access, has_write_access

DATA_DIR = os.getenv("STATE_DATA_DIR", "./data")

app = FastAPI(title="TerraHarbor")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _project_dir(name: str) -> str:
    path = os.path.join(DATA_DIR, name)
    os.makedirs(path, exist_ok=True)
    return path

def _latest_state(name: str) -> str:
    return os.path.join(_project_dir(name), "latest.tfstate")

@app.post("/register", tags=["auth"])
async def register(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Response:
    """
    Register a new user.
    This endpoint creates a new user with the provided username, password, full name, and email.
    The password is hashed using SHA-512.
    """
    if not form_data.username or not form_data.password:
        raise HTTPException(status_code=400, detail="All fields are required")

    user = User(username=form_data.username.strip(), disabled=True, sha512_hash=sha512(form_data.password.encode()).hexdigest(), usedforsecurity=True)
    if user_exists(user):
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        register_user(user)
        return {"message": "User registered successfully", "user": user}

@app.post("/token", tags=["auth"])
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    """
    Authenticates a user and returns an access token.
    """
    user = get_user(form_data.username)
    if not user or user.sha512_hash != sha512(form_data.password.encode()).hexdigest():
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = token_hex(32)
    update_user_token(user.username, access_token)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", tags=["auth"])
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    """
    Authenticates a user and returns an access token.
    """
    return await token(form_data)


@app.get("/me", tags=["auth"])
async def me(token: Annotated[str, Depends(oauth2_scheme)]) -> User | None:
    """
    Retrieve the currently authenticated user.
    """
    return get_current_user(token)

# GET  /state/{project}
@app.get("/state/{name}", response_class=FileResponse)
async def get_state(name: str, token: Annotated[str, Depends(oauth2_scheme)]) -> FileResponse:

    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")

    path = _latest_state(name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="State not found")
    return FileResponse(path, media_type="application/octet-stream")

# POST /state/{project}
@app.post("/state/{name}", response_class=Response)
async def put_state(name: str, request: Request, token: Annotated[str, Depends(oauth2_scheme)]) -> Response:
    
    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Empty body")

    proj_dir = _project_dir(name)
    ts = int(time.time())
    version_path = os.path.join(proj_dir, f"{ts}.tfstate")

    # We register the new state version and update the latest state
    for path in (version_path, _latest_state(name)):
        with open(path, "wb") as f:
            f.write(body)

    return Response(status_code=status.HTTP_200_OK)


# LOCK  /state/{project}
@app.api_route("/state/{name}", methods=["LOCK"], response_class=Response)
async def lock_state(name: str, request: Request, token: Annotated[str, Depends(oauth2_scheme)]) -> Response:

    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    lock_path = os.path.join(_project_dir(name), ".lock")
    body = (await request.body()).decode() or "{}"

    if os.path.exists(lock_path):
        with open(lock_path, "r") as f:
            return Response(f.read(), status_code=status.HTTP_423_LOCKED,
                            media_type="application/json")

    with open(lock_path, "w") as f:
        f.write(body)
    return Response(status_code=status.HTTP_200_OK)

# UNLOCK /state/{project}
@app.api_route("/state/{name}", methods=["UNLOCK"], response_class=Response)
async def unlock_state(name: str, request: Request, token: Annotated[str, Depends(oauth2_scheme)]) -> Response:

    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")

    lock_path = os.path.join(_project_dir(name), ".lock")
    if not os.path.exists(lock_path):
        # idempotent : ok even if the lock does not exist
        return Response(status_code=status.HTTP_200_OK)

    req_info = json.loads((await request.body()).decode() or "{}")
    with open(lock_path, "r") as f:
        cur_info = json.loads(f.read() or "{}")

    # if the request ID is provided and does not match the current lock ID, return error 409 Conflict
    if req_info.get("ID") and req_info["ID"] != cur_info.get("ID"):
        return Response(json.dumps(cur_info), status_code=status.HTTP_409_CONFLICT,
                        media_type="application/json")

    os.remove(lock_path)
    return Response(status_code=status.HTTP_200_OK)

# DELETE /state/{project}
@app.delete("/state/{name}", response_class=Response)
async def delete_state(name: str, token: Annotated[str, Depends(oauth2_scheme)]) -> Response:

    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")

    proj_dir = _project_dir(name)
    latest_path = _latest_state(name)

    if not os.path.exists(latest_path):
        raise HTTPException(status_code=404, detail="State not found")

    # Remove the latest state and all versions
    for file in os.listdir(proj_dir):
        os.remove(os.path.join(proj_dir, file))

    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Project token endpoints
@app.post("/state/{project_name}/token")
async def create_proj_token(token: str, project_name: str, permissions: int) -> dict:
    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")

    username = get_current_user(token).username

    try:
        project_token = create_project_token(username, project_name, permissions)
    except Exception as e:
        logger.error(f"Failed to create project token: {e}")
        raise HTTPException(status_code=403, detail="Failed to create project token")

    return {"project_token": project_token}


@app.delete("/state/{project_name}/{project_token}", response_class=Response)
async def delete_proj_token(token: str, project_name: str, project_token: str) -> Response:
    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        revoke_project_token(project_name, project_token)
    except Exception as e:
        logger.error(f"Failed to revoke project token: {e}")
        raise HTTPException(status_code=403, detail="Failed to revoke project token")

    return Response(status_code=status.HTTP_200_OK)


@app.get("/state/{project_name}/{project_token}/canRead", response_class=Response)
async def has_read_rights(project_name: str, project_token: str) -> Response:
    if not has_read_access(project_name, project_token):
        return Response(status_code=status.HTTP_403_FORBIDDEN)
    else:
        return Response(status_code=status.HTTP_200_OK)


@app.get("/state/{project_name}/{project_token}/canWrite", response_class=Response)
async def has_read_rights(project_name: str, project_token: str) -> Response:
    if not has_write_access(project_name, project_token):
        return Response(status_code=status.HTTP_403_FORBIDDEN)
    else:
        return Response(status_code=status.HTTP_200_OK)
