# Fledge MCP Server for Smithery.ai

This document provides specific information for deploying the Fledge MCP Server on Smithery.ai.

## Deployment Configuration

The `smithery.yaml` file contains the full configuration for deploying this service on Smithery.ai.

### Key Components:

1. **Entry Point**: `fledge_mcp.main:main`
   - The main function in the `fledge_mcp.main` module

2. **WebSocket Protocol**: MCP over WebSockets
   - Port: 8082
   - Timeout: 300 seconds

3. **HTTP Health Check**:
   - Port: 8083
   - Path: `/health`
   - Response: `{"status": "ok", "message": "Fledge MCP Server is running"}`

4. **Environment Variables**:
   - `FLEDGE_API_URL`: URL of the Fledge API (required)
   - `API_KEY`: Optional API key for secure mode
   - `TOOLS_FILE`: Path to the tools JSON file
   - `HTTP_PORT`: Port for the HTTP health check server
   - `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

## Troubleshooting

If the server fails to start, check the following:

1. **Container Logs**: 
   ```
   smithery logs fledge-mcp
   ```

2. **Configuration**: 
   - Ensure `FLEDGE_API_URL` is properly set
   - Ensure the tools file exists at the specified path

3. **Health Check**:
   - Verify the health check is responding on port 8083
   - Ensure both ports (8082 and 8083) are exposed in the Dockerfile

## Manual Testing

To test the MCP server manually:

1. **Health Check**:
   ```
   curl https://your-smithery-instance.smithery.ai/health
   ```

2. **Initialize Method** (using WebSocket client):
   ```json
   {
       "jsonrpc": "2.0",
       "method": "initialize",
       "params": {},
       "id": "1"
   }
   ```

3. **List Tools** (using WebSocket client):
   ```json
   {
       "jsonrpc": "2.0",
       "method": "tools/list",
       "params": {},
       "id": "2"
   }
   ```