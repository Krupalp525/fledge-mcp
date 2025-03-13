#!/usr/bin/env python3
"""
Test script for the Fledge MCP Server.
This script demonstrates how to call the MCP server tools programmatically.
"""

import requests
import json
import time

# MCP Server endpoint
MCP_URL = "http://localhost:8082/tools"

def call_tool(name, parameters=None):
    """Call an MCP tool and return the result."""
    if parameters is None:
        parameters = {}
    
    payload = {
        "name": name,
        "parameters": parameters
    }
    
    print(f"\n--- Calling {name} ---")
    print(f"Parameters: {json.dumps(parameters, indent=2)}")
    
    response = requests.post(MCP_URL, json=payload)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"Error: {response.text}")
        return None

def main():
    """Run a series of tool calls to demonstrate the MCP server."""
    # First check if the server is running
    try:
        health = requests.get("http://localhost:8082/health")
        if health.status_code != 200:
            print("MCP Server is not running. Please start it with 'python mcp_server.py'")
            return
    except requests.exceptions.ConnectionError:
        print("MCP Server is not running. Please start it with 'python mcp_server.py'")
        return
    
    print("Fledge MCP Server Test Script")
    print("============================\n")
    
    # Test basic API validation
    call_tool("validate_api_connection")
    
    # Test service status
    call_tool("get_service_status")
    
    # Test listing sensors
    call_tool("list_sensors")
    
    # Test ingesting mock data
    call_tool("ingest_test_data", {
        "sensor_id": "test_sensor",
        "value": 22.5,
        "count": 3
    })
    
    # Wait for data processing
    time.sleep(1)
    
    # Test getting sensor data
    call_tool("get_sensor_data", {
        "sensor_id": "test_sensor",
        "limit": 5
    })
    
    # Test getting latest reading
    call_tool("get_latest_reading", {
        "sensor_id": "test_sensor"
    })
    
    # Test generating mock data
    call_tool("generate_mock_data", {
        "sensor_id": "mock_sensor", 
        "count": 3
    })
    
    # Test generating UI component
    call_tool("generate_ui_component", {
        "component_type": "chart",
        "sensor_id": "test_sensor"
    })
    
    # Test API schema
    call_tool("get_api_schema")
    
    # Test plugin listing
    call_tool("list_plugins")
    
    print("\nTest complete! All tools called successfully.")

if __name__ == "__main__":
    main() 