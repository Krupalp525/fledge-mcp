# Fledge MCP Server

This is a Model Context Protocol (MCP) server that connects Fledge functionality to Cursor AI, allowing the AI to interact with Fledge instances via natural language commands.

## Prerequisites

- Fledge installed locally or accessible via API (default: http://localhost:8081)
- Cursor AI installed
- Python 3.8+

## Installation

1. Clone this repository:
```
git clone https://github.com/Krupalp525/fledge-mcp.git
cd fledge-mcp
```

2. Install the dependencies:
```
pip install -r requirements.txt
```

## Running the Server

1. Make sure Fledge is running:
```
fledge start
```

2. Start the MCP server:
```
python mcp_server.py
```

For secure operation with API key authentication:
```
python secure_mcp_server.py
```

3. Verify it's working by accessing the health endpoint:
```
curl http://localhost:8082/health
```
You should receive "Fledge MCP Server is running" as the response.

## Connecting to Cursor

1. In Cursor, go to Settings > MCP Servers
2. Add a new server:
   - URL: http://localhost:8082/tools
   - Tools file: Upload the included tools.json or point to its local path

3. For the secure server, configure the "X-API-Key" header with the value from the api_key.txt file that is generated when the secure server starts.

4. Test it: Open Cursor's Composer (Ctrl+I), type "Check if Fledge API is reachable," and the AI should call the `validate_api_connection` tool.

## Available Tools

### Data Access and Management
1. **get_sensor_data**: Fetch sensor data from Fledge with optional filtering by time range and limit
2. **list_sensors**: List all sensors available in Fledge
3. **ingest_test_data**: Ingest test data into Fledge, with optional batch count

### Service Control
4. **get_service_status**: Get the status of all Fledge services
5. **start_stop_service**: Start or stop a Fledge service by type
6. **update_config**: Update Fledge configuration parameters

### Frontend Code Generation
7. **generate_ui_component**: Generate React components for Fledge data visualization
8. **fetch_sample_frontend**: Get sample frontend templates for different frameworks
9. **suggest_ui_improvements**: Get AI-powered suggestions for improving UI code

### Real-Time Data Streaming
10. **subscribe_to_sensor**: Set up a subscription to sensor data updates
11. **get_latest_reading**: Get the most recent reading from a specific sensor

### Debugging and Validation
12. **validate_api_connection**: Check if the Fledge API is reachable
13. **simulate_frontend_request**: Test API requests with different methods and payloads

### Documentation and Schema
14. **get_api_schema**: Get information about available Fledge API endpoints
15. **list_plugins**: List available Fledge plugins

### Advanced AI-Assisted Features
16. **generate_mock_data**: Generate realistic mock sensor data for testing

## Testing the API

You can test the server using the included test scripts:

```
# For standard server
python test_mcp.py

# For secure server with API key
python test_secure_mcp.py
```

## Security Options

The secure server (secure_mcp_server.py) adds API key authentication:

1. On first run, it generates an API key stored in api_key.txt
2. All requests must include this key in the X-API-Key header
3. Health check endpoint remains accessible without authentication

## Example API Requests

```bash
# Validate API connection
curl -X POST -H "Content-Type: application/json" -d '{"name": "validate_api_connection"}' http://localhost:8082/tools

# Generate mock data
curl -X POST -H "Content-Type: application/json" -d '{"name": "generate_mock_data", "parameters": {"sensor_id": "temp1", "count": 5}}' http://localhost:8082/tools

# Generate React chart component
curl -X POST -H "Content-Type: application/json" -d '{"name": "generate_ui_component", "parameters": {"component_type": "chart", "sensor_id": "temp1"}}' http://localhost:8082/tools

# For secure server, add API key header
curl -X POST -H "Content-Type: application/json" -H "X-API-Key: YOUR_API_KEY" -d '{"name": "list_sensors"}' http://localhost:8082/tools
```

## Extending the Server

To add more tools:
1. Add the tool definition to `tools.json`
2. Implement the tool handler in `mcp_server.py` and `secure_mcp_server.py`

## Production Considerations

For production deployment:
- Use HTTPS
- Deploy behind a reverse proxy like Nginx
- Implement more robust authentication (JWT, OAuth)
- Add rate limiting
- Set up persistent data storage for subscriptions 

## Deploying on Smithery.ai

The Fledge MCP Server can be deployed on Smithery.ai for enhanced scalability and availability. Follow these steps to deploy:

1. **Prerequisites**
   - Docker installed on your local machine
   - A Smithery.ai account
   - The Smithery CLI tool installed

2. **Build and Deploy**
   ```bash
   # Build the Docker image
   docker build -t fledge-mcp .

   # Deploy to Smithery.ai
   smithery deploy
   ```

3. **Configuration**
   The `smithery.json` file contains the configuration for your deployment:
   - WebSocket transport on port 8082
   - Configurable Fledge API URL
   - Tool definitions and parameters
   - Timeout settings

4. **Environment Variables**
   Set the following environment variables in your Smithery.ai dashboard:
   - `FLEDGE_API_URL`: Your Fledge API endpoint
   - `API_KEY`: Your secure API key (if using secure mode)

5. **Verification**
   After deployment, verify your server is running:
   ```bash
   smithery status fledge-mcp
   ```

6. **Monitoring**
   Monitor your deployment through the Smithery.ai dashboard:
   - Real-time logs
   - Performance metrics
   - Error tracking
   - Resource usage

7. **Updating**
   To update your deployment:
   ```bash
   # Build new image
   docker build -t fledge-mcp .
   
   # Deploy updates
   smithery deploy --update
   ```

## JSON-RPC Protocol Support

The server implements the Model Context Protocol (MCP) using JSON-RPC 2.0 over WebSocket. The following methods are supported:

1. **initialize**
   ```json
   {
       "jsonrpc": "2.0",
       "method": "initialize",
       "params": {},
       "id": "1"
   }
   ```
   Response:
   ```json
   {
       "jsonrpc": "2.0",
       "result": {
           "serverInfo": {
               "name": "fledge-mcp",
               "version": "1.0.0",
               "description": "Fledge Model Context Protocol (MCP) Server",
               "vendor": "Fledge",
               "capabilities": {
                   "tools": true,
                   "streaming": true,
                   "authentication": "api_key"
               }
           },
           "configSchema": {
               "type": "object",
               "properties": {
                   "fledge_api_url": {
                       "type": "string",
                       "description": "Fledge API URL",
                       "default": "http://localhost:8081/fledge"
                   }
               }
           }
       },
       "id": "1"
   }
   ```

2. **tools/list**
   ```json
   {
       "jsonrpc": "2.0",
       "method": "tools/list",
       "params": {},
       "id": "2"
   }
   ```
   Response: Returns the list of available tools and their parameters.

3. **tools/call**
   ```json
   {
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
           "name": "get_sensor_data",
           "parameters": {
               "sensor_id": "temp1",
               "limit": 10
           }
       },
       "id": "3"
   }
   ```

### Error Codes

The server follows standard JSON-RPC 2.0 error codes:

- -32700: Parse error
- -32600: Invalid Request
- -32601: Method not found
- -32602: Invalid params
- -32000: Server error 