"""
Production-Ready MCP Server

This example demonstrates a production-grade MCP server with:
- Comprehensive logging
- Error handling and recovery
- Performance monitoring
- Security best practices
- Configuration management
- Health checks
- Graceful shutdown
"""

import asyncio
import logging
import json
import time
import signal
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio


# Configuration
@dataclass
class ServerConfig:
    """Server configuration"""
    name: str = "production-mcp-server"
    version: str = "1.0.0"
    log_level: str = "INFO"
    max_request_size: int = 1024 * 1024  # 1MB
    request_timeout: int = 30  # seconds
    rate_limit_requests: int = 100  # per minute
    enable_metrics: bool = True


# Metrics collection
class MetricsCollector:
    """Collect and track server metrics"""

    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "tools_executed": {},
            "average_response_time": 0.0,
            "uptime_seconds": 0,
            "start_time": time.time()
        }
        self.response_times = []

    def record_request(self, success: bool, response_time: float, tool_name: str = None):
        """Record request metrics"""
        self.metrics["requests_total"] += 1

        if success:
            self.metrics["requests_successful"] += 1
        else:
            self.metrics["requests_failed"] += 1

        if tool_name:
            if tool_name not in self.metrics["tools_executed"]:
                self.metrics["tools_executed"][tool_name] = 0
            self.metrics["tools_executed"][tool_name] += 1

        self.response_times.append(response_time)
        if len(self.response_times) > 1000:  # Keep last 1000 measurements
            self.response_times = self.response_times[-1000:]

        self.metrics["average_response_time"] = sum(self.response_times) / len(self.response_times)
        self.metrics["uptime_seconds"] = time.time() - self.metrics["start_time"]

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()


