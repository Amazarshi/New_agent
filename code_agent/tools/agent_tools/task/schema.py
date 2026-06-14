SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a task and save it to disk.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title."},
                    "description": {"type": "string", "description": "Task description."},
                    "blocked_by": {
                        "type": "array",
                        "description": "Task ids that block this task.",
                        "items": {
                            "type": "string",
                            "pattern": "^task-[0-9]{3}$",
                        },
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Complete a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "pattern": "^task-[0-9]{3}$",
                        "description": "Task id, for example task-001.",
                    }
                },
                "required": ["task_id"],
            },
        },
    },
]
