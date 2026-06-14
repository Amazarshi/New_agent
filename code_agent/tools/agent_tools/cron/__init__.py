from tools.agent_tools.cron.schema import SCHEMAS
from tools.agent_tools.cron.tool import (
    run_cancel_cron_job,
    run_create_cron_job,
    run_list_cron_jobs,
    run_pop_due_cron_prompts,
)


HANDLERS = {
    "create_cron_job": run_create_cron_job,
    "list_cron_jobs": run_list_cron_jobs,
    "cancel_cron_job": run_cancel_cron_job,
    "pop_due_cron_prompts": run_pop_due_cron_prompts,
}
