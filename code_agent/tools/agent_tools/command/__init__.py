from tools.agent_tools.command.schema import SCHEMAS
from tools.agent_tools.command.tool import run_bash


HANDLERS = {
    "bash": run_bash,
}
