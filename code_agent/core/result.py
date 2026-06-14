import json
from datetime import datetime


def now_text():
    """统一生成 ISO 时间，方便日志、审计和工具返回对齐。"""
    return datetime.now().isoformat(timespec="seconds")


def success(message, data=None, code="ok", meta=None):
    """工具成功时统一返回这个结构，方便 Agent 和程序同时读取。"""
    return {
        "ok": True,
        "code": code,
        "message": message,
        "data": data if data is not None else {},
        "error": None,
        "meta": meta if meta is not None else {},
        "time": now_text(),
    }


def failure(code, message, category="execution_error", details=None, retryable=False, meta=None):
    """工具失败时统一返回错误分类，后续可以按 category 决定是否重试。"""
    return {
        "ok": False,
        "code": code,
        "message": message,
        "data": {},
        "error": {
            "category": category,
            "message": message,
            "details": details if details is not None else {},
            "retryable": retryable,
        },
        "meta": meta if meta is not None else {},
        "time": now_text(),
    }


def is_result(value):
    """判断一个值是不是已经是统一返回结构。"""
    return isinstance(value, dict) and "ok" in value and "code" in value and "message" in value


def to_json(value):
    """把统一返回结构转成 JSON 字符串，作为 role=tool 的 content 返回给模型。"""
    return json.dumps(value, ensure_ascii=False, default=str)


def parse_result_text(text):
    """尽量把工具返回文本解析回结构，解析失败就返回 None。"""
    if not isinstance(text, str):
        return None

    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return None

    if is_result(value):
        return value

    return None


def normalize_tool_result(tool_name, value):
    """兼容旧工具的字符串返回，统一包装成结构化结果。"""
    if is_result(value):
        return value

    return success(
        message=str(value),
        data={"text": str(value)},
        code=f"{tool_name}.success",
    )


def message_from_result_text(text):
    """给人看的地方可以从结构化 JSON 里取 message，旧文本则原样返回。"""
    result = parse_result_text(text)

    if result is None:
        return text

    return result.get("message", "")
