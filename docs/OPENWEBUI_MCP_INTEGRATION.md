# Open WebUI MCP Integration

This guide explains how to integrate all Claude MCP servers into Open WebUI using **mcpo** (MCP-to-OpenAPI proxy).

## Problem

Open WebUI only supports "Streamable HTTP" MCP servers, but all Claude MCP servers use **stdio transport**. The mcpo proxy translates stdio MCP servers into HTTP/OpenAPI endpoints that Open WebUI can consume.

## Solution Overview

**mcpo** is a proxy server that:
- Takes stdio MCP server commands
- Makes them accessible via standard RESTful OpenAPI
- Auto-generates interactive docs for every tool
- Adds HTTP-based security and stability

## Installation

mcpo is installed via `uv`:

```bash
# Test installation
uvx mcpo --help
```

## Configuration

All MCP servers are configured in `src/configs/mcpo.json`. This file mirrors your Claude configuration from `~/.claude.json` and includes:

- google-calendar
- google-maps
- spotify
- spoonacular
- openweathermap
- mobile-mcp
- terrarium (custom server)
- arxiv
- github
- tavily

## Running mcpo

### Manual Start (for testing)

```bash
uvx mcpo --port 8765 --api-key "terrarium-mcp-bridge" --config src/configs/mcpo.json --hot-reload
```

This will:
1. Start the proxy server on port 8765
2. Load all 10 MCP servers from the config
3. Enable hot-reload for configuration changes
4. Expose each server at its own API endpoint

### Verify It's Working

Check the main docs page:
```bash
curl http://localhost:8765/docs
```

View available servers:
```bash
curl http://localhost:8765/openapi.json | python3 -m json.tool
```

Each server has its own documentation:
- http://localhost:8765/google-calendar/docs
- http://localhost:8765/spotify/docs
- http://localhost:8765/openweathermap/docs
- etc.

### Test a Tool

Example - Get current time from Google Calendar:
```bash
curl -X POST http://localhost:8765/google-calendar/get-current-time \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer terrarium-mcp-bridge" \
  -d '{}'
```

Example - Get weather:
```bash
curl -X POST http://localhost:8765/openweathermap/get-current-weather \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer terrarium-mcp-bridge" \
  -d '{"location": "Toronto"}'
```

## Open WebUI Integration

### Step 1: Ensure mcpo is Running

Make sure mcpo is running before configuring Open WebUI:
```bash
uvx mcpo --port 8765 --api-key "terrarium-mcp-bridge" --config src/configs/mcpo.json --hot-reload
```

### Step 2: Add MCP Servers to Open WebUI

1. Open Open WebUI and navigate to **⚙️ Admin Settings → External Tools**
2. Click the **add button** to create a new server
3. Select **MCP (Streamable HTTP)** as the integration type

For **each MCP server**, add it separately:

#### Google Calendar
- **Server URL**: `http://localhost:8765/google-calendar`
- **Authentication**: Bearer Token
- **API Key**: `terrarium-mcp-bridge`

#### Google Maps
- **Server URL**: `http://localhost:8765/google-maps`
- **Authentication**: Bearer Token
- **API Key**: `terrarium-mcp-bridge`

#### Spotify
- **Server URL**: `http://localhost:8765/spotify`
- **Authentication**: Bearer Token
- **API Key**: `terrarium-mcp-bridge`

#### Spoonacular
- **Server URL**: `http://localhost:8765/spoonacular`
- **Authentication**: Bearer Token
- **API Key**: `terrarium-mcp-bridge`

#### OpenWeatherMap
- **Server URL**: `http://localhost:8765/openweathermap`
- **Authentication**: Bearer Token
- **API Key**: `terrarium-mcp-bridge`

#### Mobile MCP
- **Server URL**: `http://localhost:8765/mobile-mcp`
- **Authentication**: Bearer Token
- **API Key**: `terrarium-mcp-bridge`

#### Terrarium (Custom)
- **Server URL**: `http://localhost:8765/terrarium`
- **Authentication**: Bearer Token
- **API Key**: `terrarium-mcp-bridge`

#### arXiv
- **Server URL**: `http://localhost:8765/arxiv`
- **Authentication**: Bearer Token
- **API Key**: `terrarium-mcp-bridge`

#### GitHub
- **Server URL**: `http://localhost:8765/github`
- **Authentication**: Bearer Token
- **API Key**: `terrarium-mcp-bridge`

#### Tavily
- **Server URL**: `http://localhost:8765/tavily`
- **Authentication**: Bearer Token
- **API Key**: `terrarium-mcp-bridge`

### Step 3: Save and Test

1. Save each server configuration
2. Restart Open WebUI if prompted
3. Test the tools in a conversation

## Security Notes

- The API key `terrarium-mcp-bridge` is used for local authentication
- For production use, consider using a stronger API key
- mcpo runs on localhost by default (0.0.0.0:8765)
- To restrict access, use `--host 127.0.0.1` when starting mcpo

## Troubleshooting

### MCP Server Not Connecting

Check mcpo logs:
```bash
# If running in background, check the output
# Or restart mcpo with verbose logging
uvx mcpo --log-level DEBUG --config src/configs/mcpo.json
```

### Tool Not Working in Open WebUI

1. Verify mcpo is running: `curl http://localhost:8765/openapi.json`
2. Test the tool directly with curl (see examples above)
3. Check Open WebUI logs for authentication errors
4. Verify the Bearer token is set correctly

### Port Already in Use

Change the port:
```bash
uvx mcpo --port 8766 --api-key "terrarium-mcp-bridge" --config src/configs/mcpo.json
```

Then update Open WebUI server URLs to use port 8766.

## Resources

- mcpo GitHub: https://github.com/open-webui/mcpo
- Open WebUI MCP Documentation: https://docs.openwebui.com/features/mcp/
- Claude MCP Servers: ~/.claude.json

## Next Steps

Once confirmed working:
1. Add mcpo as a service in the `dev` script as "bridge"
2. Document in README.md
3. Consider setting up mcpo as a systemd service for automatic startup
