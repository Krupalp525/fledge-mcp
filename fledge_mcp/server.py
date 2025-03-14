import aiohttp
from aiohttp import web
import requests
import json
import subprocess
import logging
from datetime import datetime, timedelta
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FledgeMCP")

# Fledge API base URL (adjust if different)
FLEDGE_API = "http://localhost:8081/fledge"

# Mock data store for subscriptions (in-memory for simplicity)
subscriptions = {}

async def handle_tool_call(request):
    """Handle incoming tool calls from Cursor."""
    data = await request.json()
    tool_name = data.get("name")
    params = data.get("parameters", {})
    logger.info(f"Received tool call: {tool_name} with params: {params}")

    try:
        # Data Access and Management Tools
        if tool_name == "get_sensor_data":
            sensor_id = params.get("sensor_id")
            time_range = params.get("time_range")
            limit = params.get("limit", 100)
            if not sensor_id:
                return web.json_response({"error": "sensor_id required"}, status=400)
            url = f"{FLEDGE_API}/asset/{sensor_id}?limit={limit}"
            if time_range:
                url += f"&time_range={time_range}"
            response = requests.get(url)
            return web.json_response(response.json())

        elif tool_name == "list_sensors":
            response = requests.get(f"{FLEDGE_API}/asset")
            return web.json_response(response.json())

        elif tool_name == "ingest_test_data":
            sensor_id = params.get("sensor_id")
            value = params.get("value")
            count = params.get("count", 1)
            if not sensor_id or value is None:
                return web.json_response({"error": "sensor_id and value required"}, status=400)
            for _ in range(count):
                payload = {"asset": sensor_id, "timestamp": "now", "readings": {"value": value}}
                requests.post(f"{FLEDGE_API}/south/ingest", json=payload)
            return web.json_response({"result": f"Ingested {count} data points"})

        # Fledge Service Control Tools
        elif tool_name == "get_service_status":
            response = requests.get(f"{FLEDGE_API}/service")
            return web.json_response(response.json())

        elif tool_name == "start_stop_service":
            service_type = params.get("service_type")
            action = params.get("action")
            if not service_type or action not in ["start", "stop"]:
                return web.json_response({"error": "Invalid service_type or action"}, status=400)
            subprocess.run(["fledge", action, service_type], check=True)
            return web.json_response({"result": f"{service_type} {action}ed"})

        elif tool_name == "update_config":
            config_key = params.get("config_key")
            value = params.get("value")
            if not config_key or value is None:
                return web.json_response({"error": "config_key and value required"}, status=400)
            payload = {config_key: value}
            response = requests.put(f"{FLEDGE_API}/category/core", json=payload)
            return web.json_response(response.json())

        # Frontend Code Generation Tools
        elif tool_name == "generate_ui_component":
            component_type = params.get("component_type")
            sensor_id = params.get("sensor_id", "example_sensor")
            framework = params.get("framework", "react")
            if component_type == "chart":
                code = f"""
import React, {{ useEffect, useState }} from 'react';
import {{ Line }} from 'react-chartjs-2';
import axios from 'axios';

const {sensor_id}Chart = () => {{
  const [data, setData] = useState({{ labels: [], datasets: [] }});

  useEffect(() => {{
    axios.get('http://localhost:8081/fledge/asset/{sensor_id}')
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
                return web.json_response({"code": code})
            return web.json_response({"error": "Unsupported component_type"}, status=400)

        elif tool_name == "fetch_sample_frontend":
            framework = params.get("framework", "react")
            # Simplified: return a basic template
            code = f"// Sample {framework} frontend for Fledge\nconsole.log('Hello Fledge');"
            return web.json_response({"code": code})

        # Real-Time Data Streaming Tools
        elif tool_name == "subscribe_to_sensor":
            sensor_id = params.get("sensor_id")
            interval = params.get("interval", 5)
            if not sensor_id:
                return web.json_response({"error": "sensor_id required"}, status=400)
            subscriptions[sensor_id] = interval  # Store subscription
            return web.json_response({"result": f"Subscribed to {sensor_id} every {interval}s"})

        elif tool_name == "get_latest_reading":
            sensor_id = params.get("sensor_id")
            if not sensor_id:
                return web.json_response({"error": "sensor_id required"}, status=400)
            response = requests.get(f"{FLEDGE_API}/asset/{sensor_id}?limit=1")
            return web.json_response(response.json()[0])

        # Debugging and Validation Tools
        elif tool_name == "validate_api_connection":
            try:
                response = requests.get(f"{FLEDGE_API}/ping")
                return web.json_response({"result": f"API reachable, version {response.json()['version']}"})
            except Exception as e:
                return web.json_response({"error": f"API unreachable: {str(e)}"}, status=503)

        elif tool_name == "simulate_frontend_request":
            endpoint = params.get("endpoint")
            method = params.get("method", "GET")
            payload = params.get("payload", {})
            if not endpoint:
                return web.json_response({"error": "endpoint required"}, status=400)
            url = f"{FLEDGE_API}{endpoint}"
            response = requests.request(method, url, json=payload)
            return web.json_response(response.json())

        # Documentation and Schema Tools
        elif tool_name == "get_api_schema":
            # Simplified: return known endpoints
            schema = {"endpoints": ["/asset", "/service", "/south/ingest"]}
            return web.json_response(schema)

        elif tool_name == "list_plugins":
            response = requests.get(f"{FLEDGE_API}/plugin")
            return web.json_response(response.json())

        # Advanced AI-Assisted Features
        elif tool_name == "suggest_ui_improvements":
            code = params.get("code", "")
            suggestions = ["Add error handling for API calls"] if "try" not in code else ["Looks good!"]
            return web.json_response({"suggestions": suggestions})

        elif tool_name == "generate_mock_data":
            sensor_id = params.get("sensor_id", "mock_sensor")
            count = params.get("count", 10)
            mock_data = [
                {"timestamp": (datetime.now() - timedelta(seconds=i)).isoformat(), "readings": {"value": random.uniform(20, 30)}}
                for i in range(count)
            ]
            return web.json_response(mock_data)

        else:
            return web.json_response({"error": "Unknown tool"}, status=404)

    except Exception as e:
        logger.error(f"Error in {tool_name}: {str(e)}")
        return web.json_response({"error": str(e)}, status=500)

async def health_check(request):
    """Simple health check endpoint."""
    return web.Response(text="Fledge MCP Server is running")

# Set up the server
app = web.Application()
app.router.add_post("/tools", handle_tool_call)
app.router.add_get("/health", health_check)

if __name__ == "__main__":
    logger.info("Starting Fledge MCP Server on port 8082...")
    web.run_app(app, host="localhost", port=8082) 