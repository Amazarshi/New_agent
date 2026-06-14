from tools.agent_tools.background.schema import SCHEMAS
from tools.agent_tools.background.tool import (
    run_list_background_jobs,
    run_pop_background_notifications,
    run_start_background_command,
)


HANDLERS = {
    "start_background_command": run_start_background_command,
    "list_background_jobs": run_list_background_jobs,
    "pop_background_notifications": run_pop_background_notifications,
}
