"""
MCP Client Example

This demonstrates how to connect to an MCP server and use its tools.
Shows the client-side implementation of the MCP protocol.
"""

import asyncio
import json
from typing import Dict, Any, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClientDemo:
    """Demonstration MCP client"""

    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.session = None

    async def connect(self):
        """Connect to the MCP server"""
        print("🔌 Connecting to MCP server...")

        server_params = StdioServerParameters(
            command=self.server_command[0],
            args=self.server_command[1:] if len(self.server_command) > 1 else []
        )

        self.session = await stdio_client(server_params).__aenter__()

        # Initialize the session
        await self.session.initialize()
        print("✅ Connected to MCP server successfully!")

        return self.session

    async def list_available_tools(self):
        """List all tools available on the server"""
        print("\n🔧 Listing available tools...")

        try:
            tools = await self.session.list_tools()

            if not tools.tools:
                print("No tools available on this server")
                return []

            print(f"Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"  📋 {tool.name}: {tool.description}")
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    properties = tool.inputSchema.get('properties', {})
                    if properties:
                        print(f"     Parameters: {', '.join(properties.keys())}")

            return tools.tools

        except Exception as e:
            print(f"❌ Error listing tools: {e}")
            return []

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None):
        """Call a specific tool with arguments"""
        print(f"\n🚀 Calling tool '{tool_name}' with arguments: {arguments}")

        try:
            result = await self.session.call_tool(tool_name, arguments or {})

            print("✅ Tool execution successful!")

            # Display results
            if result.content:
                for i, content in enumerate(result.content):
                    if hasattr(content, 'text'):
                        print(f"📄 Result {i+1}: {content.text}")
                    elif hasattr(content, 'data'):
                        print(f"📊 Result {i+1}: [Binary data, {len(content.data)} bytes]")
                    else:
                        print(f"🔍 Result {i+1}: {content}")
            else:
                print("📭 No content returned")

            return result

        except Exception as e:
            print(f"❌ Error calling tool: {e}")
            return None

    async def run_demo(self):
        """Run a complete demonstration"""
        try:
            # Connect to server
            await self.connect()

            # List available tools
            tools = await self.list_available_tools()

            if not tools:
                print("No tools to demonstrate")
                return

            print("\n" + "="*60)
            print("🎯 Running tool demonstrations...")
            print("="*60)

            # Demonstrate each tool
            for tool in tools:
                await self.demonstrate_tool(tool)

        except Exception as e:
            print(f"❌ Demo error: {e}")

        finally:
            if self.session:
                await self.session.__aexit__(None, None, None)
                print("\n👋 Disconnected from MCP server")

    async def demonstrate_tool(self, tool):
        """Demonstrate a specific tool with example inputs"""
        tool_name = tool.name

        print(f"\n📋 Demonstrating: {tool_name}")
        print("-" * 40)

        # Example arguments for different tools
        example_args = {
            "echo": {"message": "Hello from MCP client!"},
            "calculate": {"operation": "add", "a": 15, "b": 27},
            "get_system_info": {}
        }

        # Use predefined example or empty args
        args = example_args.get(tool_name, {})

        await self.call_tool(tool_name, args)

        # For calculate tool, show multiple operations
        if tool_name == "calculate":
            operations = [
                {"operation": "subtract", "a": 50, "b": 12},
                {"operation": "multiply", "a": 6, "b": 7},
                {"operation": "divide", "a": 84, "b": 4}
            ]

            for op_args in operations:
                await self.call_tool(tool_name, op_args)


async def main():
    """Main demonstration function"""
    print("🤖 MCP Client Demonstration")
    print("="*50)

    # Server command - adjust path as needed
    server_command = ["python", "simple_mcp_server.py"]

    # Create and run client demo
    client = MCPClientDemo(server_command)
    await client.run_demo()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        print("\n💡 Make sure the MCP server is available:")
        print("   python simple_mcp_server.py")
