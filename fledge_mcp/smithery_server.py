import asyncio
import websockets
import json
import logging
import os
from datetime import datetime, timedelta
import random
import requests
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmitheryFledgeMCP")

# Fledge API base URL (configurable through environment)
FLEDGE_API = os.getenv("FLEDGE_API_URL", "http://localhost:8081/fledge")

# Server capabilities and metadata
SERVER_INFO = {
    "name": "fledge-mcp",
    "version": "1.0.0",
    "description": "Fledge Model Context Protocol (MCP) Server for Cursor AI integration",
    "vendor": "Fledge",
    "capabilities": {
        "tools": True,
        "streaming": True,
        "authentication": "api_key"
    }
}

# Configuration schema for Smithery
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "fledge_api_url": {
            "type": "string",
            "description": "Fledge API URL",
            "default": "http://localhost:8081/fledge"
        }
    }
}

# Mock data store (in-memory for ephemeral storage)
subscriptions = {}

async def handle_initialize(params):
    """Handle the initialize method required by MCP."""
    return {
        "jsonrpc": "2.0",
        "result": {
            "serverInfo": SERVER_INFO,
            "configSchema": CONFIG_SCHEMA
        },
        "id": params.get("id")
    }

async def handle_tools_list(params):
    """Handle the tools/list method."""
    with open('smithery.json', 'r') as f:
        config = json.load(f)
    
    return {
        "jsonrpc": "2.0",
        "result": {
            "tools": config.get("tools", [])
        },
        "id": params.get("id")
    }

