from core.locks import LockError, task_lock
from core.result import failure, parse_result_text, success
from core.runtime import TASK_DIR
from tools.agent_tools.task.service import (
    load_task_file,
    now_text,
    save_task_file,
    validate_task_id,
)


AGENT_ROLES = ["leader", "coder", "reviewer"]
DEFAULT_MAX_RETRIES = 2


def is_task_completed(task_id):
    """检查依赖任务是否已经完成。"""
    task_file = TASK_DIR / f"{task_id}.json"

    if not task_file.exists():
        return False

    task = load_task_file(task_file)

    if task is None:
        return False

    return task.get("status") == "completed"


def dependencies_are_done(task):
    """只有依赖任务全部完成，当前任务才可以领取。"""
    blocked_by = task.get("blocked_by", [])

    if not isinstance(blocked_by, list):
        return False

    for task_id in blocked_by:
        if not validate_task_id(task_id):
            return False

        if not is_task_completed(task_id):
            return False

    return True


def can_agent_do_task(role, task):
    """判断某个角色是否可以领取任务。"""
    if role not in AGENT_ROLES:
        return False

    if task.get("status") != "pending":
        return False

    required_role = task.get("required_role", "coder")

    if role != required_role:
        return False

    return dependencies_are_done(task)


def agent_find_task(role):
    """扫描任务目录，找到可领取任务，并用锁保证不会重复领取。"""
    if role not in AGENT_ROLES:
        return failure(
            code="agent.unknown_role",
            message=f"Unknown agent role: {role}",
            category="invalid_arguments",
            retryable=False,
        )

    TASK_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with task_lock("claim_tasks", ttl_seconds=30):
            for task_file in sorted(TASK_DIR.glob("task-*.json")):
                task = load_task_file(task_file)

                if task is None:
                    continue

                if not can_agent_do_task(role, task):
                    continue

                task["status"] = "in_progress"
                task["claimed_by"] = role
                task["claimed_at"] = now_text()
                task["max_retries"] = int(task.get("max_retries", DEFAULT_MAX_RETRIES))
                save_task_file(task_file, task)

                return success(
                    message=f"Agent {role} claimed task: {task['id']}",
                    data={"task": task},
                    code="agent.task_claimed",
                )
    except LockError as e:
        return failure(
            code="lock.claim_conflict",
            message=str(e),
            category="lock_conflict",
            retryable=True,
        )
    except OSError as e:
        return failure(
            code="lock.filesystem_error",
            message=f"任务锁写入失败：{e}",
            category="filesystem_error",
            retryable=True,
        )

    return success(
        message=f"No available task for agent: {role}",
        data={"task": None},
        code="agent.no_available_task",
    )


def classify_agent_result(result):
    """把 Agent 执行结果分类，方便任务失败后定位原因。"""
    parsed = parse_result_text(result)

    if parsed is None:
        return False, "", ""

    if parsed.get("ok"):
        return False, "", ""

    error = parsed.get("error") or {}
    return True, error.get("category", "execution_error"), parsed.get("message", "")


def get_retry_count(task):
    """读取任务已重试次数，异常时按 0 处理。"""
    try:
        return int(task.get("retry_count", 0))
    except (TypeError, ValueError):
        return 0


def get_max_retries(task):
    """读取任务最大重试次数，异常时使用默认值。"""
    try:
        max_retries = int(task.get("max_retries", DEFAULT_MAX_RETRIES))
    except (TypeError, ValueError):
        return DEFAULT_MAX_RETRIES

    if max_retries < 0:
        return DEFAULT_MAX_RETRIES

    return max_retries


def mark_task_retrying(task_file, task, retry_count, error_category, error):
    """记录一次自动重试。"""
    task["status"] = "in_progress"
    task["retry_count"] = retry_count
    task["last_error"] = error
    task["error_category"] = error_category
    task["retry_at"] = now_text()
    save_task_file(task_file, task)


def mark_task_failed(task_file, task, error_category, error):
    """自动重试耗尽后标记为 failed。"""
    task["status"] = "failed"
    task["failed_at"] = now_text()
    task["last_error"] = error
    task["error_category"] = error_category
    save_task_file(task_file, task)


