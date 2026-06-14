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
from memory.episodic import load_episodic_memory, load_episodes, save_episode


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


class EpisodicMemoryTest(unittest.TestCase):
    """验证情景记忆能保存任务片段，并加载到后续 prompt。"""

    def test_save_and_load_recent_episodic_memory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            episode_file = Path(temp_dir) / "episodes.jsonl"

            with mock.patch("memory.episodic.EPISODIC_MEMORY_FILE", episode_file):
                save_episode("第一个问题", "第一个回答", ["read_file"])
                save_episode("第二个问题", "第二个回答", [])

                episodes = load_episodes()
                memory_text = load_episodic_memory(max_items=1)

        self.assertEqual(len(episodes), 2)
        self.assertIn("第二个问题", memory_text)
        self.assertIn("第二个回答", memory_text)
        self.assertNotIn("第一个问题", memory_text)

    def test_agent_task_saves_episode_after_final_answer(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            episode_file = Path(temp_dir) / "episodes.jsonl"

            with (
                mock.patch("memory.episodic.EPISODIC_MEMORY_FILE", episode_file),
                mock.patch("core.agent_executor.chat", return_value=FakeResponse("回答完成")),
            ):
                answer = run_agent_task("请记住这个任务场景")
                episodes = load_episodes()

        self.assertEqual(answer, "回答完成")
        self.assertEqual(len(episodes), 1)
        self.assertIn("请记住这个任务场景", episodes[0]["user_input"])
        self.assertIn("回答完成", episodes[0]["assistant_output"])


if __name__ == "__main__":
    unittest.main()
