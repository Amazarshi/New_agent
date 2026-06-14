from pathlib import Path

from core.runtime import PROJECT_ROOT


DANGEROUS_COMMANDS = [
    "del /s",
    "rd /s",
    "rmdir /s",
    "remove-item -recurse",
    "rm -rf",
    "shutdown",
    "restart-computer",
    "stop-computer",
    "format",
    "diskpart",
]

SYSTEM_DIRS = [
    "c:\\windows",
    "c:\\program files",
    "c:\\program files (x86)",
]

PATH_TOOLS = {
    "read_file": "path",
    "write_file": "path",
    "edit_file": "path",
    "ask_subagent": "path",
}


def check_command_safe(command):
    """检查命令是否包含危险操作。"""
    command_lower = str(command or "").lower()

    for danger in DANGEROUS_COMMANDS:
        if danger in command_lower:
            return False, f"拒绝执行危险命令：{command}"

    return True, "命令安全"


def resolve_project_path(path):
    """把路径限制在项目根目录内，禁止访问项目外和系统目录。"""
    base_dir = PROJECT_ROOT.resolve()
    target = Path(path or "")

    if not target.is_absolute():
        target = base_dir / target

    target = target.resolve()
    target_text = str(target).lower()

    try:
        target.relative_to(base_dir)
    except ValueError:
        return False, f"拒绝访问项目目录外的路径：{target}", None

    for system_dir in SYSTEM_DIRS:
        if target_text.startswith(system_dir):
            return False, f"拒绝访问系统目录：{target}", None

    return True, str(target), target


def check_path_safe(path):
    """只检查路径是否安全，不要求文件一定存在。"""
    allowed, message, _ = resolve_project_path(path)
    return allowed, message


def get_safe_path(path):
    """返回项目内安全绝对路径，不安全时抛出异常。"""
    allowed, message, target = resolve_project_path(path)

    if not allowed:
        raise ValueError(message)

    return target


def check_glob_safe(pattern):
    """glob 只能在项目内查找，禁止绝对路径和 .. 逃逸。"""
    pattern = str(pattern or "*")

    if Path(pattern).is_absolute():
        return False, "glob pattern 不能是绝对路径"

    if ".." in Path(pattern).parts:
        return False, "glob pattern 不能包含 .."

    return True, "glob pattern 安全"


def check_tool_permission(tool_name, args):
    """统一检查工具调用是否允许执行。"""
    if tool_name in ["bash", "start_background_command"]:
        return check_command_safe(args.get("command", ""))

    if tool_name in PATH_TOOLS:
        return check_path_safe(args.get(PATH_TOOLS[tool_name], ""))

    if tool_name == "glob":
        return check_glob_safe(args.get("pattern", "*"))

    return True, "允许执行"
