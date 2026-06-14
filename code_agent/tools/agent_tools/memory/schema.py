SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "Save an important memory, such as user preference or project rule.",
            "parameters": {
                "type": "object",
                "properties": {
                    "kind": {
                        "type": "string",
                        "description": "Memory kind.",
                        "enum": ["user", "project"],
                    },
                    "content": {
                        "type": "string",
                        "description": "Memory content.",
                    },
                },
                "required": ["kind", "content"],
            },
        },
    }
]
