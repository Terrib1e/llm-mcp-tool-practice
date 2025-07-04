# Complete Guide to MCP Servers and Function Calling with LLM Providers

## Table of Contents
1. [MCP Server Creation Tutorial](#mcp-server-creation-tutorial)
2. [Function Calling with Different LLM Providers](#function-calling-with-different-llm-providers)
3. [Advanced Examples and Best Practices](#advanced-examples-and-best-practices)
4. [Troubleshooting and Common Issues](#troubleshooting-and-common-issues)

---

## MCP Server Creation Tutorial

### What is MCP (Model Context Protocol)?

The Model Context Protocol (MCP) is an open standard introduced by Anthropic in November 2024 that allows AI applications to provide context to Large Language Models (LLMs) in a standardized way. Think of it as a "USB-C port for AI" - it creates a universal interface for connecting LLMs to external data sources and tools.

### Key Benefits of MCP:
- **Standardization**: Eliminates the need for custom integrations
- **Scalability**: One server can serve multiple AI clients
- **Security**: Controlled access to external resources
- **Flexibility**: Supports various data sources and tools

### MCP Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Client     │    │   MCP Server    │    │  External Data  │
│  (Claude, etc.) │◄──►│   (Your Code)   │◄──►│   (APIs, DBs)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Tutorial 1: Setting Up Your Development Environment

#### Prerequisites
- Python 3.10 or higher
- Basic understanding of Python
- Terminal/Command Line access

#### Step 1: Install Required Tools

```bash
# Install uv (recommended Python project manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart your terminal, then create a new project
uv init my-mcp-server
cd my-mcp-server

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install MCP SDK
uv add "mcp[cli]"
```

#### Step 2: Create Your First MCP Server

Create a file called `server.py`:

```python
from mcp import FastMCP
import datetime
import os

# Initialize the MCP server
mcp = FastMCP("My First MCP Server")

@mcp.tool()
def get_current_time() -> str:
    """Get the current date and time"""
    return datetime.datetime.now().isoformat()

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.resource("greeting")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}! Welcome to MCP!"

@mcp.resource("system_info")
def get_system_info() -> dict:
    """Get basic system information"""
    return {
        "python_version": "3.10+",
        "mcp_version": "0.1.0",
        "server_name": "My First MCP Server"
    }

if __name__ == "__main__":
    mcp.run()
```

#### Step 3: Test Your Server

```bash
# Run in development mode
mcp dev server.py

# In another terminal, test with MCP Inspector
mcp inspector
```

### Tutorial 2: Building a Weather MCP Server

Let's create a more practical example - a weather server that integrates with real APIs:

```python
from mcp import FastMCP
import httpx
import json
from typing import Dict, Any

mcp = FastMCP("Weather Server")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> Dict[str, Any] | None:
    """Make a request to the National Weather Service API"""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error making request: {e}")
            return None

def format_alert(feature: Dict) -> str:
    """Format an alert feature into a readable string"""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions')}
"""

@mcp.tool()
async def get_weather_alerts(state: str) -> str:
    """Get weather alerts for a US state (use 2-letter state code like CA, NY)"""
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."
    
    if not data["features"]:
        return "No active alerts for this state."
    
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_weather_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a specific location using coordinates"""
    # First, get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    
    if not points_data:
        return "Unable to fetch forecast data for this location."
    
    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)
    
    if not forecast_data:
        return "Unable to fetch detailed forecast."
    
    # Format the forecast periods
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    
    for period in periods[:5]:  # Show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)
    
    return "\n---\n".join(forecasts)

@mcp.resource("supported_states")
def get_supported_states() -> list:
    """Get list of supported US state codes"""
    return [
        "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
        "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
        "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
        "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
        "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
    ]

if __name__ == "__main__":
    mcp.run()
```

### Tutorial 3: Building a File Management MCP Server

This server demonstrates both resources and tools working together:

```python
from mcp import FastMCP
import os
import tempfile
import json
from pathlib import Path

# Create a temporary directory for demo
temp_dir = tempfile.mkdtemp()
print(f"Using temporary directory: {temp_dir}")

mcp = FastMCP("File Management Server")

@mcp.resource("files_list")
def list_files() -> list:
    """List all files in the managed directory"""
    files = []
    for file_path in Path(temp_dir).glob("*"):
        if file_path.is_file():
            files.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "modified": file_path.stat().st_mtime
            })
    return files

@mcp.tool()
def create_file(filename: str, content: str) -> str:
    """Create a new file with the given content"""
    file_path = Path(temp_dir) / filename
    
    try:
        with open(file_path, "w") as f:
            f.write(content)
        return f"Successfully created file '{filename}'"
    except Exception as e:
        return f"Error creating file: {str(e)}"

@mcp.tool()
def read_file(filename: str) -> str:
    """Read the contents of a file"""
    file_path = Path(temp_dir) / filename
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"File '{filename}' not found"
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def delete_file(filename: str) -> str:
    """Delete a file"""
    file_path = Path(temp_dir) / filename
    
    try:
        file_path.unlink()
        return f"Successfully deleted file '{filename}'"
    except FileNotFoundError:
        return f"File '{filename}' not found"
    except Exception as e:
        return f"Error deleting file: {str(e)}"

@mcp.resource("directory_info")
def get_directory_info() -> dict:
    """Get information about the managed directory"""
    files = list(Path(temp_dir).glob("*"))
    return {
        "directory_path": temp_dir,
        "total_files": len([f for f in files if f.is_file()]),
        "total_size": sum(f.stat().st_size for f in files if f.is_file())
    }

if __name__ == "__main__":
    mcp.run()
```

### Tutorial 4: Integrating with Claude Desktop

#### Step 1: Install Claude Desktop
Download and install Claude Desktop from the official Anthropic website.

#### Step 2: Configure Your MCP Server

Create or edit the Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/your/project", "run", "server.py"]
    }
  }
}
```

#### Step 3: Restart Claude Desktop
After saving the configuration, restart Claude Desktop to load your MCP server.

### Tutorial 5: Building a Database MCP Server

Here's an example that connects to a SQLite database:

```python
from mcp import FastMCP
import sqlite3
import json
from pathlib import Path

mcp = FastMCP("Database Server")

# Initialize database
DB_PATH = "example.db"

def init_database():
    """Initialize the database with sample data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Insert sample data
    users = [
        ("Alice Johnson", "alice@example.com"),
        ("Bob Smith", "bob@example.com"),
        ("Charlie Brown", "charlie@example.com")
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO users (name, email) VALUES (?, ?)", users)
    
    posts = [
        (1, "My First Post", "This is my first blog post!"),
        (2, "Python Tips", "Here are some useful Python tips..."),
        (1, "MCP Tutorial", "Learning about Model Context Protocol")
    ]
    
    cursor.executemany("INSERT OR IGNORE INTO posts (user_id, title, content) VALUES (?, ?, ?)", posts)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_database()

@mcp.tool()
def execute_query(query: str) -> str:
    """Execute a SQL query (SELECT only for safety)"""
    if not query.strip().upper().startswith("SELECT"):
        return "Only SELECT queries are allowed for safety"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        
        # Format results as JSON
        formatted_results = []
        for row in results:
            formatted_results.append(dict(zip(column_names, row)))
        
        return json.dumps(formatted_results, indent=2)
    except Exception as e:
        return f"Error executing query: {str(e)}"

@mcp.tool()
def get_table_schema(table_name: str) -> str:
    """Get the schema for a specific table"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        results = cursor.fetchall()
        conn.close()
        
        schema = []
        for row in results:
            schema.append({
                "column": row[1],
                "type": row[2],
                "nullable": not row[3],
                "default": row[4],
                "primary_key": bool(row[5])
            })
        
        return json.dumps(schema, indent=2)
    except Exception as e:
        return f"Error getting schema: {str(e)}"

@mcp.resource("available_tables")
def get_available_tables() -> list:
    """Get list of available tables in the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    except Exception as e:
        return [f"Error: {str(e)}"]

if __name__ == "__main__":
    mcp.run()
```

---

## Function Calling with Different LLM Providers

### What is Function Calling?

Function calling allows Large Language Models to interact with external functions or APIs. Instead of just generating text, the model can decide when to call specific functions and provide the necessary parameters.

### Key Concepts:
- **Tools**: Functions that the model can call
- **Arguments**: Parameters passed to functions
- **Structured Output**: JSON responses with function calls
- **Execution**: Your code executes the function and returns results

### Tutorial 1: OpenAI Function Calling

#### Basic Setup

```python
import openai
import json
from typing import Dict, Any

# Initialize OpenAI client
client = openai.OpenAI(api_key="your-api-key-here")

# Define a simple function
def get_current_weather(location: str, unit: str = "celsius") -> Dict[str, Any]:
    """Get current weather for a location"""
    # This is a mock function - in reality, you'd call a weather API
    weather_data = {
        "location": location,
        "temperature": 22,
        "unit": unit,
        "condition": "sunny"
    }
    return weather_data

# Define function schema for OpenAI
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    }
]

def chat_with_functions(user_message: str):
    """Chat with OpenAI using function calling"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_message}
    ]
    
    # First API call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    
    # Check if the model wants to call a function
    if response_message.tool_calls:
        messages.append(response_message)
        
        # Process each function call
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "get_current_weather":
                function_response = get_current_weather(**function_args)
                
                # Add function response to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(function_response)
                })
        
        # Second API call to get final response
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )
        
        return final_response.choices[0].message.content
    else:
        return response_message.content

