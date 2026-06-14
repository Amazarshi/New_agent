from tools.agent_tools.cron.service import (
    create_cron_job,
    list_cron_jobs,
    cancel_cron_job,
    pop_due_cron_prompts,
)


def run_create_cron_job(args):
    """Create a cron job."""
    return create_cron_job(
        args.get("delay_seconds", 60),
        args.get("prompt", ""),
    )


def run_list_cron_jobs(args):
    """List cron jobs."""
    return list_cron_jobs()


def run_cancel_cron_job(args):
    """Cancel a cron job."""
    return cancel_cron_job(args.get("job_id", ""))


def run_pop_due_cron_prompts(args):
    """Pop due cron prompts."""
    return pop_due_cron_prompts()
