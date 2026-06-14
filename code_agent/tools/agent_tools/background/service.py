import subprocess
import threading

from core.result import failure, now_text, success
from core.runtime import BACKGROUND_STATE_FILE
from core.safety import check_command_safe
from core.store import read_json, write_json


BACKGROUND_JOBS = {}
NOTIFICATIONS = []
STATE_LOCK = threading.Lock()
MAX_OUTPUT_CHARS = 4000


def shorten_output(text):
    """后台输出可能很长，落盘前做截断，节约空间和 token。"""
    text = str(text or "")

    if len(text) <= MAX_OUTPUT_CHARS:
        return text

    return text[:MAX_OUTPUT_CHARS] + "\n...[输出过长，已截断]"


def load_state():
    """读取后台任务状态，重启后 running 任务标记为 stopped_on_restart。"""
    state = read_json(BACKGROUND_STATE_FILE, {"jobs": {}, "notifications": []})
    jobs = state.get("jobs", {})

    for job in jobs.values():
        if job.get("status") in ["pending", "running"]:
            job["status"] = "stopped_on_restart"
            job["updated_at"] = now_text()

    BACKGROUND_JOBS.update(jobs)
    NOTIFICATIONS.extend(state.get("notifications", []))


def save_state():
    """把后台任务和通知队列保存到磁盘。"""
    write_json(
        BACKGROUND_STATE_FILE,
        {
            "jobs": BACKGROUND_JOBS,
            "notifications": NOTIFICATIONS,
        },
    )


def ensure_loaded():
    """懒加载状态，避免导入模块时就写文件。"""
    if not BACKGROUND_JOBS and not NOTIFICATIONS:
        load_state()


def next_job_id():
    """根据已有后台任务生成下一个 job id。"""
    numbers = []

    for job_id in BACKGROUND_JOBS:
        if job_id.startswith("bg-") and job_id[3:].isdigit():
            numbers.append(int(job_id[3:]))

    return f"bg-{max(numbers, default=0) + 1:03d}"


def update_job(job_id, **fields):
    """更新后台任务状态并落盘。"""
    BACKGROUND_JOBS[job_id].update(fields)
    BACKGROUND_JOBS[job_id]["updated_at"] = now_text()
    save_state()


def push_notification(job_id, message):
    """把后台任务完成或失败消息放入通知队列。"""
    NOTIFICATIONS.append(
        {
            "job_id": job_id,
            "message": message,
            "time": now_text(),
        }
    )
    save_state()


def run_command_in_background(job_id, command):
    """真正执行后台命令，并把结果持久化。"""
    with STATE_LOCK:
        update_job(job_id, status="running")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300,
        )

        status = "completed" if result.returncode == 0 else "failed"
        message = f"Background job {status}: {job_id}"

        with STATE_LOCK:
            update_job(
                job_id,
                status=status,
                returncode=result.returncode,
                stdout=shorten_output(result.stdout.strip()),
                stderr=shorten_output(result.stderr.strip()),
            )
            push_notification(job_id, message)

    except subprocess.TimeoutExpired:
        with STATE_LOCK:
            update_job(
                job_id,
                status="timeout",
                stderr="Background job timed out",
            )
            push_notification(job_id, f"Background job timed out: {job_id}")

    except Exception as e:
        with STATE_LOCK:
            update_job(
                job_id,
                status="failed",
                stderr=str(e),
            )
            push_notification(job_id, f"Background job error: {job_id}")


def start_background_command(command):
    """启动后台命令，立即返回 job id。"""
    ensure_loaded()
    allowed, message = check_command_safe(command)

    if not allowed:
        return failure(
            code="background.denied",
            message=message,
            category="permission_denied",
            retryable=False,
        )

    with STATE_LOCK:
        job_id = next_job_id()
        BACKGROUND_JOBS[job_id] = {
            "id": job_id,
            "command": command,
            "status": "pending",
            "stdout": "",
            "stderr": "",
            "returncode": None,
            "created_at": now_text(),
            "updated_at": now_text(),
        }
        try:
            save_state()
        except OSError as e:
            return failure(
                code="background.save_failed",
                message=f"后台任务状态保存失败：{e}",
                category="filesystem_error",
                retryable=True,
            )

    thread = threading.Thread(
        target=run_command_in_background,
        args=(job_id, command),
        daemon=True,
    )
    thread.start()

    return success(
        message=f"Background job started: {job_id}",
        data={"job_id": job_id},
        code="background.started",
    )


def list_background_jobs():
    """查看后台任务列表。"""
    ensure_loaded()

    if not BACKGROUND_JOBS:
        return success(
            message="No background jobs",
            data={"jobs": []},
            code="background.list_empty",
        )

    lines = [
        f"{job['id']} [{job['status']}] {job['command']}"
        for job in BACKGROUND_JOBS.values()
    ]

    return success(
        message="\n".join(lines),
        data={"jobs": list(BACKGROUND_JOBS.values())},
        code="background.list",
    )


def pop_background_notifications():
    """读取并清空后台通知。"""
    ensure_loaded()

    if not NOTIFICATIONS:
        return success(
            message="No background notifications",
            data={"notifications": []},
            code="background.notifications_empty",
        )

    notifications = list(NOTIFICATIONS)
    lines = [f"{item['time']} {item['message']}" for item in notifications]
    NOTIFICATIONS.clear()
    save_state()

    return success(
        message="\n".join(lines),
        data={"notifications": notifications},
        code="background.notifications",
    )
