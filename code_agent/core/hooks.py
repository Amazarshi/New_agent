import json

from core.audit import audit_event, shorten
from core.result import is_result, now_text
from core.runtime import LOG_DIR
from core.safety import check_tool_permission


def before_tool_use(tool_name, args):
    """工具执行前统一做权限检查，并记录审计事件。"""
    audit_event("tool.before", tool_name=tool_name, args=shorten(args))
    allowed, message = check_tool_permission(tool_name, args)

    if not allowed:
        audit_event("tool.denied", tool_name=tool_name, args=shorten(args), reason=message)
        return False, message

    return True, "允许执行"


def after_tool_use(tool_name, args, result):
    """工具执行后记录普通日志和审计日志。"""
    result_text = json.dumps(result, ensure_ascii=False, default=str) if is_result(result) else str(result)

    if len(result_text) > 500:
        result_text = result_text[:500] + "...[内容过长，已截断]"

    log_item = {
        "time": now_text(),
        "tool_name": tool_name,
        "args": args,
        "result": result_text,
    }

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOG_DIR / "tool_calls.jsonl"
        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(log_item, ensure_ascii=False, default=str) + "\n")
    except OSError:
        # 普通工具日志失败不能影响工具主流程。
        pass

    audit_event(
        "tool.after",
        tool_name=tool_name,
        args=shorten(args),
        result=shorten(result),
    )
