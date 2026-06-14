from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = PACKAGE_DIR.parent
RUNTIME_DIR = PROJECT_ROOT / ".runtime"
MEMORY_DIR = RUNTIME_DIR / "memory"
TASK_DIR = RUNTIME_DIR / "tasks"
CRON_DIR = RUNTIME_DIR / "crons"
LOG_DIR = RUNTIME_DIR / "logs"
MAILBOX_DIR = RUNTIME_DIR / "mailboxes"
LOCK_DIR = RUNTIME_DIR / "locks"
BACKGROUND_STATE_FILE = RUNTIME_DIR / "background_jobs.json"
LOOP_STATE_FILE = RUNTIME_DIR / "agent_task_loops.json"
TODO_STATE_FILE = RUNTIME_DIR / "current_todo.json"


def ensure_runtime_dirs():
    """确保运行时数据目录存在。"""
    for path in [MEMORY_DIR, TASK_DIR, CRON_DIR, LOG_DIR, MAILBOX_DIR, LOCK_DIR]:
        path.mkdir(parents=True, exist_ok=True)
