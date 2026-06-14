from core.runtime import MEMORY_DIR


USER_MEMORY_FILE = MEMORY_DIR / "user.md"
PROJECT_MEMORY_FILE = MEMORY_DIR / "project.md"


def ensure_memory_files():
    """确保长期记忆文件存在。"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    if not USER_MEMORY_FILE.exists():
        USER_MEMORY_FILE.write_text("# User Memory\n\n", encoding="utf-8")

    if not PROJECT_MEMORY_FILE.exists():
        PROJECT_MEMORY_FILE.write_text("# Project Memory\n\n", encoding="utf-8")


def remember(kind, content):
    """把重要信息写入长期记忆。"""
    ensure_memory_files()

    if kind == "user":
        target = USER_MEMORY_FILE
    elif kind == "project":
        target = PROJECT_MEMORY_FILE
    else:
        return "Memory kind must be user or project"

    with target.open("a", encoding="utf-8") as f:
        f.write(f"- {content}\n")

    return f"Saved memory to {target}"


def load_memory():
    """读取用户长期记忆和项目长期记忆。"""
    ensure_memory_files()

    user_memory = USER_MEMORY_FILE.read_text(encoding="utf-8")
    project_memory = PROJECT_MEMORY_FILE.read_text(encoding="utf-8")

    return (
        "User memory:\n"
        + user_memory
        + "\n\nProject memory:\n"
        + project_memory
    )
