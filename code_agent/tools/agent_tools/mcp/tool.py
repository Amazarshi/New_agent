from tools.agent_tools.mcp.service import call_mcp_tool_service, list_mcp_tools_service


def run_mcp_list_tools(args):
    """列出真实 MCP server 的工具。"""
    return list_mcp_tools_service(args.get("server_name", ""))


def run_mcp_call_tool(args):
    """调用真实 MCP server 的工具。"""
    return call_mcp_tool_service(
        args.get("server_name", ""),
        args.get("tool_name", ""),
        args.get("arguments", {}),
    )
