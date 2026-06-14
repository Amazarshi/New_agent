from tools.agent_tools.workspace.schema import SCHEMAS
from tools.agent_tools.workspace.tool import (
    run_create_task_workspace,
    run_read_workspace_file,
    run_write_workspace_file,
)


HANDLERS = {
    "create_task_workspace": run_create_task_workspace,
    "write_workspace_file": run_write_workspace_file,
    "read_workspace_file": run_read_workspace_file,
}
