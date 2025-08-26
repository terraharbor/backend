from typing import Annotated
from fastapi import FastAPI, Request, Response, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from user import User
from hashlib import sha512
from auth_functions import *
import os, time, json
from secrets import token_hex


DATA_DIR = os.getenv("STATE_DATA_DIR", "./data")

app = FastAPI(title="TerraHarbor")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _state_dir(project: str, state_name: str) -> str:
    path = os.path.join(DATA_DIR, project, state_name)
    os.makedirs(path, exist_ok=True)
    return path

def _latest_state_path(project: str, state_name: str) -> str:
    return os.path.join(_state_dir(project, state_name), "latest.tfstate")

def _versioned_state_path(project: str, state_name: str, ts: int) -> str:
    return os.path.join(_state_dir(project, state_name), f"{ts}.tfstate")


@app.post("/register")
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

@app.post("/token")
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

@app.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    """
    Authenticates a user and returns an access token.
    """
    return token(form_data)


@app.get("/me", tags=["auth"])
async def me(token: Annotated[str, Depends(oauth2_scheme)]) -> User | None:
    """
    Retrieve the currently authenticated user.
    """
    return get_current_user(token)

# GET  /state/{project}/{state_name}
@app.get("/state/{project}/{state_name}", response_class=FileResponse, tags=["auth"])
async def get_state(project: str, state_name: str, token: Annotated[str, Depends(oauth2_scheme)], version: int = None) -> FileResponse:
    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    if version:
        path = _versioned_state_path(project, state_name, version)
    else:
        path = _latest_state_path(project, state_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="State not found")
    return FileResponse(path, media_type="application/octet-stream")

# POST /state/{project}/{state_name}
@app.post("/state/{project}/{state_name}", response_class=Response, tags=["auth"])
async def put_state(project: str, state_name: str, request: Request, token: Annotated[str, Depends(oauth2_scheme)]) -> Response:
    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Empty body")
    ts = int(time.time())
    version_path = _versioned_state_path(project, state_name, ts)
    latest_path = _latest_state_path(project, state_name)
    # Save new version
    with open(version_path, "wb") as f:
        f.write(body)

    with open(latest_path, "wb") as f:
        f.write(body)
    return Response(status_code=status.HTTP_200_OK)


# LOCK  /state/{project}
@app.api_route("/state/{project}/{state_name}", methods=["LOCK"], response_class=Response, tags=["auth"])
async def lock_state(project: str, state_name: str, request: Request, token: Annotated[str, Depends(oauth2_scheme)]) -> Response:
    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")
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
async def unlock_state(project: str, state_name: str, request: Request, token: Annotated[str, Depends(oauth2_scheme)]) -> Response:
    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")
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
async def delete_state(project: str, state_name: str, token: Annotated[str, Depends(oauth2_scheme)], version: int = None) -> Response:
    if not is_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    state_dir = _state_dir(project, state_name)
    if version:
        path = _versioned_state_path(project, state_name, version)
        if os.path.exists(path):
            os.remove(path)
        else:
            raise HTTPException(status_code=404, detail="State version not found")
    else:
        # Remove all versions and latest
        for file in os.listdir(state_dir):
            os.remove(os.path.join(state_dir, file))
    return Response(status_code=status.HTTP_204_NO_CONTENT)