import json

from core.mcp_client import call_mcp_tool, list_mcp_tools
from core.result import failure, success


def list_mcp_tools_service(server_name):
    """把真实 MCP 工具列表转换成统一工具返回结构。"""
    if not server_name:
        return failure(
            code="mcp.missing_server",
            message="缺少 server_name，例如 chrome-devtools。",
            category="invalid_arguments",
            retryable=False,
        )

    try:
        result = list_mcp_tools(server_name)
    except Exception as e:
        return failure(
            code="mcp.list_failed",
            message=f"读取 MCP 工具失败：{type(e).__name__}: {e!r}",
            category="execution_error",
            details={"server_name": server_name},
            retryable=True,
        )

    tools = result.get("tools", [])
    names = [tool.get("name", "") for tool in tools if tool.get("name")]
    return success(
        message="\n".join(names) if names else "MCP server 没有返回工具。",
        data={"server_name": server_name, "tools": tools},
        code="mcp.tools_listed",
    )


def call_mcp_tool_service(server_name, tool_name, arguments):
    """调用真实 MCP 工具，并保持项目统一返回格式。"""
    if not server_name or not tool_name:
        return failure(
            code="mcp.missing_arguments",
            message="缺少 server_name 或 tool_name。",
            category="invalid_arguments",
            retryable=False,
        )

    if not isinstance(arguments, dict):
        return failure(
            code="mcp.invalid_arguments",
            message="arguments 必须是 JSON 对象。",
            category="invalid_arguments",
            details={"arguments": arguments},
            retryable=False,
        )

    try:
        result = call_mcp_tool(server_name, tool_name, arguments)
    except Exception as e:
        return failure(
            code="mcp.call_failed",
            message=f"MCP 工具调用失败：{type(e).__name__}: {e!r}",
            category="execution_error",
            retryable=True,
            details={
                "server_name": server_name,
                "tool_name": tool_name,
                "arguments": arguments,
            },
        )

    if result.get("is_error"):
        return failure(
            code="mcp.tool_error",
            message=result.get("message", "MCP 工具返回错误。"),
            category="execution_error",
            details={"raw": result.get("raw")},
            retryable=False,
        )

    return success(
        message=result.get("message", ""),
        data={
            "server_name": server_name,
            "tool_name": tool_name,
            "arguments": arguments,
            "raw": result.get("raw"),
        },
        code="mcp.tool_called",
        meta={"raw_json": json.dumps(result.get("raw"), ensure_ascii=False, default=str)},
    )
