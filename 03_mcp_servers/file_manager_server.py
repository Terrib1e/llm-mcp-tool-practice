"""
File Management MCP Server

A practical MCP server that provides file system operations.
Demonstrates real-world MCP server implementation with:
- File reading/writing
- Directory operations
- File search capabilities
- Security considerations
"""

import asyncio
import os
import json
import glob
from pathlib import Path
from typing import Dict, Any, List, Optional
import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio


class FileManagerMCPServer:
    """MCP Server for file management operations"""

    def __init__(self, allowed_directories: List[str] = None):
        self.server = Server("file-manager-mcp-server")
        self.allowed_directories = allowed_directories or [os.getcwd()]
        self.setup_tools()

    def _is_path_allowed(self, path: str) -> bool:
        """Check if the path is within allowed directories"""
        abs_path = os.path.abspath(path)
        for allowed_dir in self.allowed_directories:
            allowed_abs = os.path.abspath(allowed_dir)
            if abs_path.startswith(allowed_abs):
                return True
        return False

    def setup_tools(self):
        """Register file management tools"""

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available file management tools"""
            return [
                types.Tool(
                    name="read_file",
                    description="Read the contents of a text file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filepath": {
                                "type": "string",
                                "description": "Path to the file to read"
                            }
                        },
                        "required": ["filepath"]
                    }
                ),
                types.Tool(
                    name="write_file",
                    description="Write content to a text file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filepath": {
                                "type": "string",
                                "description": "Path to the file to write"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file"
                            },
                            "mode": {
                                "type": "string",
                                "enum": ["write", "append"],
                                "description": "Write mode: 'write' to overwrite, 'append' to add to end",
                                "default": "write"
                            }
                        },
                        "required": ["filepath", "content"]
                    }
                ),
                types.Tool(
                    name="list_directory",
                    description="List contents of a directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Path to the directory to list"
                            },
                            "include_hidden": {
                                "type": "boolean",
                                "description": "Whether to include hidden files",
                                "default": False
                            }
                        },
                        "required": ["directory"]
                    }
                ),
                types.Tool(
                    name="search_files",
                    description="Search for files matching a pattern",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "description": "Glob pattern to search for (e.g., '*.py', '**/*.txt')"
                            },
                            "directory": {
                                "type": "string",
                                "description": "Directory to search in (defaults to current directory)"
                            }
                        },
                        "required": ["pattern"]
                    }
                ),
                types.Tool(
                    name="get_file_info",
                    description="Get detailed information about a file or directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filepath": {
                                "type": "string",
                                "description": "Path to the file or directory"
                            }
                        },
                        "required": ["filepath"]
                    }
                ),
                types.Tool(
                    name="create_directory",
                    description="Create a new directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Path of the directory to create"
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Create parent directories if they don't exist",
                                "default": True
                            }
                        },
                        "required": ["directory"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(
            name: str, arguments: dict[str, Any] | None
        ) -> list[types.TextContent]:
            """Handle tool execution"""

            if not arguments:
                return [types.TextContent(
                    type="text",
                    text="Error: No arguments provided"
                )]

            try:
                if name == "read_file":
                    return await self._read_file(arguments)
                elif name == "write_file":
                    return await self._write_file(arguments)
                elif name == "list_directory":
                    return await self._list_directory(arguments)
                elif name == "search_files":
                    return await self._search_files(arguments)
                elif name == "get_file_info":
                    return await self._get_file_info(arguments)
                elif name == "create_directory":
                    return await self._create_directory(arguments)
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Error: Unknown tool '{name}'"
                    )]

            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

    async def _read_file(self, args: Dict[str, Any]) -> list[types.TextContent]:
        """Read file content"""
        filepath = args["filepath"]

        if not self._is_path_allowed(filepath):
            return [types.TextContent(
                type="text",
                text=f"Error: Access denied to {filepath}"
            )]

        if not os.path.exists(filepath):
            return [types.TextContent(
                type="text",
                text=f"Error: File not found: {filepath}"
            )]

        if not os.path.isfile(filepath):
            return [types.TextContent(
                type="text",
                text=f"Error: {filepath} is not a file"
            )]

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            return [types.TextContent(
                type="text",
                text=f"Content of {filepath}:\n\n{content}"
            )]

        except UnicodeDecodeError:
            return [types.TextContent(
                type="text",
                text=f"Error: Cannot read {filepath} as text (binary file?)"
            )]

    async def _write_file(self, args: Dict[str, Any]) -> list[types.TextContent]:
        """Write content to file"""
        filepath = args["filepath"]
        content = args["content"]
        mode = args.get("mode", "write")

        if not self._is_path_allowed(filepath):
            return [types.TextContent(
                type="text",
                text=f"Error: Access denied to {filepath}"
            )]

        # Create directory if it doesn't exist
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        write_mode = "a" if mode == "append" else "w"

        with open(filepath, write_mode, encoding='utf-8') as f:
            f.write(content)

        action = "Appended to" if mode == "append" else "Written to"
        return [types.TextContent(
            type="text",
            text=f"{action} {filepath} successfully ({len(content)} characters)"
        )]

    async def _list_directory(self, args: Dict[str, Any]) -> list[types.TextContent]:
        """List directory contents"""
        directory = args["directory"]
        include_hidden = args.get("include_hidden", False)

        if not self._is_path_allowed(directory):
            return [types.TextContent(
                type="text",
                text=f"Error: Access denied to {directory}"
            )]

        if not os.path.exists(directory):
            return [types.TextContent(
                type="text",
                text=f"Error: Directory not found: {directory}"
            )]

        if not os.path.isdir(directory):
            return [types.TextContent(
                type="text",
                text=f"Error: {directory} is not a directory"
            )]

        items = []
        for item in os.listdir(directory):
            if not include_hidden and item.startswith('.'):
                continue

            item_path = os.path.join(directory, item)
            item_type = "DIR" if os.path.isdir(item_path) else "FILE"

            # Get size for files
            size_info = ""
            if os.path.isfile(item_path):
                try:
                    size = os.path.getsize(item_path)
                    if size < 1024:
                        size_info = f" ({size} B)"
                    elif size < 1024*1024:
                        size_info = f" ({size/1024:.1f} KB)"
                    else:
                        size_info = f" ({size/(1024*1024):.1f} MB)"
                except:
                    size_info = " (size unknown)"

            items.append(f"{item_type:4} {item}{size_info}")

        items.sort()
        content = f"Contents of {directory}:\n\n" + "\n".join(items)

        return [types.TextContent(type="text", text=content)]

    async def _search_files(self, args: Dict[str, Any]) -> list[types.TextContent]:
        """Search for files matching pattern"""
        pattern = args["pattern"]
        directory = args.get("directory", ".")

        if not self._is_path_allowed(directory):
            return [types.TextContent(
                type="text",
                text=f"Error: Access denied to {directory}"
            )]

        search_pattern = os.path.join(directory, pattern)
        matches = glob.glob(search_pattern, recursive=True)

        # Filter to only allowed paths
        allowed_matches = [m for m in matches if self._is_path_allowed(m)]

        if not allowed_matches:
            return [types.TextContent(
                type="text",
                text=f"No files found matching pattern: {pattern}"
            )]

        result_lines = [f"Found {len(allowed_matches)} files matching '{pattern}':"]

        for match in sorted(allowed_matches):
            if os.path.isfile(match):
                size = os.path.getsize(match)
                result_lines.append(f"FILE {match} ({size} bytes)")
            else:
                result_lines.append(f"DIR  {match}")

        return [types.TextContent(
            type="text",
            text="\n".join(result_lines)
        )]

    async def _get_file_info(self, args: Dict[str, Any]) -> list[types.TextContent]:
        """Get detailed file information"""
        filepath = args["filepath"]

        if not self._is_path_allowed(filepath):
            return [types.TextContent(
                type="text",
                text=f"Error: Access denied to {filepath}"
            )]

        if not os.path.exists(filepath):
            return [types.TextContent(
                type="text",
                text=f"Error: Path not found: {filepath}"
            )]

        stat = os.stat(filepath)

        info = {
            "path": filepath,
            "absolute_path": os.path.abspath(filepath),
            "type": "directory" if os.path.isdir(filepath) else "file",
            "size_bytes": stat.st_size,
            "modified_time": stat.st_mtime,
            "created_time": stat.st_ctime,
            "permissions": oct(stat.st_mode)[-3:],
            "is_readable": os.access(filepath, os.R_OK),
            "is_writable": os.access(filepath, os.W_OK),
            "is_executable": os.access(filepath, os.X_OK)
        }

        if os.path.isfile(filepath):
            info["extension"] = os.path.splitext(filepath)[1]

        return [types.TextContent(
            type="text",
            text=f"File Information:\n{json.dumps(info, indent=2)}"
        )]

    async def _create_directory(self, args: Dict[str, Any]) -> list[types.TextContent]:
        """Create a directory"""
        directory = args["directory"]
        recursive = args.get("recursive", True)

        if not self._is_path_allowed(directory):
            return [types.TextContent(
                type="text",
                text=f"Error: Access denied to {directory}"
            )]

        if os.path.exists(directory):
            return [types.TextContent(
                type="text",
                text=f"Directory already exists: {directory}"
            )]

        os.makedirs(directory, exist_ok=recursive)

        return [types.TextContent(
            type="text",
            text=f"Created directory: {directory}"
        )]


async def main():
    """Run the file manager MCP server"""

    # Define allowed directories (security measure)
    allowed_dirs = [
        os.getcwd(),  # Current working directory
        os.path.expanduser("~/Documents"),  # User documents
        "/tmp" if os.name != "nt" else os.environ.get("TEMP", "C:\\Temp")  # Temp directory
    ]

    server = FileManagerMCPServer(allowed_dirs)

    print("📁 Starting File Manager MCP Server...")
    print(f"🔒 Allowed directories: {allowed_dirs}")
    print("🔧 Available tools: read_file, write_file, list_directory, search_files, get_file_info, create_directory")
    print("⏹️  Press Ctrl+C to stop the server")

    # Setup resource handlers (empty for this example)
    @server.server.list_resources()
    async def handle_list_resources() -> list[types.Resource]:
        return []

    @server.server.read_resource()
    async def handle_read_resource(uri: str) -> str:
        raise ValueError(f"Resource not found: {uri}")

    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="file-manager-mcp-server",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                )
            )
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 File Manager MCP Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
