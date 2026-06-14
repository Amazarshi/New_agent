import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parents[1]
PACKAGE_DIR = ROOT_DIR / "code_agent"
if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))

from core.client import get_llm_config
from core.prompt import build_system_prompt
from tools.runner import run_tool
from tools.registry import TOOL_HANDLERS


def call_tool(tool_name, args):
    """调用工具并解析统一 JSON 返回。"""
    return json.loads(run_tool(tool_name, json.dumps(args, ensure_ascii=False)))


class ProductionContractTest(unittest.TestCase):
    """生产级基础契约测试，重点验证结构化协议和安全边界。"""

    def assert_tool_shape(self, result):
        """所有工具返回都必须包含这些固定字段。"""
        self.assertIn("ok", result)
        self.assertIn("code", result)
        self.assertIn("message", result)
        self.assertIn("data", result)
        self.assertIn("error", result)
        self.assertIn("time", result)

    def test_unknown_tool_returns_structured_error(self):
        """未知工具必须返回结构化错误，而不是普通字符串。"""
        result = call_tool("not_exists", {})
        self.assert_tool_shape(result)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["category"], "invalid_tool")

    def test_invalid_json_returns_structured_error(self):
        """工具参数 JSON 解析失败时必须返回 invalid_arguments。"""
        result = json.loads(run_tool("bash", "{bad json"))
        self.assert_tool_shape(result)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["category"], "invalid_arguments")

    def test_workspace_escape_is_denied_before_write(self):
        """工作区相对路径不能使用 .. 逃逸任务目录。"""
        result = call_tool(
            "write_workspace_file",
            {
                "task_id": "task-001",
                "relative_path": "../escape.txt",
                "content": "bad",
            },
        )
        self.assert_tool_shape(result)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["category"], "permission_denied")

    def test_prompt_survives_memory_failure(self):
        """长期记忆读取失败不能导致系统提示词构建失败。"""
        with mock.patch("core.prompt.load_memory", side_effect=PermissionError("no access")):
            prompt = build_system_prompt()

        self.assertIn("长期记忆暂不可用", prompt)
        self.assertIn("工具使用规则", prompt)

    def test_llm_config_uses_only_new_env_names(self):
        """模型配置只接受精简后的 LLM_* 变量名。"""
        new_env = {
            "LLM_API_KEY": "test-key",
            "LLM_MODEL": "test-model",
            "LLM_BASE_URL": "https://example.test/v1",
        }
        with mock.patch.dict(os.environ, new_env, clear=True):
            config = get_llm_config()

        self.assertEqual(config["api_key"], "test-key")
        self.assertEqual(config["model"], "test-model")
        self.assertEqual(config["base_url"], "https://example.test/v1")

        old_env = {
            "DASHSCOPE_API_KEY": "old-key",
            "MODEL_ID": "old-model",
            "QWEN_BASE_URL": "https://old.example/v1",
        }
        with mock.patch.dict(os.environ, old_env, clear=True):
            with self.assertRaises(RuntimeError):
                get_llm_config()

    def test_chrome_devtools_mcp_is_configured(self):
        """真实 Chrome DevTools MCP 配置和工具入口必须存在。"""
        config_path = ROOT_DIR / "mcp_servers.json"
        config = json.loads(config_path.read_text(encoding="utf-8"))
        chrome_config = config["mcpServers"]["chrome-devtools"]

        self.assertEqual(chrome_config["command"], "cmd")
        self.assertIn("chrome-devtools-mcp@latest", chrome_config["args"])
        self.assertIn("mcp_list_tools", TOOL_HANDLERS)
        self.assertIn("mcp_call_tool", TOOL_HANDLERS)


if __name__ == "__main__":
    unittest.main()
