from tools.agent_tools.workspace.service import (
    create_task_workspace,
    read_workspace_file,
    write_workspace_file,
)


def run_create_task_workspace(args):
    """从参数里取出任务 id，然后创建任务工作区。"""
    return create_task_workspace(args.get("task_id", ""))


def run_write_workspace_file(args):
    """把内容写入指定任务的隔离工作区文件。"""
    return write_workspace_file(
        args.get("task_id", ""),
        args.get("relative_path", ""),
        args.get("content", ""),
    )


def run_read_workspace_file(args):
    """读取指定任务的隔离工作区文件。"""
    return read_workspace_file(
        args.get("task_id", ""),
        args.get("relative_path", ""),
    )
