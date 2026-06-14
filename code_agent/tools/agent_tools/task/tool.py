from tools.agent_tools.task.service import create_task, list_tasks, complete_task


def run_create_task(args):
    """Create a task."""
    return create_task(
        args.get("title", ""),
        args.get("description", ""),
        args.get("blocked_by", []),
    )


def run_list_tasks(args):
    """List all tasks."""
    return list_tasks()


def run_complete_task(args):
    """Complete a task."""
    return complete_task(args.get("task_id", ""))
