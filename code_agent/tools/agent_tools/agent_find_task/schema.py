SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "agent_find_task",
            "description": "Let an agent scan tasks, find a pending task it can do, and claim it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "enum": ["leader", "coder", "reviewer"],
                        "description": "Agent role.",
                    },
                },
                "required": ["role"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "agent_execute_claimed_task",
            "description": "Let an agent execute a task it has claimed, then mark it completed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "enum": ["leader", "coder", "reviewer"],
                        "description": "Agent role.",
                    },
                    "task_id": {
                        "type": "string",
                        "pattern": "^task-[0-9]{3}$",
                        "description": "Task id, for example task-001.",
                    },
                },
                "required": ["role", "task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recover_failed_task",
            "description": "Recover a permanently failed task back to pending and reset its retry count.",
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
]
