from tools.agent_tools.memory.service import remember


def run_remember(args):
    """Save an important memory."""
    return remember(
        args.get("kind", ""),
        args.get("content", ""),
    )
