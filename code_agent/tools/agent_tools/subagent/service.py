from core.client import chat
from core.safety import get_safe_path


def safe_read_file(path):
    try:
        target = get_safe_path(path)
    except ValueError as e:
        return str(e)

    if not target.exists():
        return f"File does not exist: {target}"

    if not target.is_file():
        return f"Not a file: {target}"

    content = target.read_text(encoding="utf-8")

    if len(content) > 8000:
        content = content[:8000] + "\n\n...[file truncated]"

    return content


def ask_subagent(path, task):
    file_content = safe_read_file(path)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a subagent. Use only the provided file content "
                "to complete the summary task. Do not edit files and do "
                "not call tools. Return a concise answer."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Task: {task}\n\n"
                f"File path: {path}\n\n"
                f"File content:\n{file_content}"
            ),
        },
    ]

    response = chat(messages)
    message = response.choices[0].message

    return message.content
