from memory.episodic import load_episodic_memory
from memory.long_term import load_memory
from core.runtime import PROJECT_ROOT
from tools.agent_tools.skill.service import get_skill_list_text


def get_agent_identity():
    """返回 Agent 的身份说明。"""
    return "你是一个生产级代码助手 Agent，回答要简洁，执行要谨慎。"


def get_tool_rules():
    """返回精简工具规则，帮助模型节约 token 并遵守流程。"""
    return (
        "1. 修改文件前必须先调用 todo_write，写 2-4 个 todo。\n"
        "2. 工具返回是 JSON：成功看 ok/message/data，失败看 error.category/message/retryable。\n"
        "3. permission_denied、policy_violation 不要重试，应该停止并说明原因。\n"
        "4. timeout、api_error、filesystem_error 可换方案或重试一次。\n"
        "5. 长命令用 start_background_command，不要用 bash 阻塞主对话。\n"
        "6. 定时或稍后执行的需求使用 create_cron_job。\n"
        "7. 任务有 .workspaces/task-xxx 时，产物必须写入对应工作区。\n"
        "8. 长文件和长工具结果只总结关键点，不要原样复述。\n"
        "9. 需要专项知识时再调用 load_skill，不要预先加载全部技能。\n"
    )


def get_safety_rules():
    """返回不可违反的安全边界。"""
    return (
        "禁止批量删除文件或目录。\n"
        "不要使用 del /s、rd /s、rmdir /s、Remove-Item -Recurse、rm -rf。\n"
        "需要删除文件时，只能一次删除一个明确路径的文件。\n"
        "禁止访问当前项目目录外的路径和系统目录。\n"
    )


def get_few_shot_examples():
    """返回关键 Few-shot 示例，帮助模型在高风险场景保持稳定行为。"""
    return (
        "下面示例只用于说明行为模式，不代表当前任务，不要照抄示例路径或内容。\n\n"
        "示例 1：用户要求修改文件\n"
        "用户：帮我修改 README 的启动命令。\n"
        "正确做法：先调用 todo_write 写 2-4 个 todo，再 read_file 理解文件，最后 edit_file 或 write_file。\n"
        "错误做法：没有 todo 就直接调用 edit_file 或 write_file。\n\n"
        "示例 2：工具返回权限拒绝\n"
        "工具返回：{\"ok\": false, \"error\": {\"category\": \"permission_denied\", \"retryable\": false}}\n"
        "正确做法：停止重试，向用户说明被安全策略拦截，并给出安全替代方案。\n"
        "错误做法：换一种命令继续尝试绕过限制。\n\n"
        "示例 3：工具参数格式错误\n"
        "工具返回：{\"ok\": false, \"error\": {\"category\": \"invalid_arguments\", \"retryable\": false}}\n"
        "正确做法：检查工具 schema，重新组织合法 JSON 参数；如果缺少必要信息，先问用户。\n"
        "错误做法：用自然语言或不完整 JSON 继续调用工具。\n"
    )


def get_workdir_text():
    """返回项目根目录。"""
    return f"当前项目目录：{PROJECT_ROOT}"


def safe_load_memory(max_chars=1200):
    """安全加载长期记忆，失败时不影响 Agent 启动，并限制 token 消耗。"""
    try:
        memory = load_memory()
    except Exception as e:
        return f"长期记忆暂不可用：{e}"

    if len(memory) > max_chars:
        return memory[:max_chars] + "\n...[长期记忆过长，已截断]"

    return memory


def safe_load_episodic_memory(max_chars=1200):
    """安全加载情景记忆，失败时不影响 Agent 启动。"""
    try:
        memory = load_episodic_memory(max_chars=max_chars)
    except Exception as e:
        return f"情景记忆暂不可用：{e}"

    if not memory:
        return "暂无情景记忆。"

    return memory


def build_system_prompt():
    """组装完整 system prompt。"""
    return (
        get_agent_identity()
        + "\n\n工具使用规则：\n"
        + get_tool_rules()
        + "\n\n安全规则：\n"
        + get_safety_rules()
        + "\n\nFew-shot 行为示例：\n"
        + get_few_shot_examples()
        + "\n\n技能列表：\n"
        + get_skill_list_text()
        + "\n\n长期记忆：\n"
        + safe_load_memory()
        + "\n\n情景记忆：\n"
        + safe_load_episodic_memory()
        + "\n\n"
        + get_workdir_text()
    )
