from tools.agent_tools.task.schema import SCHEMAS
from tools.agent_tools.task.tool import (
    run_complete_task,
    run_create_task,
    run_list_tasks,
)


HANDLERS = {
    "create_task": run_create_task,
    "list_tasks": run_list_tasks,
    "complete_task": run_complete_task,
}