async def handle_tool_call(params):
    """Handle tool calls from Cursor."""
    tool_name = params.get("name")
    tool_params = params.get("parameters", {})
    logger.info(f"Received tool call: {tool_name} with params: {tool_params}")

    try:
        # Data Access and Management Tools
        if tool_name == "get_sensor_data":
            sensor_id = tool_params.get("sensor_id")
            time_range = tool_params.get("time_range")
            limit = tool_params.get("limit", 100)
            if not sensor_id:
                return {"error": {"code": -32602, "message": "sensor_id required"}}
            url = f"{FLEDGE_API}/asset/{sensor_id}?limit={limit}"
            if time_range:
                url += f"&time_range={time_range}"
            response = requests.get(url)
            return {"result": response.json()}

        elif tool_name == "list_sensors":
            response = requests.get(f"{FLEDGE_API}/asset")
            return response.json()

        elif tool_name == "ingest_test_data":
            sensor_id = tool_params.get("sensor_id")
            value = tool_params.get("value")
            count = tool_params.get("count", 1)
            if not sensor_id or value is None:
                return {"error": "sensor_id and value required"}
            for _ in range(count):
                payload = {"asset": sensor_id, "timestamp": "now", "readings": {"value": value}}
                requests.post(f"{FLEDGE_API}/south/ingest", json=payload)
            return {"result": f"Ingested {count} data points"}

        # Service Control Tools
        elif tool_name == "get_service_status":
            response = requests.get(f"{FLEDGE_API}/service")
            return response.json()

        elif tool_name == "update_config":
            config_key = tool_params.get("config_key")
            value = tool_params.get("value")
            if not config_key or value is None:
                return {"error": "config_key and value required"}
            payload = {config_key: value}
            response = requests.put(f"{FLEDGE_API}/category/core", json=payload)
            return response.json()

        # Frontend Code Generation Tools
        elif tool_name == "generate_ui_component":
            component_type = tool_params.get("component_type")
            sensor_id = tool_params.get("sensor_id", "example_sensor")
            framework = tool_params.get("framework", "react")
            if component_type == "chart":
                code = f"""
import React, {{ useEffect, useState }} from 'react';
import {{ Line }} from 'react-chartjs-2';
import axios from 'axios';

const {sensor_id}Chart = () => {{
  const [data, setData] = useState({{ labels: [], datasets: [] }});

  useEffect(() => {{
    axios.get('{FLEDGE_API}/asset/{sensor_id}')
      .then(res => {{
        const readings = res.data;
        setData({{
          labels: readings.map(r => r.timestamp),
          datasets: [{{ label: '{sensor_id}', data: readings.map(r => r.readings.value) }}]
        }});
      }});
  }}, []);

  return <Line data={{data}} />;
}};
export default {sensor_id}Chart;
"""
                return {"code": code}
            return {"error": "Unsupported component_type"}

        elif tool_name == "fetch_sample_frontend":
            framework = tool_params.get("framework", "react")
            code = f"// Sample {framework} frontend for Fledge\nconsole.log('Hello Fledge');"
            return {"code": code}

        # Real-Time Data Streaming Tools
        elif tool_name == "subscribe_to_sensor":
            sensor_id = tool_params.get("sensor_id")
            interval = tool_params.get("interval", 5)
            if not sensor_id:
                return {"error": "sensor_id required"}
            subscriptions[sensor_id] = interval
            return {"result": f"Subscribed to {sensor_id} every {interval}s"}

        elif tool_name == "get_latest_reading":
            sensor_id = tool_params.get("sensor_id")
            if not sensor_id:
                return {"error": "sensor_id required"}
            response = requests.get(f"{FLEDGE_API}/asset/{sensor_id}?limit=1")
            return response.json()[0]

        # Debugging and Validation Tools
        elif tool_name == "validate_api_connection":
            try:
                response = requests.get(f"{FLEDGE_API}/ping")
                return {"result": f"API reachable, version {response.json()['version']}"}
            except Exception as e:
                return {"error": f"API unreachable: {str(e)}"}

        elif tool_name == "simulate_frontend_request":
            endpoint = tool_params.get("endpoint")
            method = tool_params.get("method", "GET")
            payload = tool_params.get("payload", {})
            if not endpoint:
                return {"error": "endpoint required"}
            url = f"{FLEDGE_API}{endpoint}"
            response = requests.request(method, url, json=payload)
            return response.json()

        # Documentation and Schema Tools
        elif tool_name == "get_api_schema":
            schema = {"endpoints": ["/asset", "/service", "/south/ingest"]}
            return schema

        elif tool_name == "list_plugins":
            response = requests.get(f"{FLEDGE_API}/plugin")
            return response.json()

        # Advanced AI-Assisted Features
        elif tool_name == "suggest_ui_improvements":
            code = tool_params.get("code", "")
            suggestions = ["Add error handling for API calls"] if "try" not in code else ["Looks good!"]
            return {"suggestions": suggestions}

        elif tool_name == "generate_mock_data":
            sensor_id = tool_params.get("sensor_id", "mock_sensor")
            count = tool_params.get("count", 10)
            mock_data = [
                {"timestamp": (datetime.now() - timedelta(seconds=i)).isoformat(), "readings": {"value": random.uniform(20, 30)}}
                for i in range(count)
            ]
            return mock_data

        else:
            return {"error": {"code": -32601, "message": "Unknown tool"}}

    except Exception as e:
        logger.error(f"Error in {tool_name}: {str(e)}")
        return {"error": {"code": -32000, "message": str(e)}}

async def handle_message(message_data):
    """Handle incoming JSON-RPC messages."""
    try:
        if not isinstance(message_data, dict):
            return {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None}

        method = message_data.get("method")
        params = message_data.get("params", {})
        msg_id = message_data.get("id", str(uuid.uuid4()))

        if method == "initialize":
            return await handle_initialize(message_data)
        elif method == "tools/list":
            return await handle_tools_list(message_data)
        elif method == "tools/call":
            result = await handle_tool_call(params)
            return {
                "jsonrpc": "2.0",
                **result,
                "id": msg_id
            }
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method {method} not found"},
                "id": msg_id
            }

    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": str(e)},
            "id": message_data.get("id", None)
        }

async def handle_websocket(websocket, path):
    """Handle WebSocket connections."""
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                response = await handle_message(data)
                await websocket.send(json.dumps(response))
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                    "id": None
                }))
            except Exception as e:
                await websocket.send(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": str(e)},
                    "id": None
                }))
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")

async def main():
    """Start the WebSocket server."""
    port = int(os.getenv("PORT", "8082"))
    server = await websockets.serve(handle_websocket, "0.0.0.0", port)
    logger.info(f"Starting Smithery Fledge MCP Server on port {port}...")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main()) 