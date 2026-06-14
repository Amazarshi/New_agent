from tools.agent_tools import (
    agent_find_task,
    agent_task_loop,
    background,
    command,
    cron,
    file,
    mcp,
    memory,
    skill,
    subagent,
    task,
    todo,
    team,
    workspace,
)


TOOL_MODULES = [
    command,
    file,
    todo,
    subagent,
    skill,
    mcp,
    memory,
    task,
    background,
    cron,
    team,
    agent_find_task,
    agent_task_loop,
    workspace,
]


# Collect schemas from each tool category for the model.
TOOL_SCHEMAS = [
    schema
    for module in TOOL_MODULES
    for schema in module.SCHEMAS
]


# Collect handler functions from each tool category for the runner.
TOOL_HANDLERS = {}
for module in TOOL_MODULES:
    TOOL_HANDLERS.update(module.HANDLERS)
