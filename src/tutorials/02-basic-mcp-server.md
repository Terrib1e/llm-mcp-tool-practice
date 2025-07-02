# Setting Up Your First MCP Server

## Prerequisites

Make sure you have the following installed:
- Node.js (v18 or later)
- TypeScript
- MCP SDK (already installed in your project)

## Basic MCP Server Structure

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";

// Create server instance
const server = new Server(
  {
    name: "my-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_weather",
        description: "Get current weather for a city",
        inputSchema: {
          type: "object",
          properties: {
            city: {
              type: "string",
              description: "City name",
            },
          },
          required: ["city"],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "get_weather") {
    const city = args.city;

    // Simulate weather API call
    const weather = {
      city,
      temperature: Math.round(Math.random() * 30 + 10),
      condition: ["sunny", "cloudy", "rainy"][Math.floor(Math.random() * 3)],
      humidity: Math.round(Math.random() * 100),
    };

    return {
      content: [
        {
          type: "text",
          text: `Weather in ${city}: ${weather.temperature}°C, ${weather.condition}, ${weather.humidity}% humidity`,
        },
      ],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP Server running on stdio");
}

main().catch(console.error);
```

## Key Points

1. **Server Configuration**: Name, version, and capabilities
2. **Tool Definition**: Schema defines input parameters
3. **Tool Handler**: Implements the actual functionality
4. **Transport**: How the server communicates (stdio, HTTP, etc.)

## Running Your Server

```bash
# Compile TypeScript
npx tsc

# Run the server
node dist/weather-server.js
```

## Next: Integrating with FastAPI
