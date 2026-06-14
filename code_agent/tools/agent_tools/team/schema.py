SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "send_team_message",
            "description": "Send a team message with a fixed protocol type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sender": {
                        "type": "string",
                        "enum": ["leader", "coder", "reviewer"],
                        "description": "Sender role.",
                    },
                    "receiver": {
                        "type": "string",
                        "enum": ["leader", "coder", "reviewer"],
                        "description": "Receiver role.",
                    },
                    "message_type": {
                        "type": "string",
                        "enum": [
                            "request_plan",
                            "submit_plan",
                            "approve_plan",
                            "reject_plan",
                            "task_done",
                            "shutdown",
                        ],
                        "description": "Fixed team protocol message type.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Message content.",
                    },
                    "task_id": {
                        "type": "string",
                        "pattern": "^task-[0-9]{3}$",
                        "description": "Related task id, for example task-001.",
                    },
                },
                "required": ["sender", "receiver", "message_type", "content", "task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_team_messages",
            "description": "Read messages for one agent role.",
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
                        "description": "Related task id, for example task-001.",
                    },
                },
                "required": ["role", "task_id"],
            },
        },
    },
]