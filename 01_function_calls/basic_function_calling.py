"""
Basic Function Calling Examples

This module demonstrates the fundamental concepts of function calling with LLMs.
Learn how to define functions, create schemas, and handle responses.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class FunctionCallResult:
    """Represents the result of a function call"""

    def __init__(self, success: bool, result: Any = None, error: str = None):
        self.success = success
        self.result = result
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "result": self.result,
            "error": self.error
        }


class ToolRegistry:
    """Registry for managing available functions/tools"""

    def __init__(self):
        self.tools = {}

    def register_tool(self, name: str, func, schema: Dict[str, Any]):
        """Register a tool with its function and schema"""
        self.tools[name] = {
            "function": func,
            "schema": schema
        }

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas for LLM"""
        return [tool["schema"] for tool in self.tools.values()]

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> FunctionCallResult:
        """Execute a tool by name with arguments"""
        if name not in self.tools:
            return FunctionCallResult(False, error=f"Tool '{name}' not found")

        try:
            func = self.tools[name]["function"]
            result = func(**arguments)
            return FunctionCallResult(True, result=result)
        except Exception as e:
            return FunctionCallResult(False, error=str(e))


# Example tool functions
def calculate_age(birth_year: int, current_year: int = 2025) -> int:
    """Calculate a person's age given their birth year"""
    if birth_year > current_year:
        raise ValueError("Birth year cannot be in the future")
    return current_year - birth_year


def get_weather(city: str, units: str = "celsius") -> Dict[str, Any]:
    """Simulate getting weather data for a city"""
    # This is a mock implementation
    mock_weather = {
        "city": city,
        "temperature": 22 if units == "celsius" else 72,
        "units": units,
        "condition": "sunny",
        "humidity": 65
    }
    return mock_weather


def search_database(query: str, table: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Simulate searching a database"""
    # Mock implementation
    return [
        {"id": i, "title": f"Result {i} for '{query}'", "table": table}
        for i in range(1, min(limit + 1, 6))
    ]


# Tool schemas in OpenAI format
TOOL_SCHEMAS = {
    "calculate_age": {
        "type": "function",
        "function": {
            "name": "calculate_age",
            "description": "Calculate a person's age given their birth year",
            "parameters": {
                "type": "object",
                "properties": {
                    "birth_year": {
                        "type": "integer",
                        "description": "The year the person was born"
                    },
                    "current_year": {
                        "type": "integer",
                        "description": "The current year (optional, defaults to 2025)"
                    }
                },
                "required": ["birth_year"]
            }
        }
    },
    "get_weather": {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather information for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature units"
                    }
                },
                "required": ["city"]
            }
        }
    },
    "search_database": {
        "type": "function",
        "function": {
            "name": "search_database",
            "description": "Search for records in a database table",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string"
                    },
                    "table": {
                        "type": "string",
                        "description": "Database table to search"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["query", "table"]
            }
        }
    }
}


def create_tool_registry() -> ToolRegistry:
    """Create and populate a tool registry with example tools"""
    registry = ToolRegistry()

    # Register tools
    registry.register_tool("calculate_age", calculate_age, TOOL_SCHEMAS["calculate_age"])
    registry.register_tool("get_weather", get_weather, TOOL_SCHEMAS["get_weather"])
    registry.register_tool("search_database", search_database, TOOL_SCHEMAS["search_database"])

    return registry


def demonstrate_function_calling():
    """Demonstrate basic function calling concepts"""
    print("🔧 Basic Function Calling Demonstration\n")

    # Create tool registry
    registry = create_tool_registry()

    # Show available tools
    print("Available tools:")
    for name, tool in registry.tools.items():
        desc = tool["schema"]["function"]["description"]
        print(f"  - {name}: {desc}")

    print("\n" + "="*50)

    # Example function calls
    test_calls = [
        ("calculate_age", {"birth_year": 1990}),
        ("get_weather", {"city": "London", "units": "celsius"}),
        ("search_database", {"query": "python tutorials", "table": "articles", "limit": 3}),
        ("calculate_age", {"birth_year": 2030}),  # This should fail
    ]

    for tool_name, arguments in test_calls:
        print(f"\n🚀 Calling {tool_name} with {arguments}")
        result = registry.execute_tool(tool_name, arguments)

        if result.success:
            print(f"✅ Success: {result.result}")
        else:
            print(f"❌ Error: {result.error}")


if __name__ == "__main__":
    demonstrate_function_calling()
