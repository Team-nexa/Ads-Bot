import asyncio
from typing import Dict, Optional

_running_tasks: Dict[int, asyncio.Task] = {}

def register_task(user_id: int, task: asyncio.Task) -> None:
    old_task = _running_tasks.get(user_id)
    if old_task and not old_task.done():
        old_task.cancel()
    _running_tasks[user_id] = task

def get_task(user_id: int) -> Optional[asyncio.Task]:
    return _running_tasks.get(user_id)

def cancel_task(user_id: int) -> bool:
    task = _running_tasks.get(user_id)
    if not task:
        return False
    if not task.done():
        task.cancel()
    _running_tasks.pop(user_id, None)
    return True

def is_running(user_id: int) -> bool:
    task = _running_tasks.get(user_id)
    return bool(task and not task.done())

def cleanup_finished():
    finished_users = [user_id for user_id, task in _running_tasks.items() if task.done()]
    for user_id in finished_users:
        _running_tasks.pop(user_id, None)

running_tasks = _running_tasks