class ProductionMCPServer:
    """Production-ready MCP server with monitoring and error handling"""

    def __init__(self, config: ServerConfig):
        self.config = config
        self.server = Server(config.name)
        self.metrics = MetricsCollector()
        self.logger = self._setup_logging()
        self.shutdown_event = asyncio.Event()
        self.setup_tools()
        self._setup_signal_handlers()

    def _setup_logging(self) -> logging.Logger:
        """Configure logging"""
        logger = logging.getLogger(self.config.name)
        logger.setLevel(getattr(logging, self.config.log_level))

        # Console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.shutdown_event.set()

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def setup_tools(self):
        """Register production tools with proper error handling"""

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools"""
            self.logger.info("Listing available tools")

            return [
                types.Tool(
                    name="health_check",
                    description="Check server health and status",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False
                    }
                ),
                types.Tool(
                    name="get_metrics",
                    description="Get server performance metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "detailed": {
                                "type": "boolean",
                                "description": "Include detailed metrics",
                                "default": False
                            }
                        }
                    }
                ),
                types.Tool(
                    name="process_data",
                    description="Process data with validation and error handling",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "string",
                                "description": "Data to process"
                            },
                            "operation": {
                                "type": "string",
                                "enum": ["analyze", "transform", "validate"],
                                "description": "Operation to perform"
                            }
                        },
                        "required": ["data", "operation"]
                    }
                ),
                types.Tool(
                    name="system_info",
                    description="Get system information and status",
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
        ) -> list[types.TextContent]:
            """Handle tool execution with comprehensive error handling"""

            start_time = time.time()
            success = False

            try:
                self.logger.info(f"Executing tool: {name} with args: {arguments}")

                # Validate request size
                if arguments and len(str(arguments)) > self.config.max_request_size:
                    raise ValueError("Request size exceeds maximum allowed")

                # Route to appropriate handler
                if name == "health_check":
                    result = await self._health_check(arguments or {})
                elif name == "get_metrics":
                    result = await self._get_metrics(arguments or {})
                elif name == "process_data":
                    result = await self._process_data(arguments or {})
                elif name == "system_info":
                    result = await self._system_info(arguments or {})
                else:
                    raise ValueError(f"Unknown tool: {name}")

                success = True
                self.logger.info(f"Tool {name} executed successfully")
                return result

            except Exception as e:
                self.logger.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
                return [types.TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

            finally:
                response_time = time.time() - start_time
                self.metrics.record_request(success, response_time, name)

    async def _health_check(self, args: Dict[str, Any]) -> list[types.TextContent]:
        """Perform health check"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - self.metrics.metrics["start_time"],
            "version": self.config.version,
            "requests_processed": self.metrics.metrics["requests_total"],
            "success_rate": (
                self.metrics.metrics["requests_successful"] /
                max(1, self.metrics.metrics["requests_total"]) * 100
            )
        }

        return [types.TextContent(
            type="text",
            text=f"Health Check:\n{json.dumps(health_status, indent=2)}"
        )]

    async def _get_metrics(self, args: Dict[str, Any]) -> list[types.TextContent]:
        """Get server metrics"""
        detailed = args.get("detailed", False)
        metrics = self.metrics.get_metrics()

        if not detailed:
            # Return summary metrics only
            summary = {
                "requests_total": metrics["requests_total"],
                "success_rate": (
                    metrics["requests_successful"] /
                    max(1, metrics["requests_total"]) * 100
                ),
                "average_response_time_ms": metrics["average_response_time"] * 1000,
                "uptime_seconds": metrics["uptime_seconds"]
            }
            metrics = summary

        return [types.TextContent(
            type="text",
            text=f"Server Metrics:\n{json.dumps(metrics, indent=2)}"
        )]

    async def _process_data(self, args: Dict[str, Any]) -> list[types.TextContent]:
        """Process data with validation"""
        data = args.get("data", "")
        operation = args.get("operation", "")

        if not data:
            raise ValueError("Data parameter is required")

        if len(data) > 10000:  # Limit data size
            raise ValueError("Data size too large (max 10KB)")

        # Simulate processing based on operation
        if operation == "analyze":
            result = {
                "operation": "analyze",
                "data_length": len(data),
                "word_count": len(data.split()),
                "contains_numbers": any(char.isdigit() for char in data),
                "contains_uppercase": any(char.isupper() for char in data)
            }
        elif operation == "transform":
            result = {
                "operation": "transform",
                "original": data[:100] + "..." if len(data) > 100 else data,
                "transformed": data.upper()[:100] + "..." if len(data) > 100 else data.upper(),
                "length_change": 0
            }
        elif operation == "validate":
            result = {
                "operation": "validate",
                "is_valid": len(data) > 0 and data.strip() != "",
                "validation_errors": [] if data.strip() else ["Empty or whitespace-only data"],
                "data_type": "string",
                "encoding": "utf-8"
            }
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return [types.TextContent(
            type="text",
            text=f"Data Processing Result:\n{json.dumps(result, indent=2)}"
        )]

    async def _system_info(self, args: Dict[str, Any]) -> list[types.TextContent]:
        """Get system information"""
        import platform
        import psutil
        import os

        try:
            system_info = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture(),
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                "disk_usage_gb": round(psutil.disk_usage('/').total / (1024**3), 2) if os.name != 'nt' else "N/A",
                "process_id": os.getpid(),
                "current_directory": os.getcwd()
            }
        except ImportError:
            system_info = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "architecture": platform.architecture(),
                "note": "Install psutil for detailed system metrics"
            }

        return [types.TextContent(
            type="text",
            text=f"System Information:\n{json.dumps(system_info, indent=2)}"
        )]


async def main():
    """Run the production MCP server"""
    config = ServerConfig()
    server = ProductionMCPServer(config)

    server.logger.info(f"Starting {config.name} v{config.version}")
    server.logger.info(f"Configuration: {config}")

    # Setup resource handlers
    @server.server.list_resources()
    async def handle_list_resources() -> list[types.Resource]:
        return []

    @server.server.read_resource()
    async def handle_read_resource(uri: str) -> str:
        raise ValueError(f"Resource not found: {uri}")

    try:
        # Run the server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            server.logger.info("Server started and ready for connections")

            # Create server task
            server_task = asyncio.create_task(
                server.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=config.name,
                        server_version=config.version,
                        capabilities=server.server.get_capabilities(
                            notification_options=None,
                            experimental_capabilities=None,
                        )
                    )
                )
            )

            # Wait for shutdown signal or server completion
            done, pending = await asyncio.wait(
                [server_task, asyncio.create_task(server.shutdown_event.wait())],
                return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            server.logger.info("Server shutdown completed")

    except Exception as e:
        server.logger.error(f"Server error: {e}", exc_info=True)
        raise

    finally:
        # Log final metrics
        final_metrics = server.metrics.get_metrics()
        server.logger.info(f"Final metrics: {final_metrics}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
