SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "load_skill",
            "description": "Load skill content by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Skill name.",
                        "enum": ["python", "git", "project_rules"],
                    }
                },
                "required": ["name"],
            },
        },
    }
]
