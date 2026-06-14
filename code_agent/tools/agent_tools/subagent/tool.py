from tools.agent_tools.subagent.service import ask_subagent


def run_ask_subagent(args):
    """Ask a subagent to read a file and complete a small task."""
    return ask_subagent(
        args.get("path", ""),
        args.get("task", ""),
    )
