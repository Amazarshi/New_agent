SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "ask_subagent",
            "description": "Ask a subagent to read a file and complete a small task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path for the subagent to read.",
                    },
                    "task": {
                        "type": "string",
                        "description": "Task for the subagent.",
                    },
                },
                "required": ["path", "task"],
            },
        },
    }
]
