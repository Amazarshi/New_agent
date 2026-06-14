from core.hooks import after_tool_use, before_tool_use
from core.recovery import format_tool_error, safe_json_loads
from core.result import failure, normalize_tool_result, to_json
from tools.agent_tools.todo.service import has_valid_todos
from tools.registry import TOOL_HANDLERS


def run_tool(tool_name, arguments):
    """统一工具入口，负责解析参数、权限检查、执行工具、结构化返回。"""
    args, error = safe_json_loads(arguments)

    if error:
        return to_json(error)

    try:
        if tool_name in ["write_file", "edit_file"] and not has_valid_todos():
            return to_json(
                failure(
                    code="todo.required",
                    message="修改文件前请先调用 todo_write，写出 2-4 个 todo。",
                    category="policy_violation",
                    retryable=False,
                )
            )

        allowed, message = before_tool_use(tool_name, args)

        if not allowed:
            return to_json(
                failure(
                    code="permission.denied",
                    message=message,
                    category="permission_denied",
                    retryable=False,
                )
            )

        handler = TOOL_HANDLERS.get(tool_name)

        if handler is None:
            return to_json(
                failure(
                    code="tool.unknown",
                    message=f"Unknown tool: {tool_name}",
                    category="invalid_tool",
                    retryable=False,
                )
            )

        result = normalize_tool_result(tool_name, handler(args))
        after_tool_use(tool_name, args, result)

        return to_json(result)

    except Exception as e:
        return to_json(format_tool_error(e))
