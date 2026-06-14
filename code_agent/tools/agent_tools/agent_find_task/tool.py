from tools.agent_tools.agent_find_task.service import (
    agent_find_task,
    agent_execute_claimed_task,
    recover_failed_task,
)


def run_agent_find_task(args):
    """从参数中取出 Agent 角色，然后自动领取可做任务。"""
    return agent_find_task(args.get("role", ""))


def run_agent_execute_claimed_task(args):
    """执行当前 Agent 已领取的任务，并在完成后标记 completed。"""
    return agent_execute_claimed_task(
        args.get("role", ""),
        args.get("task_id", ""),
    )


def run_recover_failed_task(args):
    """把最终失败的任务恢复为 pending，并重置重试次数。"""
    return recover_failed_task(args.get("task_id", ""))
