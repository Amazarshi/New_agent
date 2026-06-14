import json
import os
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta

from core.runtime import LOCK_DIR


class LockError(RuntimeError):
    """拿不到任务锁时抛出这个错误，上层会归类为 lock_conflict。"""


def _lock_path(name):
    safe_name = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in name)
    return LOCK_DIR / f"{safe_name}.lock"


def _is_stale(lock_file):
    try:
        data = json.loads(lock_file.read_text(encoding="utf-8"))
        expires_at = datetime.fromisoformat(data.get("expires_at", ""))
    except (OSError, ValueError, json.JSONDecodeError):
        return True

    return expires_at <= datetime.now()


def acquire_lock(name, ttl_seconds=300):
    """用 O_EXCL 创建锁文件，保证多进程同时抢任务时只有一个成功。"""
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    lock_file = _lock_path(name)
    token = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
    payload = {
        "name": name,
        "token": token,
        "pid": os.getpid(),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "expires_at": expires_at.isoformat(timespec="seconds"),
    }

    while True:
        try:
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False))
            return lock_file, token
        except FileExistsError:
            if not _is_stale(lock_file):
                raise LockError(f"Lock is already held: {name}")

            try:
                lock_file.unlink()
            except FileNotFoundError:
                continue


def release_lock(lock_file, token):
    """只释放自己创建的锁，避免误删别的进程刚创建的新锁。"""
    try:
        data = json.loads(lock_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return

    if data.get("token") == token:
        try:
            lock_file.unlink()
        except FileNotFoundError:
            pass


@contextmanager
def task_lock(name, ttl_seconds=300):
    """with 语法包装任务锁，正常结束或异常时都会释放锁。"""
    lock_file, token = acquire_lock(name, ttl_seconds=ttl_seconds)

    try:
        yield
    finally:
        release_lock(lock_file, token)
