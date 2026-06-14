SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "create_cron_job",
            "description": "Create a timed job that triggers a prompt after a delay.",
            "parameters": {
                "type": "object",
                "properties": {
                    "delay_seconds": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Delay in seconds, for example 60.",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Prompt to trigger when the time is due.",
                    },
                },
                "required": ["delay_seconds", "prompt"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_cron_jobs",
            "description": "List all timed jobs.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_cron_job",
            "description": "Cancel a timed job.",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "pattern": "^cron-[0-9]{3}$",
                        "description": "Cron job id, for example cron-001.",
                    }
                },
                "required": ["job_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pop_due_cron_prompts",
            "description": "Pop due cron prompts and mark them as triggered.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]
