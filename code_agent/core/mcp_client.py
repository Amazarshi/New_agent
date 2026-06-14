import asyncio
import json
import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
MCP_CONFIG_FILE = ROOT_DIR / "mcp_servers.json"


def load_mcp_server_config(server_name):
    """读取项目里的 MCP server 配置。"""
    if not MCP_CONFIG_FILE.exists():
        raise FileNotFoundError(f"MCP 配置文件不存在：{MCP_CONFIG_FILE}")

    config = json.loads(MCP_CONFIG_FILE.read_text(encoding="utf-8"))
    servers = config.get("mcpServers", {})

    if server_name not in servers:
        available = ", ".join(sorted(servers.keys())) or "none"
        raise ValueError(f"未知 MCP server：{server_name}，可用 server：{available}")

    server = dict(servers[server_name])
    server["args"] = [
        str(ROOT_DIR / arg) if isinstance(arg, str) and arg.startswith(".runtime/")
        else arg
        for arg in server.get("args", [])
    ]
    return server


def serialize_mcp_value(value):
    """把 MCP SDK 返回对象转换成普通 JSON 数据。"""
    if hasattr(value, "model_dump"):
        return value.model_dump(by_alias=True, exclude_none=True)

    if isinstance(value, list):
        return [serialize_mcp_value(item) for item in value]

    if isinstance(value, dict):
        return {key: serialize_mcp_value(item) for key, item in value.items()}

    return value


def extract_mcp_result_text(result):
    """从 MCP 工具结果里提取给用户看的文本。"""
    texts = []

    for item in getattr(result, "content", []) or []:
        text = getattr(item, "text", None)
        if text:
            texts.append(text)

    if texts:
        return "\n".join(texts)

    structured = getattr(result, "structured_content", None)
    if structured is None:
        structured = getattr(result, "structuredContent", None)

    if structured is not None:
        return json.dumps(serialize_mcp_value(structured), ensure_ascii=False)

    return json.dumps(serialize_mcp_value(result), ensure_ascii=False)


async def run_with_mcp_session(server_name, operation):
    """启动 MCP server，初始化会话，然后执行一次操作。"""
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as e:
        raise RuntimeError(
            "缺少 MCP Python SDK。请先在当前 Python 环境执行：pip install \"mcp[cli]>=1.27,<2\""
        ) from e

    server = load_mcp_server_config(server_name)
    env = os.environ.copy()
    env.update(server.get("env", {}))

    params = StdioServerParameters(
        command=server.get("command", ""),
        args=server.get("args", []),
        env=env,
    )
    timeout_seconds = server.get("startup_timeout_ms", 20000) / 1000

    async def connect_and_run():
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await operation(session)

    return await asyncio.wait_for(connect_and_run(), timeout=timeout_seconds)


def run_async(coro):
    """在当前命令行 Agent 里运行异步 MCP 调用。"""
    return asyncio.run(coro)


def list_mcp_tools(server_name):
    """列出某个真实 MCP server 暴露的工具。"""
    async def operation(session):
        result = await session.list_tools()
        return serialize_mcp_value(result)

    return run_async(run_with_mcp_session(server_name, operation))


def call_mcp_tool(server_name, tool_name, arguments):
    """调用某个真实 MCP 工具。"""
    async def operation(session):
        result = await session.call_tool(tool_name, arguments or {})
        return {
            "is_error": bool(getattr(result, "isError", False)),
            "message": extract_mcp_result_text(result),
            "raw": serialize_mcp_value(result),
        }

    return run_async(run_with_mcp_session(server_name, operation))
