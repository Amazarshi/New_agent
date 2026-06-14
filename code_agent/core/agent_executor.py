from core.client import chat
from core.compact import compact_messages
from core.recovery import format_api_error
from core.result import to_json
from memory.episodic import safe_save_episode
from memory.short_term import build_turn_messages, save_turn_messages
from tools.agent_tools.todo.service import reset_todos


def finish_agent_task(user_input, result, messages, session_messages, tool_names):
    """统一保存短期记忆和情景记忆，然后返回最终结果。"""
    save_turn_messages(session_messages, messages)
    safe_save_episode(user_input, result, tool_names)
    return result


def run_agent_task(user_input, session_messages=None):
    """执行一个完整 Agent 任务，并返回最终回答。"""
    # 延迟导入工具，避免工具注册阶段和任务领取工具形成循环导入。
    from tools import TOOLS, run_tool

    reset_todos()
    messages = build_turn_messages(user_input, session_messages)
    tool_names = []

    while True:
        try:
            response = chat(messages, tools=TOOLS)
        except Exception as e:
            # 第一次 API 失败时，压缩上下文后重试一次。
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "刚才调用模型失败。请减少上下文长度，换一种更简单的方式继续完成任务。\n"
                        + to_json(format_api_error(e))
                    ),
                }
            )
            messages = compact_messages(messages)

            try:
                response = chat(messages, tools=TOOLS)
            except Exception as e:
                result = to_json(format_api_error(e))
                messages.append({"role": "assistant", "content": result})
                return finish_agent_task(user_input, result, messages, session_messages, tool_names)

        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            result = message.content or ""
            return finish_agent_task(user_input, result, messages, session_messages, tool_names)

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_names.append(tool_name)
            arguments = tool_call.function.arguments
            tool_result = run_tool(tool_name, arguments)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                }
            )

            messages = compact_messages(messages)
