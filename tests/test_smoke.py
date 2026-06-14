import json
import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT_DIR / "code_agent"
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

from tools.agent_tools.todo.service import reset_todos
from tools.runner import run_tool


def call_tool(tool_name, args):
    """用和 Agent 一样的入口调用工具，并解析 JSON 返回。"""
    return json.loads(run_tool(tool_name, json.dumps(args, ensure_ascii=False)))


class SmokeTest(unittest.TestCase):
    """最低成本冒烟测试，不调用真实模型 API。"""

    def setUp(self):
        """每个用例开始前清空 todo，避免用例互相影响。"""
        reset_todos()

    def test_read_and_glob_tools_work(self):
        """验证读文件和文件搜索工具能返回结构化成功结果。"""
        glob_result = call_tool("glob", {"pattern": "**/*.py"})
        self.assertTrue(glob_result["ok"])
        self.assertIn("main.py", glob_result["message"])

        main_path = str(ROOT_DIR / "main.py")
        read_result = call_tool("read_file", {"path": main_path})
        self.assertTrue(read_result["ok"])
        self.assertIn("run_agent_task", read_result["message"])

    def test_write_tool_requires_todo_then_writes_file(self):
        """验证写文件前必须有 todo，满足后可以写入明确测试文件。"""
        target = ROOT_DIR / "tests" / ".tmp_smoke_output.txt"

        blocked = call_tool("write_file", {"path": str(target), "content": "blocked"})
        self.assertFalse(blocked["ok"])
        self.assertEqual(blocked["error"]["category"], "policy_violation")

        todo_result = call_tool(
            "todo_write",
            {
                "todos": [
                    {"content": "准备写入测试文件", "status": "completed"},
                    {"content": "写入后验证返回结构", "status": "in_progress"},
                ]
            },
        )
        self.assertTrue(todo_result["ok"])

        write_result = call_tool("write_file", {"path": str(target), "content": "ok"})
        self.assertTrue(write_result["ok"])
        self.assertTrue(target.exists())

        # 只删除本测试创建的明确单个文件，避免留下临时产物。
        target.unlink()

    def test_dangerous_command_is_denied(self):
        """验证危险批量删除命令会被权限系统拒绝。"""
        result = call_tool("bash", {"command": "rm -rf should_not_run"})
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["category"], "permission_denied")


if __name__ == "__main__":
    unittest.main()
