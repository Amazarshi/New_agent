from tools.agent_tools.background.service import (
    start_background_command,
    list_background_jobs,
    pop_background_notifications,
)


def run_start_background_command(args):
    """Start a background command."""
    return start_background_command(args.get("command", ""))


def run_list_background_jobs(args):
    """List background jobs."""
    return list_background_jobs()


def run_pop_background_notifications(args):
    """Pop background job notifications."""
    return pop_background_notifications()
