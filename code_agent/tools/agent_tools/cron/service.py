import json
import re
from datetime import datetime, timedelta

from core.runtime import CRON_DIR

CRON_FILE = CRON_DIR / "jobs.json"
CRON_ID_PATTERN = re.compile(r"^cron-[0-9]{3}$")


def now_text():
    return datetime.now().isoformat(timespec="seconds")


def ensure_cron_file():
    CRON_DIR.mkdir(parents=True, exist_ok=True)

    if not CRON_FILE.exists():
        CRON_FILE.write_text("[]", encoding="utf-8")


def load_jobs():
    ensure_cron_file()
    return json.loads(CRON_FILE.read_text(encoding="utf-8"))


def save_jobs(jobs):
    ensure_cron_file()
    CRON_FILE.write_text(
        json.dumps(jobs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_next_job_id(jobs):
    numbers = []

    for job in jobs:
        number_text = job.get("id", "").replace("cron-", "")

        if number_text.isdigit():
            numbers.append(int(number_text))

    return f"cron-{max(numbers, default=0) + 1:03d}"


def validate_delay_seconds(delay_seconds):
    """校验延迟秒数必须是大于 0 的整数。"""
    try:
        delay_seconds = int(delay_seconds)
    except (TypeError, ValueError):
        return None, "delay_seconds must be an integer"

    if delay_seconds < 1:
        return None, "delay_seconds must be at least 1"

    return delay_seconds, ""


def validate_cron_job_id(job_id):
    """校验定时任务 id 必须类似 cron-001。"""
    if not isinstance(job_id, str):
        return False

    return CRON_ID_PATTERN.fullmatch(job_id) is not None


def create_cron_job(delay_seconds, prompt):
    delay_seconds, error = validate_delay_seconds(delay_seconds)

    if error:
        return error

    jobs = load_jobs()
    job_id = get_next_job_id(jobs)
    current_time = datetime.now()
    run_at = current_time + timedelta(seconds=delay_seconds)

    job = {
        "id": job_id,
        "prompt": prompt,
        "status": "pending",
        "run_at": run_at.isoformat(timespec="seconds"),
        "created_at": current_time.isoformat(timespec="seconds"),
        "updated_at": current_time.isoformat(timespec="seconds"),
    }

    jobs.append(job)
    save_jobs(jobs)

    return f"Cron job created: {job_id}, run at {job['run_at']}"


def list_cron_jobs():
    jobs = load_jobs()

    if not jobs:
        return "No cron jobs"

    return "\n".join(
        f"{job['id']} [{job['status']}] {job['run_at']} {job['prompt']}"
        for job in jobs
    )


def cancel_cron_job(job_id):
    if not validate_cron_job_id(job_id):
        return "Invalid cron job id. Expected format: cron-001"

    jobs = load_jobs()

    for job in jobs:
        if job["id"] == job_id:
            job["status"] = "cancelled"
            job["updated_at"] = now_text()
            save_jobs(jobs)
            return f"Cron job cancelled: {job_id}"

    return f"Cron job does not exist: {job_id}"


def pop_due_cron_prompts():
    jobs = load_jobs()
    current_time = datetime.now()
    due_prompts = []

    for job in jobs:
        if job["status"] != "pending":
            continue

        run_at = datetime.fromisoformat(job["run_at"])

        if run_at <= current_time:
            job["status"] = "triggered"
            job["updated_at"] = now_text()
            due_prompts.append(f"{job['id']} is due: {job['prompt']}")

    save_jobs(jobs)

    if not due_prompts:
        return "No due cron jobs"

    return "\n".join(due_prompts)
