import json
import re
from json import JSONDecodeError

from core.result import failure, now_text, success
from core.runtime import TASK_DIR


TASK_ID_PATTERN = re.compile(r"^task-[0-9]{3}$")
TASK_STATUSES = {"pending", "in_progress", "completed", "failed", "blocked"}


def ensure_task_dir():
    """确保任务目录存在。"""
    TASK_DIR.mkdir(parents=True, exist_ok=True)


def get_next_task_id():
    """根据已有任务文件生成下一个任务 id。"""
    ensure_task_dir()
    numbers = []

    for file in TASK_DIR.glob("task-*.json"):
        number_text = file.stem.replace("task-", "")

        if number_text.isdigit():
            numbers.append(int(number_text))

    return f"task-{max(numbers, default=0) + 1:03d}"


def validate_task_id(task_id):
    """任务 id 必须类似 task-001。"""
    return isinstance(task_id, str) and TASK_ID_PATTERN.fullmatch(task_id) is not None


def validate_blocked_by(blocked_by):
    """校验依赖任务列表。"""
    if blocked_by is None:
        return []

    if not isinstance(blocked_by, list):
        return None, "blocked_by must be a list"

    for task_id in blocked_by:
        if not validate_task_id(task_id):
            return None, f"Invalid blocked_by task id: {task_id}"

    return blocked_by, ""


def load_task_file(task_file):
    """读取单个任务文件，损坏时返回 None。"""
    try:
        return json.loads(task_file.read_text(encoding="utf-8"))
    except JSONDecodeError:
        return None


def save_task_file(task_file, task):
    """保存任务并更新时间。"""
    task["updated_at"] = now_text()
    task_file.write_text(
        json.dumps(task, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def create_task(title, description="", blocked_by=None, required_role="coder"):
    """创建一个可持久化任务。"""
    ensure_task_dir()
    checked_blocked_by, error = validate_blocked_by(blocked_by)

    if error:
        return failure(
            code="task.invalid_blocked_by",
            message=error,
            category="invalid_arguments",
            retryable=False,
        )

    task_id = get_next_task_id()
    current_time = now_text()
    task = {
        "id": task_id,
        "title": title,
        "description": description,
        "status": "pending",
        "required_role": required_role,
        "blocked_by": checked_blocked_by,
        "retry_count": 0,
        "max_retries": 2,
        "last_error": "",
        "error_category": "",
        "created_at": current_time,
        "updated_at": current_time,
    }

    task_file = TASK_DIR / f"{task_id}.json"

    try:
        save_task_file(task_file, task)
    except OSError as e:
        return failure(
            code="task.save_failed",
            message=f"任务保存失败：{e}",
            category="filesystem_error",
            retryable=True,
        )

    return success(
        message=f"Task created: {task_id} - {title}",
        data={"task": task},
        code="task.created",
    )


def list_tasks():
    """列出所有任务，损坏的任务文件会单独提示。"""
    ensure_task_dir()
    tasks = []
    broken_files = []

    for file in sorted(TASK_DIR.glob("task-*.json")):
        task = load_task_file(file)

        if task is None:
            broken_files.append(file.name)
            continue

        tasks.append(task)

    if not tasks:
        message = "No tasks"
        if broken_files:
            message = "No valid tasks. Broken task files: " + ", ".join(broken_files)
        return success(
            message=message,
            data={"tasks": [], "broken_files": broken_files},
            code="task.list_empty",
        )

    lines = [f"{task['id']} [{task['status']}] {task['title']}" for task in tasks]

    if broken_files:
        lines.append("Broken task files skipped: " + ", ".join(broken_files))

    return success(
        message="\n".join(lines),
        data={"tasks": tasks, "broken_files": broken_files},
        code="task.list",
    )


def complete_task(task_id):
    """把任务标记为 completed。"""
    if not validate_task_id(task_id):
        return failure(
            code="task.invalid_id",
            message="Invalid task id. Expected format: task-001",
            category="invalid_arguments",
            retryable=False,
        )

    ensure_task_dir()
    task_file = TASK_DIR / f"{task_id}.json"

    if not task_file.exists():
        return failure(
            code="task.not_found",
            message=f"Task does not exist: {task_id}",
            category="not_found",
            retryable=False,
        )

    task = load_task_file(task_file)

    if task is None:
        return failure(
            code="task.broken_file",
            message=f"Task file is broken: {task_file}",
            category="state_corrupted",
            retryable=False,
        )

    task["status"] = "completed"
    task["completed_at"] = now_text()
    try:
        save_task_file(task_file, task)
    except OSError as e:
        return failure(
            code="task.save_failed",
            message=f"任务保存失败：{e}",
            category="filesystem_error",
            retryable=True,
        )

    return success(
        message=f"Task completed: {task_id}",
        data={"task": task},
        code="task.completed",
    )
