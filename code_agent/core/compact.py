MAX_MESSAGES = 20
KEEP_RECENT_MESSAGES = 10
MAX_TOOL_RESULT_CHARS = 1200


def shorten_text(text, max_chars):
    """把太长的文本截短，避免工具结果撑爆上下文"""
    if not isinstance(text, str):
        return text

    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "\n\n...（内容太长，已截断）"


def compact_messages(messages):
    """压缩 messages，保留 system、总结旧消息、保留最近消息"""

    if len(messages) <= MAX_MESSAGES:
        return messages

    system_message = messages[0]
    old_messages = messages[1:-KEEP_RECENT_MESSAGES]
    recent_messages = messages[-KEEP_RECENT_MESSAGES:]

    summary_lines = []

    for msg in old_messages:
        role = msg.get("role", "")
        content = msg.get("content", "")

        if role == "tool":
            content = shorten_text(content, MAX_TOOL_RESULT_CHARS)

        if content:
            summary_lines.append(f"{role}: {content}")

    summary_message = {
        "role": "system",
        "content": (
            "以下是较早对话的压缩总结，只用于保持上下文：\n"
            + shorten_text("\n".join(summary_lines), 3000)
        ),
    }

    return [system_message, summary_message] + recent_messages