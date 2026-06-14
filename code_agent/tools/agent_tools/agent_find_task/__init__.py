from tools.agent_tools.agent_find_task.schema import SCHEMAS
from tools.agent_tools.agent_find_task.tool import (
    run_agent_find_task,
    run_agent_execute_claimed_task,
    run_recover_failed_task,
)


HANDLERS = {
    "agent_find_task": run_agent_find_task,
    "agent_execute_claimed_task": run_agent_execute_claimed_task,
    "recover_failed_task": run_recover_failed_task,
}
