import os


DATA_DIR = os.getenv("STATE_DATA_DIR", "./data")

def _state_dir(project_id: int, state_name: str) -> str:
    path = os.path.join(DATA_DIR, str(project_id), state_name)
    os.makedirs(path, exist_ok=True)
    return path

def _latest_state_path(project_id: int, state_name: str) -> str:
    return os.path.join(_state_dir(project_id, state_name), "latest.tfstate")

def _versioned_state_path(project_id: int, state_name: str, version: int) -> str:
    return os.path.join(_state_dir(project_id, state_name), f"{version}.tfstate")


def _versioned_state_info_path(project: str, state_name: str, version: int) -> str:
    return os.path.join(_state_dir(project, state_name), f"{version}.tfstate.meta")