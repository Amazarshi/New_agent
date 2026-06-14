import threading

from core.result import failure, success
from core.runtime import LOOP_STATE_FILE
from core.store import read_json, write_json
from tools.agent_tools.agent_find_task.service import (
    AGENT_ROLES,
    agent_execute_claimed_task,
    agent_find_task,
)


LOOPS = {}
STOP_EVENTS = {}
LOOP_LOCK = threading.Lock()


def load_loop_state():
    """读取上次保存的轮询器状态，旧进程里的 running 线程会标记为 stopped_on_restart。"""
    state = read_json(LOOP_STATE_FILE, {})

    for loop_id, loop in state.items():
        if loop.get("status") in ["starting", "running", "stopping"]:
            loop["status"] = "stopped_on_restart"
        LOOPS[loop_id] = loop


def save_loop_state():
    """保存轮询器状态，方便审计和重启后查看。"""
    write_json(LOOP_STATE_FILE, LOOPS)


def ensure_loaded():
    """懒加载状态，避免模块导入时创建目录。"""
    if not LOOPS:
        load_loop_state()


def next_loop_id():
    """根据已有状态生成下一个 loop id。"""
    numbers = []

    for loop_id in LOOPS:
        if loop_id.startswith("loop-") and loop_id[5:].isdigit():
            numbers.append(int(loop_id[5:]))

    return f"loop-{max(numbers, default=0) + 1:03d}"


def get_claimed_task_id(result):
    """从结构化领取结果里取出 task_id。"""
    if not isinstance(result, dict) or not result.get("ok"):
        return ""

    task = (result.get("data") or {}).get("task")

    if not task:
        return ""

    return task.get("id", "")


def validate_interval_seconds(interval_seconds):
    """限制轮询间隔，避免过度消耗 token。"""
    try:
        interval_seconds = int(interval_seconds)
    except (TypeError, ValueError):
        return None, "interval_seconds must be an integer"

    if interval_seconds < 3:
        return None, "interval_seconds must be at least 3"

    return interval_seconds, ""


def has_running_loop_for_role(role):
    """同一角色只允许一个运行中的轮询器。"""
    for loop in LOOPS.values():
        if loop["role"] == role and loop["status"] in ["starting", "running"]:
            return True

    return False


def update_loop(loop_id, **fields):
    """更新内存状态并立即落盘。"""
    LOOPS[loop_id].update(fields)
    save_loop_state()


def run_agent_task_loop(loop_id, role, interval_seconds, stop_event):
    """后台轮询领取任务，领取成功后立即执行。"""
    with LOOP_LOCK:
        update_loop(loop_id, status="running")

    while not stop_event.is_set():
        try:
            claim_result = agent_find_task(role)
            task_id = get_claimed_task_id(claim_result)

            with LOOP_LOCK:
                update_loop(
                    loop_id,
                    last_claim_result=claim_result,
                    last_task_id=task_id,
                )

            if task_id:
                execute_result = agent_execute_claimed_task(role, task_id)

                with LOOP_LOCK:
                    update_loop(loop_id, last_execute_result=execute_result)

        except Exception as e:
            with LOOP_LOCK:
                update_loop(loop_id, status="failed", last_error=str(e))
            return

        stop_event.wait(interval_seconds)

    with LOOP_LOCK:
        update_loop(loop_id, status="stopped")


def start_agent_task_loop(role="coder", interval_seconds=10):
    """启动一个后台任务轮询器。"""
    ensure_loaded()

    if role not in AGENT_ROLES:
        return failure(
            code="agent.unknown_role",
            message=f"Unknown agent role: {role}",
            category="invalid_arguments",
            retryable=False,
        )

    interval_seconds, error = validate_interval_seconds(interval_seconds)

    if error:
        return failure(
            code="loop.invalid_interval",
            message=error,
            category="invalid_arguments",
            retryable=False,
        )

    with LOOP_LOCK:
        if has_running_loop_for_role(role):
            return failure(
                code="loop.already_running",
                message=f"Agent task loop already running for role: {role}",
                category="invalid_state",
                retryable=False,
            )

        loop_id = next_loop_id()
        stop_event = threading.Event()
        STOP_EVENTS[loop_id] = stop_event
        LOOPS[loop_id] = {
            "id": loop_id,
            "role": role,
            "interval_seconds": interval_seconds,
            "status": "starting",
            "last_task_id": "",
            "last_claim_result": {},
            "last_execute_result": {},
            "last_error": "",
        }
        save_loop_state()

    thread = threading.Thread(
        target=run_agent_task_loop,
        args=(loop_id, role, interval_seconds, stop_event),
        daemon=True,
    )
    thread.start()

    return success(
        message=f"Agent task loop started: {loop_id}",
        data={"loop_id": loop_id},
        code="loop.started",
    )


def stop_agent_task_loop(loop_id):
    """停止指定后台任务轮询器。"""
    ensure_loaded()

    with LOOP_LOCK:
        loop = LOOPS.get(loop_id)

        if loop is None:
            return failure(
                code="loop.not_found",
                message=f"Agent task loop does not exist: {loop_id}",
                category="not_found",
                retryable=False,
            )

        if loop["status"] not in ["starting", "running"]:
            return failure(
                code="loop.not_running",
                message=f"Agent task loop is not running: {loop_id}",
                category="invalid_state",
                retryable=False,
            )

        loop["status"] = "stopping"
        save_loop_state()
        stop_event = STOP_EVENTS.get(loop_id)

    if stop_event is not None:
        stop_event.set()

    return success(
        message=f"Agent task loop stopping: {loop_id}",
        data={"loop_id": loop_id},
        code="loop.stopping",
    )


def list_agent_task_loops():
    """列出当前进程和持久化状态里的轮询器。"""
    ensure_loaded()

    with LOOP_LOCK:
        if not LOOPS:
            return success(
                message="No agent task loops",
                data={"loops": []},
                code="loop.list_empty",
            )

        lines = []

        for loop in LOOPS.values():
            last_task_text = loop.get("last_task_id") or "-"
            lines.append(
                f"{loop['id']} [{loop['status']}] "
                f"{loop['role']} every {loop['interval_seconds']}s "
                f"last_task={last_task_text}"
            )

        return success(
            message="\n".join(lines),
            data={"loops": list(LOOPS.values())},
            code="loop.list",
        )
