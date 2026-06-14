SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "create_task_workspace",
            "description": "Create an isolated workspace directory for one task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "pattern": "^task-[0-9]{3}$",
                        "description": "Task id, for example task-001.",
                    },
                },
                "required": ["task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_workspace_file",
            "description": "Write a file inside one task's isolated workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "pattern": "^task-[0-9]{3}$",
                        "description": "Task id, for example task-001.",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "File path relative to the task workspace.",
                    },
                    "content": {
                        "type": "string",
                        "description": "File content.",
                    },
                },
                "required": ["task_id", "relative_path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_workspace_file",
            "description": "Read a file inside one task's isolated workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "pattern": "^task-[0-9]{3}$",
                        "description": "Task id, for example task-001.",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "File path relative to the task workspace.",
                    },
                },
                "required": ["task_id", "relative_path"],
            },
        },
    },
]
