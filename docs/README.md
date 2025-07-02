# Documentation

This directory contains comprehensive documentation for the MCP Servers and Function Calling learning project.

## Documentation Contents

### API References
- `function_calling_api.md` - Complete API reference for function calling patterns
- `mcp_protocol_reference.md` - MCP protocol specification and examples
- `tool_schemas.md` - JSON schema patterns for tool definitions

### Guides and Tutorials
- `getting_started.md` - Detailed getting started guide
- `best_practices.md` - Best practices for MCP development
- `troubleshooting.md` - Common issues and solutions
- `deployment_guide.md` - How to deploy MCP servers in production

### Architecture Documentation
- `architecture_overview.md` - High-level architecture concepts
- `security_model.md` - Security considerations and implementations
- `performance_optimization.md` - Performance tuning guidelines

### Examples and Patterns
- `design_patterns.md` - Common design patterns for MCP servers
- `integration_examples.md` - How to integrate with various systems
- `testing_strategies.md` - Testing approaches for MCP servers

## Quick Reference

### Function Calling Formats

**OpenAI Format:**
```json
{
  "type": "function",
  "function": {
    "name": "tool_name",
    "description": "Tool description",
    "parameters": { ... }
  }
}
```

**Anthropic Format:**
```json
{
  "name": "tool_name",
  "description": "Tool description",
  "input_schema": { ... }
}
```

### MCP Message Types
- **Initialize**: Establish connection
- **List Tools**: Discover available tools
- **Call Tool**: Execute a tool
- **List Resources**: Discover available resources
- **Read Resource**: Access a resource

## Contributing to Documentation

If you find errors or want to improve the documentation:
1. Check existing documentation first
2. Follow the established format and style
3. Include code examples where helpful
4. Test any code snippets you include
5. Submit clear and concise improvements

## Documentation Standards

- Use clear, concise language
- Include practical examples
- Provide both basic and advanced usage
- Link to related documentation
- Keep examples up to date with the latest code
