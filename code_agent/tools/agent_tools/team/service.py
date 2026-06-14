import json
from datetime import datetime
from tools.agent_tools.task.service import validate_task_id
from core.runtime import MAILBOX_DIR


TEAM_ROLES = ["leader", "coder", "reviewer"]

TEAM_MESSAGE_TYPES = [
    "request_plan",
    "submit_plan",
    "approve_plan",
    "reject_plan",
    "task_done",
    "shutdown",
]


def ensure_team_mailboxes():
    """确保每个 Agent 都有自己的邮箱文件。"""
    MAILBOX_DIR.mkdir(parents=True, exist_ok=True)

    for role in TEAM_ROLES:
        mailbox_file = MAILBOX_DIR / f"{role}.jsonl"
        mailbox_file.touch(exist_ok=True)


def read_all_team_messages():
    """读取所有邮箱里的团队消息，用来检查协议流程。"""
    ensure_team_mailboxes()
    messages = []

    for role in TEAM_ROLES:
        mailbox_file = MAILBOX_DIR / f"{role}.jsonl"

        with mailbox_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    messages.append(json.loads(line))

    return messages


def has_message(sender, receiver, message_type, task_id):
    """检查同一个任务下，是否存在指定类型的消息。"""
    for message in read_all_team_messages():
        if (
            message.get("from") == sender
            and message.get("to") == receiver
            and message.get("type") == message_type
            and message.get("task_id") == task_id
        ):
            return True

    return False


def check_team_protocol(sender, receiver, message_type, task_id):
    """检查团队消息是否符合 s16 的固定流程。"""
    if message_type == "request_plan":
        if sender != "leader":
            return False, "Only leader can send request_plan"
        return True, ""

    if message_type == "submit_plan":
        if receiver != "leader":
            return False, "submit_plan must be sent to leader"

        if not has_message("leader", sender, "request_plan", task_id):
            return False, "submit_plan requires leader request_plan first"

        return True, ""

    if message_type in ["approve_plan", "reject_plan"]:
        if sender != "leader":
            return False, f"Only leader can send {message_type}"

        if not has_message(receiver, "leader", "submit_plan", task_id):
            return False, f"{message_type} requires submit_plan first"

        return True, ""

    if message_type == "task_done":
        if receiver != "leader":
            return False, "task_done must be sent to leader"

        if not has_message("leader", sender, "approve_plan", task_id):
            return False, "task_done requires leader approve_plan first"

        return True, ""

    if message_type == "shutdown":
        if sender != "leader":
            return False, "Only leader can send shutdown"

        return True, ""

    return False, f"Unknown message type: {message_type}"


def send_team_message(sender, receiver, message_type, task_id, content):
    """按照团队协议发送消息，把消息写入接收者邮箱。"""
    ensure_team_mailboxes()

    if sender not in TEAM_ROLES:
        return f"Unknown sender: {sender}"

    if receiver not in TEAM_ROLES:
        return f"Unknown receiver: {receiver}"

    if message_type not in TEAM_MESSAGE_TYPES:
        return f"Unknown message type: {message_type}"
    
    if not validate_task_id(task_id):
        return "Invalid task id. Expected format: task-001"

    allowed, reason = check_team_protocol(sender, receiver, message_type, task_id)

    if not allowed:
        return f"Team protocol rejected: {reason}"

    message = {
        "from": sender,
        "to": receiver,
        "type": message_type,
        "content": content,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "task_id": task_id,
    }

    mailbox_file = MAILBOX_DIR / f"{receiver}.jsonl"

    with mailbox_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(message, ensure_ascii=False) + "\n")

    return f"Message sent from {sender} to {receiver}: {message_type}"


def read_team_messages(role, task_id):
    """读取某个 Agent 在指定任务下的邮箱消息。"""
    ensure_team_mailboxes()

    if role not in TEAM_ROLES:
        return f"Unknown role: {role}"

    if not validate_task_id(task_id):
        return "Invalid task id. Expected format: task-001"

    mailbox_file = MAILBOX_DIR / f"{role}.jsonl"
    messages = []

    with mailbox_file.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            message = json.loads(line)

            if message.get("task_id") == task_id:
                messages.append(message)

    if not messages:
        return f"No messages for {role} in {task_id}"

    return json.dumps(messages, ensure_ascii=False, indent=2)