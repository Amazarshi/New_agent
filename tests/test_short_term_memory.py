import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT_DIR / "code_agent"
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

from core.agent_executor import run_agent_task
from memory.short_term import create_session_memory


class FakeMessage:
    """模拟 OpenAI 返回的 message，避免测试调用真实模型。"""

    def __init__(self, content):
        self.content = content
        self.tool_calls = None

    def model_dump(self, exclude_none=True):
        return {
            "role": "assistant",
            "content": self.content,
        }


class FakeChoice:
    """模拟 OpenAI choices 里的单个结果。"""

    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeResponse:
    """模拟 OpenAI Chat Completions 响应。"""

    def __init__(self, content):
        self.choices = [FakeChoice(content)]


class ShortTermMemoryTest(unittest.TestCase):
    """验证短期记忆可以在同一次命令行会话内跨轮保留。"""

    def test_session_memory_keeps_previous_turns(self):
        session_messages = create_session_memory()
        captured_messages = []
        responses = [
            FakeResponse("我记住了，项目名是 New_Agent。"),
            FakeResponse("刚才的项目名是 New_Agent。"),
        ]

        def fake_chat(messages, tools=None):
            captured_messages.append(messages)
            return responses.pop(0)

        with tempfile.TemporaryDirectory() as temp_dir:
            episode_file = Path(temp_dir) / "episodes.jsonl"

            with (
                mock.patch("memory.episodic.EPISODIC_MEMORY_FILE", episode_file),
                mock.patch("core.agent_executor.chat", side_effect=fake_chat),
            ):
                first_answer = run_agent_task("这个项目叫 New_Agent", session_messages)
                second_answer = run_agent_task("刚才项目叫什么？", session_messages)

        self.assertIn("New_Agent", first_answer)
        self.assertIn("New_Agent", second_answer)
        self.assertGreaterEqual(len(session_messages), 4)

        second_turn_text = "\n".join(
            str(message.get("content", ""))
            for message in captured_messages[1]
        )
        self.assertIn("这个项目叫 New_Agent", second_turn_text)
        self.assertIn("我记住了，项目名是 New_Agent。", second_turn_text)


if __name__ == "__main__":
    unittest.main()
