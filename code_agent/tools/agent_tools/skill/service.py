from pathlib import Path


PACKAGE_DIR = Path(__file__).resolve().parents[3]


SKILL_FILES = {
    "python": "python.md",
    "git": "git.md",
    "project_rules": "project_rules.md",
}


def get_skill_list_text():
    return (
        "Available skills:\n"
        "- python: Python code, functions, imports, exceptions, file edits\n"
        "- git: Git status, commits, branches, diff\n"
        "- project_rules: Project development rules and safety requirements\n"
        "Call load_skill when specific skill content is needed."
    )


def load_skill(name):
    if name not in SKILL_FILES:
        available = ", ".join(SKILL_FILES.keys())
        return f"Unknown skill: {name}. Available skills: {available}"

    # main.py 已移动到项目根目录，技能文件固定从 code_agent/skills 读取。
    skill_file = PACKAGE_DIR / "skills" / SKILL_FILES[name]

    if not skill_file.exists():
        return f"Skill file does not exist: {skill_file}"

    return skill_file.read_text(encoding="utf-8")
