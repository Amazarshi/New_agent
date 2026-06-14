from tools.agent_tools.file.schema import SCHEMAS
from tools.agent_tools.file.tool import (
    run_edit_file,
    run_glob,
    run_read_file,
    run_write_file,
)


HANDLERS = {
    "read_file": run_read_file,
    "write_file": run_write_file,
    "edit_file": run_edit_file,
    "glob": run_glob,
}
