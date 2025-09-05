from path_tools import _state_dir
import os
import json

def check_lock_id(project: str, state_name: str, ID: str) -> bool:
    lock_path = os.path.join(_state_dir(project, state_name), ".lock")
    if not os.path.exists(lock_path):
        return False
    with open(lock_path, "r") as f:
        cur_info = json.loads(f.read() or "{}")
    return ID == cur_info.get("ID")