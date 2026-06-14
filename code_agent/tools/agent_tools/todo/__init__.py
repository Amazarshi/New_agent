from tools.agent_tools.todo.schema import SCHEMAS
from tools.agent_tools.todo.tool import run_todo_write


HANDLERS = {
    "todo_write": run_todo_write,
}
