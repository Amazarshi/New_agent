import json

from core.result import now_text
from core.runtime import MEMORY_DIR


EPISODIC_MEMORY_FILE = MEMORY_DIR / "episodes.jsonl"
MAX_FIELD_CHARS = 800
DEFAULT_RECENT_LIMIT = 5


def ensure_episodic_memory_file():
    """确保情景记忆文件存在。"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    EPISODIC_MEMORY_FILE.touch(exist_ok=True)


def shorten_text(text, max_chars=MAX_FIELD_CHARS):
    """截断过长内容，避免情景记忆文件和 prompt 过快膨胀。"""
    text = str(text or "").strip()

    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "\n...[内容过长，已截断]"


def load_episodes():
    """读取所有可解析的情景记忆，损坏行会被跳过。"""
    ensure_episodic_memory_file()
    episodes = []

    with EPISODIC_MEMORY_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                episodes.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return episodes


def save_episode(user_input, assistant_output, tool_names=None, source="agent_turn"):
    """保存一次任务情景，记录用户输入、最终回答和工具使用情况。"""
    ensure_episodic_memory_file()
    episodes = load_episodes()
    episode_id = f"episode-{len(episodes) + 1:06d}"

    episode = {
        "id": episode_id,
        "source": source,
        "created_at": now_text(),
        "user_input": shorten_text(user_input),
        "assistant_output": shorten_text(assistant_output),
        "tool_names": list(dict.fromkeys(tool_names or [])),
    }

    with EPISODIC_MEMORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(episode, ensure_ascii=False) + "\n")

    return episode


def safe_save_episode(user_input, assistant_output, tool_names=None):
    """安全保存情景记忆，失败时不影响 Agent 主流程。"""
    try:
        return save_episode(user_input, assistant_output, tool_names)
    except Exception:
        return None


def list_recent_episodes(limit=DEFAULT_RECENT_LIMIT):
    """返回最近几条情景记忆。"""
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = DEFAULT_RECENT_LIMIT

    if limit <= 0:
        return []

    return load_episodes()[-limit:]


def format_episode(episode):
    """把单条情景记忆格式化成适合放入 prompt 的短文本。"""
    tool_names = episode.get("tool_names") or []
    tool_text = ", ".join(tool_names) if tool_names else "无"

    return (
        f"- {episode.get('id', 'episode')} at {episode.get('created_at', '')}\n"
        f"  用户：{episode.get('user_input', '')}\n"
        f"  回答：{episode.get('assistant_output', '')}\n"
        f"  工具：{tool_text}"
    )


def load_episodic_memory(max_items=DEFAULT_RECENT_LIMIT, max_chars=1200):
    """加载最近情景记忆，供 system prompt 使用。"""
    episodes = list_recent_episodes(max_items)

    if not episodes:
        return ""

    text = "\n".join(format_episode(episode) for episode in episodes)

    if len(text) > max_chars:
        return text[:max_chars] + "\n...[情景记忆过长，已截断]"

    return text
