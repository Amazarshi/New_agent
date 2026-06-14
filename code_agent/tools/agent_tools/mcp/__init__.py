from tools.agent_tools.mcp.schema import SCHEMAS
from tools.agent_tools.mcp.tool import run_mcp_call_tool, run_mcp_list_tools


HANDLERS = {
    "mcp_list_tools": run_mcp_list_tools,
    "mcp_call_tool": run_mcp_call_tool,
}
