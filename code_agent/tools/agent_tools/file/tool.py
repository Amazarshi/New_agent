from core.result import failure, success
from core.runtime import PROJECT_ROOT
from core.safety import get_safe_path


def run_read_file(args):
    """读取项目目录内的文件。"""
    try:
        target = get_safe_path(args.get("path", ""))

        if not target.exists():
            return failure(
                code="file.not_found",
                message=f"文件不存在：{target}",
                category="not_found",
                retryable=False,
            )

        if not target.is_file():
            return failure(
                code="file.not_file",
                message=f"不是文件：{target}",
                category="invalid_arguments",
                retryable=False,
            )

        content = target.read_text(encoding="utf-8")
        return success(
            message=content,
            data={"path": str(target), "content": content},
            code="file.read_success",
        )

    except Exception as e:
        return failure(
            code="file.read_failed",
            message=f"读取文件失败：{e}",
            category="filesystem_error",
            retryable=False,
        )


def run_write_file(args):
    """写入项目目录内的文件。"""
    try:
        target = get_safe_path(args.get("path", ""))
        content = args.get("content", "")

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

        return success(
            message=f"写入成功：{target}",
            data={"path": str(target), "bytes": len(str(content).encode("utf-8"))},
            code="file.write_success",
        )

    except Exception as e:
        return failure(
            code="file.write_failed",
            message=f"写入文件失败：{e}",
            category="filesystem_error",
            retryable=False,
        )


def run_edit_file(args):
    """只替换文件中第一次匹配到的文本。"""
    try:
        target = get_safe_path(args.get("path", ""))
        old_text = args.get("old_text", "")
        new_text = args.get("new_text", "")

        if not target.exists():
            return failure(
                code="file.not_found",
                message=f"文件不存在：{target}",
                category="not_found",
                retryable=False,
            )

        content = target.read_text(encoding="utf-8")

        if old_text not in content:
            return failure(
                code="file.text_not_found",
                message=f"没有找到要替换的文本：{old_text}",
                category="not_found",
                retryable=False,
            )

        content = content.replace(old_text, new_text, 1)
        target.write_text(content, encoding="utf-8")

        return success(
            message=f"编辑成功：{target}",
            data={"path": str(target)},
            code="file.edit_success",
        )

    except Exception as e:
        return failure(
            code="file.edit_failed",
            message=f"编辑文件失败：{e}",
            category="filesystem_error",
            retryable=False,
        )


def run_glob(args):
    """在项目目录内按 glob 查找文件。"""
    try:
        pattern = args.get("pattern", "*")
        base_dir = PROJECT_ROOT.resolve()
        results = []

        for item in base_dir.glob(pattern):
            try:
                relative_path = item.resolve().relative_to(base_dir)
            except ValueError:
                continue
            results.append(str(relative_path))

        if not results:
            return success(
                message="没有找到匹配文件",
                data={"files": []},
                code="file.glob_empty",
            )

        return success(
            message="\n".join(results),
            data={"files": results},
            code="file.glob_success",
        )

    except Exception as e:
        return failure(
            code="file.glob_failed",
            message=f"查找文件失败：{e}",
            category="filesystem_error",
            retryable=False,
        )
