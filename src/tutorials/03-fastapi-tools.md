# FastAPI for Function/Tool Calls

## What is FastAPI?

FastAPI is a modern, fast web framework for building APIs with Python. It's excellent for creating tool endpoints that LLMs can call.

## Setting Up FastAPI for Tool Calls

### 1. Installation

```bash
pip install fastapi uvicorn pydantic
```

### 2. Basic FastAPI Tool Server

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn

app = FastAPI(title="AI Tool Server", version="1.0.0")

# Request/Response Models
class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

class ToolResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Tool Definitions
AVAILABLE_TOOLS = {
    "get_weather": {
        "description": "Get weather information for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "units": {"type": "string", "enum": ["metric", "imperial"], "default": "metric"}
            },
            "required": ["city"]
        }
    },
    "calculate": {
        "description": "Perform basic calculations",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["operation", "a", "b"]
        }
    },
    "get_user_info": {
        "description": "Get user information by ID",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "User ID"}
            },
            "required": ["user_id"]
        }
    }
}

@app.get("/")
async def root():
    return {"message": "AI Tool Server is running"}

@app.get("/tools")
async def list_tools():
    """List all available tools with their schemas"""
    return {"tools": AVAILABLE_TOOLS}

@app.post("/execute-tool", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """Execute a tool with given parameters"""

    if request.tool_name not in AVAILABLE_TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found")

    try:
        if request.tool_name == "get_weather":
            result = await get_weather_tool(request.parameters)
        elif request.tool_name == "calculate":
            result = await calculate_tool(request.parameters)
        elif request.tool_name == "get_user_info":
            result = await get_user_info_tool(request.parameters)
        else:
            raise HTTPException(status_code=400, detail="Tool not implemented")

        return ToolResponse(success=True, result=result)

    except Exception as e:
        return ToolResponse(success=False, error=str(e))

# Tool Implementations
async def get_weather_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    city = params["city"]
    units = params.get("units", "metric")

    # Simulate weather API call
    import random
    temp_unit = "°C" if units == "metric" else "°F"
    base_temp = 20 if units == "metric" else 68

    return {
        "city": city,
        "temperature": f"{base_temp + random.randint(-10, 15)}{temp_unit}",
        "condition": random.choice(["sunny", "cloudy", "rainy", "snowy"]),
        "humidity": f"{random.randint(30, 90)}%",
        "units": units
    }

async def calculate_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    operation = params["operation"]
    a = params["a"]
    b = params["b"]

    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else None
    }

    if operation not in operations:
        raise ValueError(f"Unknown operation: {operation}")

    result = operations[operation](a, b)
    if result is None:
        raise ValueError("Division by zero")

    return {
        "operation": operation,
        "operand_a": a,
        "operand_b": b,
        "result": result
    }

async def get_user_info_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    user_id = params["user_id"]

    # Simulate database lookup
    users_db = {
        1: {"name": "Alice Johnson", "email": "alice@example.com", "role": "admin"},
        2: {"name": "Bob Smith", "email": "bob@example.com", "role": "user"},
        3: {"name": "Carol Davis", "email": "carol@example.com", "role": "moderator"}
    }

    if user_id not in users_db:
        raise ValueError(f"User with ID {user_id} not found")

    return {"user_id": user_id, **users_db[user_id]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Using the FastAPI Tool Server

### 1. Running the Server

```bash
python tool_server.py
# or
uvicorn tool_server:app --reload
```

### 2. Testing Tools

```bash
# List available tools
curl http://localhost:8000/tools

# Execute a tool
curl -X POST http://localhost:8000/execute-tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_weather",
    "parameters": {"city": "London", "units": "metric"}
  }'
```

### 3. OpenAPI Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Next: Advanced Patterns and Integration
