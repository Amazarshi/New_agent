SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "start_agent_task_loop",
            "description": "Start a background loop that claims and executes available tasks for one agent role.",
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "enum": ["leader", "coder", "reviewer"],
                        "description": "Agent role.",
                    },
                    "interval_seconds": {
                        "type": "integer",
                        "minimum": 3,
                        "description": "Polling interval in seconds.",
                    },
                },
                "required": ["role"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "stop_agent_task_loop",
            "description": "Stop a running agent task loop.",
            "parameters": {
                "type": "object",
                "properties": {
                    "loop_id": {
                        "type": "string",
                        "pattern": "^loop-[0-9]{3}$",
                        "description": "Loop id, for example loop-001.",
                    },
                },
                "required": ["loop_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_agent_task_loops",
            "description": "List current agent task loops.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]
