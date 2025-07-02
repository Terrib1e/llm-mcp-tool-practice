"""
Simple MCP Server Implementation

This is a basic MCP server that demonstrates the core concepts:
- Server initialization
- Tool registration
- Request handling
- Response formatting

Run this server and then connect to it with the MCP client example.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Sequence
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types


class SimpleMCPServer:
    """A simple MCP server with basic tools"""

    def __init__(self):
        self.server = Server("simple-mcp-server")
        self.setup_tools()

    def setup_tools(self):
        """Register tools with the MCP server"""

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="echo",
                    description="Echo back the input message",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to echo back"
                            }
                        },
                        "required": ["message"]
                    }
                ),
                types.Tool(
                    name="calculate",
                    description="Perform basic mathematical calculations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": ["add", "subtract", "multiply", "divide"],
                                "description": "Mathematical operation to perform"
                            },
                            "a": {
                                "type": "number",
                                "description": "First number"
                            },
                            "b": {
                                "type": "number",
                                "description": "Second number"
                            }
                        },
                        "required": ["operation", "a", "b"]
                    }
                ),
                types.Tool(
                    name="get_system_info",
                    description="Get basic system information",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Handle tool execution"""

            if name == "echo":
                message = arguments.get("message", "") if arguments else ""
                return [types.TextContent(
                    type="text",
                    text=f"Echo: {message}"
                )]

            elif name == "calculate":
                if not arguments:
                    return [types.TextContent(
                        type="text",
                        text="Error: No arguments provided"
                    )]

                operation = arguments.get("operation")
                a = arguments.get("a")
                b = arguments.get("b")

                try:
                    if operation == "add":
                        result = a + b
                    elif operation == "subtract":
                        result = a - b
                    elif operation == "multiply":
                        result = a * b
                    elif operation == "divide":
                        if b == 0:
                            return [types.TextContent(
                                type="text",
                                text="Error: Division by zero"
                            )]
                        result = a / b
                    else:
                        return [types.TextContent(
                            type="text",
                            text=f"Error: Unknown operation '{operation}'"
                        )]

                    return [types.TextContent(
                        type="text",
                        text=f"Result: {a} {operation} {b} = {result}"
                    )]

                except Exception as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Error: {str(e)}"
                    )]

            elif name == "get_system_info":
                import platform
                import os

                info = {
                    "platform": platform.platform(),
                    "python_version": platform.python_version(),
                    "architecture": platform.architecture(),
                    "processor": platform.processor(),
                    "current_directory": os.getcwd()
                }

                return [types.TextContent(
                    type="text",
                    text=f"System Information:\n{json.dumps(info, indent=2)}"
                )]

            else:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Unknown tool '{name}'"
                )]


async def main():
    """Run the MCP server"""
    server = SimpleMCPServer()

    # Setup server initialization
    @server.server.list_resources()
    async def handle_list_resources() -> list[types.Resource]:
        """List available resources (none in this simple example)"""
        return []

    @server.server.read_resource()
    async def handle_read_resource(uri: str) -> str:
        """Read a resource (not implemented in this simple example)"""
        raise ValueError(f"Resource not found: {uri}")

    print("🚀 Starting Simple MCP Server...")
    print("📡 Server is ready to receive connections")
    print("🔧 Available tools: echo, calculate, get_system_info")
    print("💡 Connect using the MCP client example")
    print("⏹️  Press Ctrl+C to stop the server")

    # Run the server with stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="simple-mcp-server",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                )
            )
        )


if __name__ == "__main__":
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