# Example usage
if __name__ == "__main__":
    user_input = "What's the weather like in New York?"
    response = chat_with_functions(user_input)
    print(response)
```

#### Advanced OpenAI Function Calling

```python
import openai
import json
import requests
from datetime import datetime

client = openai.OpenAI(api_key="your-api-key-here")

def search_web(query: str, num_results: int = 5) -> str:
    """Search the web for information"""
    # Mock implementation - replace with actual web search API
    return f"Search results for '{query}': [Mock results would appear here]"

def get_current_time(timezone: str = "UTC") -> str:
    """Get current time in specified timezone"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calculate_math(expression: str) -> str:
    """Calculate a mathematical expression"""
    try:
        # Use eval with caution - in production, use a safer math parser
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

def send_email(to: str, subject: str, body: str) -> str:
    """Send an email (mock implementation)"""
    return f"Email sent to {to} with subject '{subject}'"

# Define all available tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "num_results": {"type": "integer", "description": "Number of results"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get current time",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {"type": "string", "description": "Timezone"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_math",
            "description": "Calculate mathematical expressions",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "body": {"type": "string", "description": "Email body"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    }
]

# Function mapping
available_functions = {
    "search_web": search_web,
    "get_current_time": get_current_time,
    "calculate_math": calculate_math,
    "send_email": send_email
}

def advanced_chat_with_functions(user_message: str):
    """Advanced chat with multiple function support"""
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to various tools."},
        {"role": "user", "content": user_message}
    ]
    
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        if not response_message.tool_calls:
            # No function calls, return the response
            return response_message.content
        
        # Add assistant message to conversation
        messages.append(response_message)
        
        # Process function calls
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name in available_functions:
                function_response = available_functions[function_name](**function_args)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(function_response)
                })
        
        iteration += 1
    
    return "Maximum iterations reached"

# Example usage
if __name__ == "__main__":
    examples = [
        "What time is it?",
        "Calculate 25 * 4 + 10",
        "Search for recent news about AI",
        "Send an email to john@example.com about the meeting tomorrow"
    ]
    
    for example in examples:
        print(f"User: {example}")
        response = advanced_chat_with_functions(example)
        print(f"Assistant: {response}\n")
```

### Tutorial 2: Anthropic Claude Function Calling

```python
import anthropic
import json
from typing import Dict, Any

# Initialize Anthropic client
client = anthropic.Anthropic(api_key="your-api-key-here")

def get_weather(location: str) -> Dict[str, Any]:
    """Get weather information for a location"""
    return {
        "location": location,
        "temperature": 22,
        "condition": "sunny",
        "humidity": 65
    }

def get_news(category: str = "general") -> str:
    """Get latest news for a category"""
    return f"Latest {category} news: [Mock news headlines would appear here]"

def claude_function_calling(user_message: str):
    """Function calling with Claude"""
    
    # Define tools for Claude
    tools = [
        {
            "name": "get_weather",
            "description": "Get weather information for a location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city or location"
                    }
                },
                "required": ["location"]
            }
        },
        {
            "name": "get_news",
            "description": "Get latest news for a category",
            "input_schema": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "News category (e.g., technology, sports, politics)"
                    }
                }
            }
        }
    ]
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        tools=tools,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    
    # Process the response
    for content in response.content:
        if content.type == "tool_use":
            tool_name = content.name
            tool_input = content.input
            
            # Execute the function
            if tool_name == "get_weather":
                result = get_weather(**tool_input)
            elif tool_name == "get_news":
                result = get_news(**tool_input)
            else:
                result = "Unknown function"
            
            # Continue conversation with tool result
            follow_up_response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": json.dumps(result)
                            }
                        ]
                    }
                ]
            )
            
            return follow_up_response.content[0].text
        
        elif content.type == "text":
            return content.text
    
    return "No response generated"

# Example usage
if __name__ == "__main__":
    examples = [
        "What's the weather like in Paris?",
        "Get me the latest technology news",
        "Tell me about the weather in Tokyo"
    ]
    
    for example in examples:
        print(f"User: {example}")
        response = claude_function_calling(example)
        print(f"Claude: {response}\n")
```

### Tutorial 3: Google Gemini Function Calling

```python
import google.generativeai as genai
import json
from typing import Dict, Any

# Configure Gemini
genai.configure(api_key="your-api-key-here")

def get_stock_price(symbol: str) -> Dict[str, Any]:
    """Get stock price for a symbol"""
    return {
        "symbol": symbol,
        "price": 150.25,
        "change": +2.5,
        "change_percent": +1.69
    }

def get_company_info(company_name: str) -> Dict[str, Any]:
    """Get basic company information"""
    return {
        "name": company_name,
        "industry": "Technology",
        "employees": 50000,
        "founded": 1976
    }

def gemini_function_calling(user_message: str):
    """Function calling with Gemini"""
    
    # Define functions for Gemini
    functions = [
        {
            "name": "get_stock_price",
            "description": "Get current stock price for a symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, GOOGL)"
                    }
                },
                "required": ["symbol"]
            }
        },
        {
            "name": "get_company_info",
            "description": "Get basic information about a company",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "Company name"
                    }
                },
                "required": ["company_name"]
            }
        }
    ]
    
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        tools=functions
    )
    
    chat = model.start_chat()
    response = chat.send_message(user_message)
    
    # Check if function calls are needed
    if response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        function_name = function_call.name
        function_args = dict(function_call.args)
        
        # Execute function
        if function_name == "get_stock_price":
            result = get_stock_price(**function_args)
        elif function_name == "get_company_info":
            result = get_company_info(**function_args)
        else:
            result = "Unknown function"
        
        # Send result back to model
        response = chat.send_message(
            genai.protos.Content(
                parts=[
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=function_name,
                            response=result
                        )
                    )
                ]
            )
        )
        
        return response.text
    else:
        return response.text

# Example usage
if __name__ == "__main__":
    examples = [
        "What's the current stock price of Apple?",
        "Tell me about Microsoft as a company",
        "Get me the stock price for GOOGL"
    ]
    
    for example in examples:
        print(f"User: {example}")
        response = gemini_function_calling(example)
        print(f"Gemini: {response}\n")
```

### Tutorial 4: Building a Multi-Provider Function Calling System

```python
import openai
import anthropic
import json
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

class FunctionCallingProvider(ABC):
    """Abstract base class for function calling providers"""
    
    @abstractmethod
    def call_with_functions(self, message: str, functions: List[Dict]) -> str:
        pass

class OpenAIProvider(FunctionCallingProvider):
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def call_with_functions(self, message: str, functions: List[Dict]) -> str:
        tools = [{"type": "function", "function": func} for func in functions]
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message}],
            tools=tools,
            tool_choice="auto"
        )
        
        return response.choices[0].message.content or "No response"

class AnthropicProvider(FunctionCallingProvider):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def call_with_functions(self, message: str, functions: List[Dict]) -> str:
        tools = []
        for func in functions:
            tools.append({
                "name": func["name"],
                "description": func["description"],
                "input_schema": func["parameters"]
            })
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            tools=tools,
            messages=[{"role": "user", "content": message}]
        )
        
        return response.content[0].text if response.content else "No response"

class UniversalFunctionCaller:
    """Universal function calling system supporting multiple providers"""
    
    def __init__(self):
        self.providers = {}
        self.functions = {}
        
    def add_provider(self, name: str, provider: FunctionCallingProvider):
        """Add a new provider"""
        self.providers[name] = provider
    
    def register_function(self, name: str, func: callable, description: str, parameters: Dict):
        """Register a function for use across all providers"""
        self.functions[name] = {
            "function": func,
            "description": description,
            "parameters": parameters
        }
    
    def call(self, provider_name: str, message: str) -> str:
        """Call a provider with the registered functions"""
        if provider_name not in self.providers:
            return f"Provider '{provider_name}' not found"
        
        # Convert registered functions to provider format
        function_definitions = []
        for name, details in self.functions.items():
            function_definitions.append({
                "name": name,
                "description": details["description"],
                "parameters": details["parameters"]
            })
        
        return self.providers[provider_name].call_with_functions(
            message, function_definitions
        )

# Example usage
def get_weather(location: str) -> str:
    """Get weather for a location"""
    return f"Weather in {location}: 22°C, sunny"

def get_time() -> str:
    """Get current time"""
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")

def calculate(expression: str) -> str:
    """Calculate a mathematical expression"""
    try:
        return str(eval(expression))
    except:
        return "Invalid expression"

# Set up universal function caller
ufc = UniversalFunctionCaller()

# Add providers
ufc.add_provider("openai", OpenAIProvider("your-openai-key"))
ufc.add_provider("anthropic", AnthropicProvider("your-anthropic-key"))

# Register functions
ufc.register_function(
    "get_weather",
    get_weather,
    "Get weather information for a location",
    {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "Location name"}
        },
        "required": ["location"]
    }
)

ufc.register_function(
    "get_time",
    get_time,
    "Get current time",
    {"type": "object", "properties": {}}
)

ufc.register_function(
    "calculate",
    calculate,
    "Calculate a mathematical expression",
    {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Math expression"}
        },
        "required": ["expression"]
    }
)

# Example usage
if __name__ == "__main__":
    test_messages = [
        "What's the weather like in London?",
        "What time is it?",
        "Calculate 15 * 7 + 3"
    ]
    
    for message in test_messages:
        print(f"Message: {message}")
        print(f"OpenAI: {ufc.call('openai', message)}")
        print(f"Anthropic: {ufc.call('anthropic', message)}")
        print("-" * 50)
```

---

## Advanced Examples and Best Practices

### Best Practices for MCP Servers

1. **Clear Documentation**: Always provide clear descriptions for your tools and resources
2. **Error Handling**: Implement proper error handling for external API calls
3. **Security**: Validate inputs and implement appropriate access controls
4. **Performance**: Use async operations for I/O-bound tasks
5. **Testing**: Test your servers thoroughly with the MCP Inspector

### Best Practices for Function Calling

1. **Function Descriptions**: Write clear, detailed descriptions for each function
2. **Parameter Validation**: Validate all input parameters before execution
3. **Error Handling**: Gracefully handle errors and provide meaningful feedback
4. **Security**: Never execute arbitrary code; validate and sanitize inputs
5. **Rate Limiting**: Implement rate limiting for expensive operations

### Common Patterns

#### 1. Async Function Calling Pattern
```python
import asyncio
from typing import List, Dict, Any

async def batch_function_calls(functions: List[Dict[str, Any]]) -> List[Any]:
    """Execute multiple function calls concurrently"""
    tasks = []
    
    for func_call in functions:
        if func_call["name"] == "get_weather":
            task = asyncio.create_task(get_weather_async(func_call["args"]["location"]))
        elif func_call["name"] == "get_news":
            task = asyncio.create_task(get_news_async(func_call["args"]["category"]))
        
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

async def get_weather_async(location: str) -> Dict[str, Any]:
    """Async weather function"""
    await asyncio.sleep(1)  # Simulate API call
    return {"location": location, "temperature": 22}

async def get_news_async(category: str) -> str:
    """Async news function"""
    await asyncio.sleep(1)  # Simulate API call
    return f"Latest {category} news"
```

#### 2. Function Call Retry Pattern
```python
import time
from typing import Callable, Any

def retry_function_call(func: Callable, max_retries: int = 3, delay: float = 1.0) -> Any:
    """Retry a function call with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2 ** attempt))
    
    return None
