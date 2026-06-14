import json

from core.result import failure


def safe_json_loads(text):
    """安全解析 JSON，失败时返回结构化错误。"""
    try:
        return json.loads(text or "{}"), None
    except json.JSONDecodeError as e:
        return {}, failure(
            code="json.invalid_arguments",
            message=f"JSON 参数解析失败：{e}",
            category="invalid_arguments",
            details={"raw": text},
            retryable=False,
        )


def format_api_error(error):
    """把 API 错误转换成结构化错误，方便自动重试和审计。"""
    return failure(
        code="api.call_failed",
        message=f"API 调用失败：{error}",
        category="api_error",
        details={"error": str(error)},
        retryable=True,
    )


def format_tool_error(error):
    """把工具异常转换成结构化错误。"""
    return failure(
        code="tool.execution_failed",
        message=f"工具执行失败：{error}",
        category="execution_error",
        details={"error": str(error)},
        retryable=False,
    )
