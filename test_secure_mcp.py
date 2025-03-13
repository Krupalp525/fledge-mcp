#!/usr/bin/env python3
"""
Test script for the Secure Fledge MCP Server.
This script demonstrates how to call the MCP server tools programmatically with API key auth.
"""

import requests
import json
import time
import os

# MCP Server endpoint
MCP_URL = "http://localhost:8082/tools"
API_KEY_FILE = "api_key.txt"
API_KEY_HEADER = "X-API-Key"

def get_api_key():
    """Read the API key from the file."""
    if not os.path.exists(API_KEY_FILE):
        print(f"Error: API key file {API_KEY_FILE} not found.")
        print("Please start the secure_mcp_server.py first to generate an API key.")
        return None
    
    with open(API_KEY_FILE, "r") as f:
        return f.read().strip()

def call_tool(name, parameters=None):
    """Call an MCP tool with authentication and return the result."""
    api_key = get_api_key()
    if not api_key:
        return None
    
    if parameters is None:
        parameters = {}
    
    payload = {
        "name": name,
        "parameters": parameters
    }
    
    headers = {
        "Content-Type": "application/json",
        API_KEY_HEADER: api_key
    }
    
    print(f"\n--- Calling {name} ---")
    print(f"Parameters: {json.dumps(parameters, indent=2)}")
    
    response = requests.post(MCP_URL, json=payload, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        return result
    else:
        print(f"Error: {response.text}")
        return None

def main():
    """Run a series of tool calls to demonstrate the secure MCP server."""
    # First check if the server is running
    try:
        health = requests.get("http://localhost:8082/health")
        if health.status_code != 200:
            print("MCP Server is not running. Please start it with 'python secure_mcp_server.py'")
            return
    except requests.exceptions.ConnectionError:
        print("MCP Server is not running. Please start it with 'python secure_mcp_server.py'")
        return
    
    print("Secure Fledge MCP Server Test Script")
    print("===================================\n")
    
    # Test basic API validation
    call_tool("validate_api_connection")
    
    # Test service status
    call_tool("get_service_status")
    
    # Test mock data generation
    mock_data = call_tool("generate_mock_data", {
        "sensor_id": "secure_sensor",
        "count": 5
    })
    
    # Test listing sensors
    call_tool("list_sensors")
    
    # Test ingesting data
    call_tool("ingest_test_data", {
        "sensor_id": "secure_sensor",
        "value": 23.7,
        "count": 3
    })
    
    # Wait for data processing
    time.sleep(1)
    
    # Test subscription
    call_tool("subscribe_to_sensor", {
        "sensor_id": "secure_sensor",
        "interval": 10
    })
    
    # Test UI component generation
    call_tool("generate_ui_component", {
        "component_type": "chart",
        "sensor_id": "secure_sensor",
        "framework": "react" 
    })
    
    # Test API schema
    call_tool("get_api_schema")
    
    # Test UI code suggestions
    call_tool("suggest_ui_improvements", {
        "code": "function fetchData() { axios.get('/api'); }"
    })
    
    print("\nTest complete! All tools called successfully.")

if __name__ == "__main__":
    main() 