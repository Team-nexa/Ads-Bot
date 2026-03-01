import os
from typing import List
from config import SESSION_DIR

def create_user_folder(user_id: int) -> str:
    os.makedirs(SESSION_DIR, exist_ok=True)
    return SESSION_DIR

def get_user_folder(user_id: int) -> str:
    return SESSION_DIR

def list_user_sessions(user_id: int) -> List[str]:
    if not os.path.exists(SESSION_DIR):
        return []
    prefix = f"{user_id}_"
    sessions = []
    try:
        for file in os.listdir(SESSION_DIR):
            if file.startswith(prefix) and file.endswith(".session"):
                sessions.append(file.replace(".session", ""))
        return sessions
    except Exception:
        return []

def session_exists(user_id: int, session_name: str) -> bool:
    path = os.path.join(SESSION_DIR, f"{session_name}.session")
    return os.path.exists(path)

def delete_session(user_id: int, session_name: str) -> bool:
    path = os.path.join(SESSION_DIR, f"{session_name}.session")
    if os.path.exists(path):
        os.remove(path)
        return True
    return False

def count_sessions(user_id: int) -> int:
    return len(list_user_sessions(user_id))