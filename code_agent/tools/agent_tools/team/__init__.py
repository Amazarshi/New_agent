from tools.agent_tools.team.schema import SCHEMAS
from tools.agent_tools.team.tool import (
    run_send_team_message,
    run_read_team_messages,
)


HANDLERS = {
    "send_team_message": run_send_team_message,
    "read_team_messages": run_read_team_messages,
}