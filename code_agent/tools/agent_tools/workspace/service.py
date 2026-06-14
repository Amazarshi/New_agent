from pathlib import Path

from core.result import failure, success
from core.runtime import PROJECT_ROOT
from tools.agent_tools.task.service import validate_task_id


WORKSPACE_DIR = PROJECT_ROOT / ".workspaces"


def get_task_workspace(task_id):
    """获取指定任务自己的隔离工作区目录。"""
    if not validate_task_id(task_id):
        return None, "Invalid task id. Expected format: task-001"

    return WORKSPACE_DIR / task_id, ""


def create_task_workspace(task_id):
    """为任务创建独立工作区目录。"""
    workspace, error = get_task_workspace(task_id)

    if error:
        return failure(
            code="workspace.invalid_task_id",
            message=error,
            category="invalid_arguments",
            retryable=False,
        )

    try:
        workspace.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        return failure(
            code="workspace.mkdir_failed",
            message=f"工作区创建失败：{e}",
            category="filesystem_error",
            retryable=True,
        )

    return success(
        message=f"Task workspace ready: {workspace}",
        data={"workspace": str(workspace)},
        code="workspace.ready",
    )


def get_safe_workspace_file(task_id, relative_path):
    """确保目标文件路径不能逃出当前任务工作区。"""
    workspace, error = get_task_workspace(task_id)

    if error:
        return None, error

    if not isinstance(relative_path, str) or not relative_path.strip():
        return None, "relative_path is required"

    relative_target = Path(relative_path)

    if relative_target.is_absolute():
        return None, "relative_path must not be absolute"

    if ".." in relative_target.parts:
        return None, "relative_path must not contain .."

    workspace = workspace.resolve()
    target = (workspace / relative_target).resolve()

    try:
        target.relative_to(workspace)
    except ValueError:
        return None, "File path escapes task workspace"

    return target, ""


def write_workspace_file(task_id, relative_path, content):
    """把文件写入指定任务自己的工作区。"""
    target, error = get_safe_workspace_file(task_id, relative_path)

    if error:
        return failure(
            code="workspace.path_denied",
            message=error,
            category="permission_denied",
            retryable=False,
        )

    create_result = create_task_workspace(task_id)

    if not create_result.get("ok"):
        return create_result

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(content), encoding="utf-8")
    except OSError as e:
        return failure(
            code="workspace.write_failed",
            message=f"工作区文件写入失败：{e}",
            category="filesystem_error",
            retryable=True,
        )

    return success(
        message=f"Workspace file written: {target}",
        data={"path": str(target)},
        code="workspace.file_written",
    )


def read_workspace_file(task_id, relative_path):
    """读取指定任务工作区里的文件。"""
    target, error = get_safe_workspace_file(task_id, relative_path)

    if error:
        return failure(
            code="workspace.path_denied",
            message=error,
            category="permission_denied",
            retryable=False,
        )

    if not target.exists():
        return failure(
            code="workspace.file_not_found",
            message=f"Workspace file does not exist: {target}",
            category="not_found",
            retryable=False,
        )

    if not target.is_file():
        return failure(
            code="workspace.not_file",
            message=f"Not a file: {target}",
            category="invalid_arguments",
            retryable=False,
        )

    content = target.read_text(encoding="utf-8")
    return success(
        message=content,
        data={"path": str(target), "content": content},
        code="workspace.file_read",
    )
