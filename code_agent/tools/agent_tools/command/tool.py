import subprocess

from core.result import failure, success
from core.runtime import PROJECT_ROOT
from core.safety import check_command_safe


def run_bash(args):
    """执行短命令，长命令应该走后台工具。"""
    command = args.get("command", "")
    allowed, message = check_command_safe(command)

    if not allowed:
        return failure(
            code="command.denied",
            message=message,
            category="permission_denied",
            retryable=False,
        )

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        return failure(
            code="command.timeout",
            message="命令执行超时",
            category="timeout",
            retryable=True,
            details={"command": command},
        )
    except Exception as e:
        return failure(
            code="command.error",
            message=f"命令执行异常：{e}",
            category="execution_error",
            retryable=False,
            details={"command": command},
        )

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    data = {
        "command": command,
        "returncode": result.returncode,
        "stdout": stdout,
        "stderr": stderr,
    }

    if result.returncode != 0:
        return failure(
            code="command.non_zero_exit",
            message=f"命令执行失败，退出码：{result.returncode}",
            category="execution_error",
            retryable=False,
            details=data,
        )

    return success(
        message=stdout or "命令执行成功，无输出",
        data=data,
        code="command.success",
    )
