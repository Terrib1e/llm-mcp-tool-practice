# Function Calls with LLMs - Basic Examples

This directory contains fundamental examples of function calling with Large Language Models.

## What are Function Calls?

Function calling (also known as tool calling) allows LLMs to interact with external systems by calling predefined functions. Instead of just generating text, the LLM can:

- Call APIs
- Query databases
- Perform calculations
- Access file systems
- Execute custom business logic

## Examples in this directory:

1. `basic_function_calling.py` - Simple function definitions and calling patterns
2. `openai_function_calls.py` - OpenAI-specific function calling implementation
3. `anthropic_function_calls.py` - Anthropic Claude function calling
4. `function_validation.py` - Input validation and error handling
5. `advanced_patterns.py` - Complex function calling patterns

## Key Concepts:

- **Function Schema**: JSON schema describing the function
- **Function Execution**: How the LLM calls and receives results
- **Error Handling**: Managing failed function calls
- **State Management**: Maintaining context across calls
