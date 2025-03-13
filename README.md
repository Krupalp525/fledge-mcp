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