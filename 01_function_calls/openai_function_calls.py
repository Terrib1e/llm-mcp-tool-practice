"""
OpenAI Function Calling Example

This module demonstrates how to use function calling with OpenAI's GPT models.
Shows real integration with the OpenAI API and proper response handling.
"""

import json
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
from basic_function_calling import create_tool_registry, ToolRegistry


class OpenAIFunctionCaller:
    """Wrapper for OpenAI function calling functionality"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.tool_registry = create_tool_registry()
        self.conversation_history = []

    def get_tools_for_openai(self) -> List[Dict[str, Any]]:
        """Get tools in OpenAI format"""
        return self.tool_registry.get_tool_schemas()

    def execute_function_call(self, function_call) -> Dict[str, Any]:
        """Execute a function call from OpenAI and return the result"""
        function_name = function_call.name
        arguments = json.loads(function_call.arguments)

        print(f"🔧 Executing function: {function_name}")
        print(f"📝 Arguments: {arguments}")

        result = self.tool_registry.execute_tool(function_name, arguments)

        if result.success:
            print(f"✅ Function result: {result.result}")
            return {"success": True, "result": result.result}
        else:
            print(f"❌ Function error: {result.error}")
            return {"success": False, "error": result.error}

    def chat_with_functions(self, user_message: str, model: str = "gpt-3.5-turbo") -> str:
        """
        Send a message to OpenAI with function calling enabled
        """
        # Add user message to conversation
        self.conversation_history.append({"role": "user", "content": user_message})

        try:
            # Make the API call with tools
            response = self.client.chat.completions.create(
                model=model,
                messages=self.conversation_history,
                tools=self.get_tools_for_openai(),
                tool_choice="auto"  # Let the model decide when to use tools
            )

            message = response.choices[0].message

            # Check if the model wants to call functions
            if message.tool_calls:
                # Add the assistant's message to conversation
                self.conversation_history.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        }
                        for tool_call in message.tool_calls
                    ]
                })

                # Execute each function call
                for tool_call in message.tool_calls:
                    function_result = self.execute_function_call(tool_call.function)

                    # Add function result to conversation
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(function_result)
                    })

                # Get the final response after function execution
                final_response = self.client.chat.completions.create(
                    model=model,
                    messages=self.conversation_history
                )

                final_message = final_response.choices[0].message.content
                self.conversation_history.append({"role": "assistant", "content": final_message})

                return final_message

            else:
                # No function calls needed, just return the response
                self.conversation_history.append({"role": "assistant", "content": message.content})
                return message.content

        except Exception as e:
            error_msg = f"Error calling OpenAI API: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []


def demonstrate_openai_function_calling():
    """Demonstrate function calling with OpenAI"""
    print("🤖 OpenAI Function Calling Demonstration\n")

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set!")
        print("Set your API key to run this example:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        print("\nFor now, showing the structure without actual API calls...\n")

        # Show what the conversation would look like
        caller = OpenAIFunctionCaller()
        tools = caller.get_tools_for_openai()

        print("Available tools for OpenAI:")
        for tool in tools:
            func_info = tool["function"]
            print(f"  - {func_info['name']}: {func_info['description']}")

        print("\nExample conversation structure:")
        print("User: 'What's the weather like in Tokyo?'")
        print("Assistant: [calls get_weather function]")
        print("Function result: {...}")
        print("Assistant: 'The weather in Tokyo is...'")

        return

    # Real demonstration with API
    caller = OpenAIFunctionCaller()

    # Example conversations
    test_queries = [
        "What's the weather like in New York?",
        "How old would someone born in 1995 be?",
        "Search the articles table for content about machine learning, limit to 5 results",
        "What's the weather in Paris in Fahrenheit and also calculate the age of someone born in 1988?"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Example {i}: {query}")
        print('='*60)

        response = caller.chat_with_functions(query)
        print(f"\n🤖 Assistant: {response}")

        # Reset for next example
        caller.reset_conversation()


if __name__ == "__main__":
    demonstrate_openai_function_calling()
