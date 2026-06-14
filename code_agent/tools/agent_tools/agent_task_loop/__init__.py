from tools.agent_tools.agent_task_loop.schema import SCHEMAS
from tools.agent_tools.agent_task_loop.tool import (
    run_list_agent_task_loops,
    run_start_agent_task_loop,
    run_stop_agent_task_loop,
)


HANDLERS = {
    "start_agent_task_loop": run_start_agent_task_loop,
    "stop_agent_task_loop": run_stop_agent_task_loop,
    "list_agent_task_loops": run_list_agent_task_loops,
}
