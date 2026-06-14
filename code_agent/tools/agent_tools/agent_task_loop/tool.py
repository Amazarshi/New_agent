from tools.agent_tools.agent_task_loop.service import (
    list_agent_task_loops,
    start_agent_task_loop,
    stop_agent_task_loop,
)


def run_start_agent_task_loop(args):
    """从参数中取出角色和间隔，启动任务轮询器。"""
    return start_agent_task_loop(
        args.get("role", "coder"),
        args.get("interval_seconds", 10),
    )


def run_stop_agent_task_loop(args):
    """从参数中取出轮询器 id，然后停止它。"""
    return stop_agent_task_loop(args.get("loop_id", ""))


def run_list_agent_task_loops(args):
    """列出当前所有任务轮询器。"""
    return list_agent_task_loops()
