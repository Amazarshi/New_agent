SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "mcp_list_tools",
            "description": "List tools exposed by a real MCP server configured in mcp_servers.json.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_name": {
                        "type": "string",
                        "description": "MCP server name, for example chrome-devtools.",
                    }
                },
                "required": ["server_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mcp_call_tool",
            "description": "Call a tool exposed by a real MCP server. Browser MCP tools can navigate pages and inspect browser state.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_name": {
                        "type": "string",
                        "description": "MCP server name, for example chrome-devtools.",
                    },
                    "tool_name": {
                        "type": "string",
                        "description": "MCP tool name returned by mcp_list_tools.",
                    },
                    "arguments": {
                        "type": "object",
                        "description": "Arguments passed to the MCP tool.",
                    },
                },
                "required": ["server_name", "tool_name", "arguments"],
            },
        },
    },
]
