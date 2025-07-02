"""
Anthropic Claude Function Calling Example

This demonstrates function calling with Anthropic's Claude models.
Shows how different LLM providers handle function calling.
"""

import json
import os
from typing import Dict, Any, List, Optional
import anthropic
from basic_function_calling import create_tool_registry, ToolRegistry


class AnthropicFunctionCaller:
    """Wrapper for Anthropic function calling functionality"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Anthropic client"""
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.tool_registry = create_tool_registry()
        self.conversation_history = []

    def convert_tools_for_anthropic(self) -> List[Dict[str, Any]]:
        """Convert OpenAI tool format to Anthropic format"""
        openai_tools = self.tool_registry.get_tool_schemas()
        anthropic_tools = []

        for tool in openai_tools:
            func_info = tool["function"]
            anthropic_tool = {
                "name": func_info["name"],
                "description": func_info["description"],
                "input_schema": func_info["parameters"]
            }
            anthropic_tools.append(anthropic_tool)

        return anthropic_tools

    def execute_function_call(self, tool_use_block) -> Dict[str, Any]:
        """Execute a function call from Claude and return the result"""
        function_name = tool_use_block.name
        arguments = tool_use_block.input

        print(f"🔧 Executing function: {function_name}")
        print(f"📝 Arguments: {arguments}")

        result = self.tool_registry.execute_tool(function_name, arguments)

        if result.success:
            print(f"✅ Function result: {result.result}")
            return {"success": True, "result": result.result}
        else:
            print(f"❌ Function error: {result.error}")
            return {"success": False, "error": result.error}

    def chat_with_functions(self, user_message: str, model: str = "claude-3-haiku-20240307") -> str:
        """
        Send a message to Claude with function calling enabled
        """
        try:
            # Prepare messages for Claude
            messages = [{"role": "user", "content": user_message}]

            # Make the API call with tools
            response = self.client.messages.create(
                model=model,
                max_tokens=1000,
                tools=self.convert_tools_for_anthropic(),
                messages=messages
            )

            # Process the response
            response_text = ""
            tool_results = []

            for content_block in response.content:
                if content_block.type == "text":
                    response_text += content_block.text
                elif content_block.type == "tool_use":
                    # Execute the tool
                    function_result = self.execute_function_call(content_block)
                    tool_results.append({
                        "tool_use_id": content_block.id,
                        "result": function_result
                    })

            # If tools were used, get the final response
            if tool_results:
                # Create follow-up messages with tool results
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Add tool results
                tool_result_content = []
                for tool_result in tool_results:
                    tool_result_content.append({
                        "type": "tool_result",
                        "tool_use_id": tool_result["tool_use_id"],
                        "content": json.dumps(tool_result["result"])
                    })

                messages.append({
                    "role": "user",
                    "content": tool_result_content
                })

                # Get final response after tool execution
                final_response = self.client.messages.create(
                    model=model,
                    max_tokens=1000,
                    messages=messages
                )

                final_text = ""
                for content_block in final_response.content:
                    if content_block.type == "text":
                        final_text += content_block.text

                return final_text

            return response_text

        except Exception as e:
            error_msg = f"Error calling Anthropic API: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg


def demonstrate_anthropic_function_calling():
    """Demonstrate function calling with Anthropic Claude"""
    print("🤖 Anthropic Claude Function Calling Demonstration\n")

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY environment variable not set!")
        print("Set your API key to run this example:")
        print("export ANTHROPIC_API_KEY='your-api-key-here'")
        print("\nFor now, showing the structure without actual API calls...\n")

        # Show what the conversation would look like
        caller = AnthropicFunctionCaller()
        tools = caller.convert_tools_for_anthropic()

        print("Available tools for Anthropic:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")

        print("\nExample conversation structure:")
        print("User: 'Calculate 25 + 17 and tell me the weather in Paris'")
        print("Claude: [calls calculate and get_weather functions]")
        print("Function results: {...}")
        print("Claude: 'The sum of 25 + 17 is 42, and the weather in Paris is...'")

        return

    # Real demonstration with API
    caller = AnthropicFunctionCaller()

    # Example conversations
    test_queries = [
        "Calculate 15 multiplied by 8",
        "What's the weather like in Tokyo in Fahrenheit?",
        "Search for Python tutorials in the articles database, limit to 3 results",
        "Calculate the age of someone born in 1992 and also get the weather in London"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Example {i}: {query}")
        print('='*60)

        response = caller.chat_with_functions(query)
        print(f"\n🤖 Claude: {response}")


def compare_function_calling_formats():
    """Compare OpenAI and Anthropic function calling formats"""
    print("🔍 Comparing Function Calling Formats\n")

    registry = create_tool_registry()

    # Get tools in both formats
    openai_tools = registry.get_tool_schemas()
    caller = AnthropicFunctionCaller()
    anthropic_tools = caller.convert_tools_for_anthropic()

    print("OpenAI Format (first tool):")
    print(json.dumps(openai_tools[0], indent=2))

    print("\n" + "-"*50)

    print("Anthropic Format (same tool):")
    print(json.dumps(anthropic_tools[0], indent=2))

    print("\n📝 Key Differences:")
    print("- OpenAI uses 'function' wrapper with 'parameters'")
    print("- Anthropic uses direct 'input_schema'")
    print("- Both support JSON Schema for parameter definition")
    print("- Tool execution flow is similar but message format differs")


if __name__ == "__main__":
    print("Choose what to run:")
    print("1. Anthropic function calling demo")
    print("2. Compare formats")
    print("3. Both")

    choice = input("\nEnter your choice (1-3): ").strip()

    if choice in ["1", "3"]:
        demonstrate_anthropic_function_calling()

    if choice in ["2", "3"]:
        print("\n" + "="*60)
        compare_function_calling_formats()
