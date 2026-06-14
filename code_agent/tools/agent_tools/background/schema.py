SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "start_background_command",
            "description": "Run a slow command in the background and return a job id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Command to run in the background.",
                    }
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_background_jobs",
            "description": "List current background jobs.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pop_background_notifications",
            "description": "Read and clear background job notifications.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]
