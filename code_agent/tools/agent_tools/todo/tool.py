from tools.agent_tools.todo.service import todo_write


def run_todo_write(args):
    """Write todos for the current task."""
    return todo_write(args.get("todos", []))
