from core.compact import compact_messages
from core.prompt import build_system_prompt


def create_session_memory():
    """创建会话级短期记忆，程序退出后自然丢失。"""
    return []


def build_turn_messages(user_input, session_messages=None):
    """把 system prompt、短期记忆和本轮用户输入组装成模型 messages。"""
    if session_messages is None:
        session_messages = []

    messages = [
        {
            "role": "system",
            "content": build_system_prompt(),
        },
    ]
    messages.extend(session_messages)
    messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    return compact_messages(messages)


def save_turn_messages(session_messages, messages):
    """保存本轮对话结果到短期记忆，只保留 system prompt 之后的上下文。"""
    if session_messages is None:
        return

    compacted_messages = compact_messages(messages)
    session_messages[:] = compacted_messages[1:]