```

#### 3. Function Call Validation Pattern
```python
from typing import Dict, Any
import jsonschema

def validate_function_call(function_name: str, arguments: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate function call arguments against schema"""
    try:
        jsonschema.validate(instance=arguments, schema=schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"Validation error for {function_name}: {e.message}")
        return False
```

---

## Troubleshooting and Common Issues

### MCP Server Issues

#### 1. Server Not Starting
```bash
# Check if uv is installed
uv --version

# Check if MCP is installed
uv pip list | grep mcp

# Run with debug logging
MCP_DEBUG=1 uv run server.py
```

#### 2. Claude Desktop Not Finding Server
- Ensure the absolute path is correct in `claude_desktop_config.json`
- Check that the server runs without errors
- Restart Claude Desktop after configuration changes

#### 3. Permission Errors
```bash
# Fix permissions on Unix systems
chmod +x server.py

# Check file permissions
ls -la server.py
```

### Function Calling Issues

#### 1. Functions Not Being Called
- Check function descriptions are clear and specific
- Verify parameter schemas are correct
- Ensure the model supports function calling

#### 2. Invalid Function Arguments
- Implement parameter validation
- Use required fields appropriately
- Provide clear parameter descriptions

#### 3. Rate Limiting Issues
```python
import time
from functools import wraps

def rate_limit(calls_per_minute: int):
    """Rate limiting decorator"""
    def decorator(func):
        calls = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [call for call in calls if now - call < 60]
            
            if len(calls) >= calls_per_minute:
                raise Exception("Rate limit exceeded")
            
            calls.append(now)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

@rate_limit(calls_per_minute=10)
def expensive_function():
    """Function with rate limiting"""
    pass
```

### Debugging Tips

1. **Use Logging**: Add comprehensive logging to track execution flow
2. **Test Incrementally**: Start with simple functions and gradually add complexity
3. **Validate JSON**: Ensure all JSON schemas are valid
4. **Monitor Performance**: Track function execution times and API usage
5. **Use Mock Data**: Test with mock data before connecting to real APIs

### Additional Resources

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use Documentation](https://docs.anthropic.com/claude/docs/tool-use)
- [Google Gemini Function Calling](https://ai.google.dev/docs/function_calling)

This comprehensive guide should help you get started with both MCP servers and function calling across different LLM providers. Remember to always follow security best practices and validate inputs when working with external APIs and user data.