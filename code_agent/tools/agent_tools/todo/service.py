from core.result import failure, success
from core.runtime import TODO_STATE_FILE
from core.store import write_json


CURRENT_TODOS = []
VALID_STATUS = ["pending", "in_progress", "completed"]


def reset_todos():
    """每次新 Agent 任务开始时重置当前 todo。"""
    global CURRENT_TODOS
    CURRENT_TODOS = []


def todo_write(todos):
    """保存 2-4 个 todo，作为修改文件前的执行计划。"""
    global CURRENT_TODOS

    if not isinstance(todos, list):
        return failure(
            code="todo.invalid_type",
            message="todos must be a list",
            category="invalid_arguments",
            retryable=False,
        )

    if len(todos) < 2 or len(todos) > 4:
        return failure(
            code="todo.invalid_count",
            message="Before editing files, write 2-4 todos",
            category="policy_violation",
            retryable=False,
        )

    checked_todos = []

    for index, todo in enumerate(todos, start=1):
        if not isinstance(todo, dict):
            return failure(
                code="todo.invalid_item",
                message=f"Todo {index} must be an object",
                category="invalid_arguments",
                retryable=False,
            )

        content = todo.get("content", "").strip()
        status = todo.get("status", "pending")

        if not content:
            return failure(
                code="todo.missing_content",
                message=f"Todo {index} is missing content",
                category="invalid_arguments",
                retryable=False,
            )

        if status not in VALID_STATUS:
            return failure(
                code="todo.invalid_status",
                message=f"Todo {index} has invalid status: {status}",
                category="invalid_arguments",
                retryable=False,
            )

        checked_todos.append({"content": content, "status": status})

    CURRENT_TODOS = checked_todos

    try:
        write_json(TODO_STATE_FILE, CURRENT_TODOS)
    except OSError:
        # todo 落盘失败不能阻塞当前 Agent 执行；部署时应修复 .runtime 权限。
        pass

    lines = ["Todo plan saved:"]
    for index, todo in enumerate(CURRENT_TODOS, start=1):
        lines.append(f"{index}. [{todo['status']}] {todo['content']}")

    return success(
        message="\n".join(lines),
        data={"todos": CURRENT_TODOS},
        code="todo.saved",
    )


def has_valid_todos():
    """检查当前任务是否已经有合格 todo。"""
    return 2 <= len(CURRENT_TODOS) <= 4
