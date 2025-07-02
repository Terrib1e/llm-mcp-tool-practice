# Quick Start Guide

Welcome to the MCP Servers and Function Calling with LLMs learning project! This guide will get you up and running quickly.

## 🚀 Quick Setup

1. **Run the setup script:**
   ```bash
   python setup.py
   ```

2. **Activate your virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Start learning!**

## 📚 Learning Path

### Step 1: Basic Function Calling
```bash
cd 01_function_calls
python basic_function_calling.py
```

This will show you:
- How to define functions for LLMs
- Function schemas and parameters
- Error handling
- Tool registries

### Step 2: OpenAI Function Calls (Optional - requires API key)
```bash
python openai_function_calls.py
```

Learn how to:
- Integrate with OpenAI's API
- Handle real function calling with GPT models
- Manage conversation context

### Step 3: MCP Basics
```bash
cd ../02_mcp_basics
python simple_mcp_server.py
```

Open another terminal and run:
```bash
python mcp_client_example.py
```

This demonstrates:
- MCP server-client architecture
- Protocol message handling
- Tool execution over MCP

### Step 4: Advanced MCP Server
```bash
cd ../03_mcp_servers
python file_manager_server.py
```

Explore:
- Real-world MCP server implementation
- Security considerations
- File system operations
- Production-ready patterns

## 🔧 Key Concepts Covered

### Function Calling
- **Tool Definition**: How to describe functions to LLMs
- **Parameter Validation**: Ensuring inputs are correct
- **Error Handling**: Managing failures gracefully
- **Response Formatting**: Structuring outputs for LLMs

### MCP Servers
- **Protocol Implementation**: Understanding MCP message flow
- **Tool Registration**: Making functions available to clients
- **Security**: Protecting against unauthorized access
- **Scalability**: Building production-ready servers

## 💡 Tips for Learning

1. **Start Simple**: Begin with basic_function_calling.py
2. **Read the Code**: Each file is heavily commented
3. **Experiment**: Modify examples to see what happens
4. **Build Gradually**: Each directory builds on the previous
5. **Check Errors**: Error messages provide learning opportunities

## 🔗 API Keys (Optional)

For OpenAI examples:
1. Get an API key from https://platform.openai.com/
2. Copy `.env.template` to `.env`
3. Add your key: `OPENAI_API_KEY=your_key_here`

## 🆘 Troubleshooting

### Common Issues

**Import errors for MCP:**
- The MCP library is still evolving
- Basic examples work without it
- Focus on concepts first, implementation details second

**Python version errors:**
- Requires Python 3.8+
- Use `python --version` to check

**Permission errors:**
- Make sure you're in the project directory
- Check file permissions
- Try running as administrator (Windows) or with sudo (macOS/Linux)

## 📖 Further Reading

- [OpenAI Function Calling Documentation](https://platform.openai.com/docs/guides/function-calling)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/docs)
- [Anthropic Tool Use Guide](https://docs.anthropic.com/claude/docs/tool-use)

## 🎯 Next Steps

After completing this tutorial:
1. Build your own MCP server for your use case
2. Integrate function calling into your applications
3. Explore advanced patterns like tool chaining
4. Consider security and performance optimizations

Happy learning! 🎓
