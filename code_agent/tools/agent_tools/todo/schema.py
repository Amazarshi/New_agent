SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "todo_write",
            "description": "Write 2-4 todos for the current task. Required before file edits.",
            "parameters": {
                "type": "object",
                "properties": {
                    "todos": {
                        "type": "array",
                        "description": "Todo list. Must contain 2-4 items.",
                        "minItems": 2,
                        "maxItems": 4,
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "Todo content.",
                                },
                                "status": {
                                    "type": "string",
                                    "description": "Todo status.",
                                    "enum": ["pending", "in_progress", "completed"],
                                },
                            },
                            "required": ["content", "status"],
                        },
                    }
                },
                "required": ["todos"],
            },
        },
    }
]