def recover_failed_task(task_id):
    """手动恢复 failed 任务，让它重新回到 pending。"""
    if not validate_task_id(task_id):
        return failure(
            code="task.invalid_id",
            message="Invalid task id. Expected format: task-001",
            category="invalid_arguments",
            retryable=False,
        )

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
            message=f"Task file is broken: {task_id}",
            category="state_corrupted",
            retryable=False,
        )

    if task.get("status") != "failed":
        return failure(
            code="task.not_failed",
            message=f"Task is not failed: {task_id}",
            category="invalid_state",
            retryable=False,
        )

    task["status"] = "pending"
    task["retry_count"] = 0
    task["max_retries"] = get_max_retries(task)
    task["recovered_at"] = now_text()
    task["last_error"] = ""
    task["error_category"] = ""
    task["claimed_by"] = ""
    task["claimed_at"] = ""
    save_task_file(task_file, task)

    return success(
        message=f"Task recovered and ready to retry: {task_id}",
        data={"task": task},
        code="task.recovered",
    )


def agent_execute_claimed_task(role, task_id):
    """执行已领取任务，失败时按分类记录并自动重试。"""
    if role not in AGENT_ROLES:
        return failure(
            code="agent.unknown_role",
            message=f"Unknown agent role: {role}",
            category="invalid_arguments",
            retryable=False,
        )

    if not validate_task_id(task_id):
        return failure(
            code="task.invalid_id",
            message="Invalid task id. Expected format: task-001",
            category="invalid_arguments",
            retryable=False,
        )

    task_file = TASK_DIR / f"{task_id}.json"

    try:
        with task_lock(task_id, ttl_seconds=600):
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
                    message=f"Task file is broken: {task_id}",
                    category="state_corrupted",
                    retryable=False,
                )

            if task.get("status") != "in_progress":
                return failure(
                    code="task.invalid_state",
                    message=f"Task is not in_progress: {task_id}",
                    category="invalid_state",
                    retryable=False,
                )

            if task.get("claimed_by") != role:
                return failure(
                    code="task.claim_owner_mismatch",
                    message=f"Task is not claimed by agent: {role}",
                    category="permission_denied",
                    retryable=False,
                )

            prompt = (
                "你现在要执行一个已经领取的任务。\n\n"
                f"任务 id：{task_id}\n"
                f"任务标题：{task.get('title', '')}\n"
                f"任务描述：{task.get('description', '')}\n\n"
                f"本任务的隔离工作区是：.workspaces/{task_id}\n"
                "如果需要写入任务产物，必须写入这个工作区，不要写到项目根目录。\n\n"
                "请完成这个任务。完成后总结你做了什么。"
            )

            from core.agent_executor import run_agent_task

            max_retries = get_max_retries(task)
            retry_count = get_retry_count(task)
            task["max_retries"] = max_retries

            while True:
                try:
                    result = run_agent_task(prompt)
                except Exception as e:
                    result = f"Agent task execution error: {e}"

                failed, error_category, error = classify_agent_result(result)

                if not failed:
                    break

                if retry_count >= max_retries:
                    task["retry_count"] = retry_count
                    mark_task_failed(task_file, task, error_category, error)
                    return failure(
                        code="agent.task_failed",
                        message=f"Agent {role} failed task permanently: {task_id}",
                        category=error_category or "execution_error",
                        details={"result": result},
                        retryable=False,
                    )

                retry_count += 1
                mark_task_retrying(task_file, task, retry_count, error_category, error)

            task["status"] = "completed"
            task["completed_at"] = now_text()
            task["result"] = result
            task["last_error"] = ""
            task["error_category"] = ""
            task["retry_count"] = retry_count
            save_task_file(task_file, task)

            return success(
                message=f"Agent {role} executed and completed task: {task_id}",
                data={"task": task, "result": result},
                code="agent.task_completed",
            )
    except LockError as e:
        return failure(
            code="lock.task_conflict",
            message=str(e),
            category="lock_conflict",
            retryable=True,
        )
    except OSError as e:
        return failure(
            code="lock.filesystem_error",
            message=f"任务锁写入失败：{e}",
            category="filesystem_error",
            retryable=True,
        )
