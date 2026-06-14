import sys
from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parent / "code_agent"
if str(PACKAGE_DIR) not in sys.path:
    # 让根目录 main.py 可以继续使用项目内部的简短导入路径。
    sys.path.insert(0, str(PACKAGE_DIR))

from core.agent_executor import run_agent_task
from core.runtime import ensure_runtime_dirs
from memory.short_term import create_session_memory


def agent_loop(user_input, session_messages):
    """主入口只负责接收用户输入，并打印统一执行器的结果。"""
    print(run_agent_task(user_input, session_messages))


if __name__ == "__main__":
    # 程序启动时，先创建所有运行时目录。
    ensure_runtime_dirs()
    session_messages = create_session_memory()

    while True:
        user_input = input("你：").strip()

        agent_loop(user_input, session_messages)
