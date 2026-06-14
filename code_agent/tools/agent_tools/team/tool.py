from tools.agent_tools.team.service import send_team_message, read_team_messages


def run_send_team_message(args):
    """从参数里取出团队协议消息，然后发送给目标角色。"""
    return send_team_message(
        args.get("sender", ""),
        args.get("receiver", ""),
        args.get("message_type", ""),
        args.get("task_id", ""),
        args.get("content", ""),
    )


def run_read_team_messages(args):
    """从参数里取出角色名和任务 id，然后读取这个角色的邮箱。"""
    return read_team_messages(
        args.get("role", ""),
        args.get("task_id", ""),
    )