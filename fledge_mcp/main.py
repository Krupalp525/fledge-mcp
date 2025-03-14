#!/usr/bin/env python3
"""
Main entry point for the Fledge MCP Server.

This module provides a consolidated entry point for starting the Fledge MCP Server,
handling command-line arguments, environment variables, and server configuration.
"""

import os
import sys
import asyncio
import logging
import argparse
import json
from pathlib import Path
import http.server
import socketserver
import threading

import websockets

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FledgeMCP")

# Default values
DEFAULT_PORT = 8082
DEFAULT_FLEDGE_API = "http://localhost:8081/fledge"
DEFAULT_TOOLS_FILE = str(Path(__file__).parent / "smithery.json")

# Server info
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

# Load tools from JSON file
def load_tools(tools_file=DEFAULT_TOOLS_FILE):
    """Load tool definitions from a JSON file."""
    try:
        with open(tools_file, 'r') as f:
            config = json.load(f)
        return config.get("tools", [])
    except Exception as e:
        logger.error(f"Failed to load tools from {tools_file}: {e}")
        # Provide minimal set of tools if file can't be loaded
        return []

# Configuration schema
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "fledge_api_url": {
            "type": "string",
            "description": "Fledge API URL",
            "default": DEFAULT_FLEDGE_API
        }
    }
}

# Mock data store (in-memory for ephemeral storage)
subscriptions = {}

async def handle_initialize(params, api_key=None):
    """Handle the initialize method required by MCP."""
    return {
        "jsonrpc": "2.0",
        "result": {
            "serverInfo": SERVER_INFO,
            "configSchema": CONFIG_SCHEMA
        },
        "id": params.get("id")
    }

async def handle_tools_list(params, tools_file=DEFAULT_TOOLS_FILE, api_key=None):
    """Handle the tools/list method."""
    tools = load_tools(tools_file)
    return {
        "jsonrpc": "2.0",
        "result": {
            "tools": tools
        },
        "id": params.get("id")
    }

# Import the tool handling logic
from fledge_mcp.smithery_server import handle_tool_call

async def handle_message(message_data, fledge_api=DEFAULT_FLEDGE_API, tools_file=DEFAULT_TOOLS_FILE, api_key=None):
    """Handle incoming JSON-RPC messages."""
    try:
        if not isinstance(message_data, dict):
            return {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None}

        method = message_data.get("method")
        params = message_data.get("params", {})
        msg_id = message_data.get("id")

        # Set environment variable for imported handlers
        os.environ["FLEDGE_API_URL"] = fledge_api

        if method == "initialize":
            return await handle_initialize(message_data, api_key)
        elif method == "tools/list":
            return await handle_tools_list(message_data, tools_file, api_key)
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

async def handle_websocket(websocket, path, fledge_api=DEFAULT_FLEDGE_API, tools_file=DEFAULT_TOOLS_FILE, api_key=None):
    """Handle WebSocket connections."""
    try:
        logger.info(f"Client connected: {websocket.remote_address}")
        async for message in websocket:
            try:
                logger.debug(f"Received message: {message}")
                data = json.loads(message)
                response = await handle_message(data, fledge_api, tools_file, api_key)
                logger.debug(f"Sending response: {response}")
                await websocket.send(json.dumps(response))
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                    "id": None
                }))
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await websocket.send(json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": str(e)},
                    "id": None
                }))
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")

class HealthCheckHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler for health check endpoint."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/health":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = json.dumps({"status": "ok", "message": "Fledge MCP Server is running"})
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = json.dumps({"error": "Not found", "status": 404})
            self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format%args))

def start_http_server(port=8083):
    """Start HTTP server for health checks."""
    handler = HealthCheckHandler
    httpd = socketserver.TCPServer(("", port), handler)
    logger.info(f"Starting HTTP server for health checks on port {port}")
    http_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    http_thread.start()
    return httpd

async def main(port=DEFAULT_PORT, fledge_api=DEFAULT_FLEDGE_API, tools_file=DEFAULT_TOOLS_FILE, api_key=None, http_port=8083):
    """Start the WebSocket server."""
    logger.info(f"Starting Fledge MCP Server on port {port}...")
    logger.info(f"Using Fledge API: {fledge_api}")
    logger.info(f"Loading tools from: {tools_file}")
    
    if api_key:
        logger.info("API key authentication enabled")
    
    # Start HTTP server for health checks
    http_server = start_http_server(http_port)
    
    # Initialize the server
    server = await websockets.serve(
        lambda ws, path: handle_websocket(ws, path, fledge_api, tools_file, api_key),
        "0.0.0.0", 
        port
    )
    
    logger.info("Server started successfully!")
    
    try:
        await server.wait_closed()
    finally:
        # Shutdown HTTP server on exit
        logger.info("Shutting down HTTP server")
        http_server.shutdown()

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Fledge MCP Server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to listen on")
    parser.add_argument("--http-port", type=int, default=8083, help="HTTP port for health checks")
    parser.add_argument("--fledge-api", type=str, default=DEFAULT_FLEDGE_API, help="Fledge API URL")
    parser.add_argument("--tools-file", type=str, default=DEFAULT_TOOLS_FILE, help="Path to tools JSON file")
    parser.add_argument("--api-key", type=str, help="API key for authentication")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level")
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Configure logging level
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        print(f"Invalid log level: {args.log_level}")
        sys.exit(1)
    logging.getLogger().setLevel(numeric_level)
    
    # Use environment variables if not provided as arguments
    port = int(os.getenv("PORT", args.port))
    http_port = int(os.getenv("HTTP_PORT", args.http_port))
    fledge_api = os.getenv("FLEDGE_API_URL", args.fledge_api)
    tools_file = os.getenv("TOOLS_FILE", args.tools_file)
    api_key = os.getenv("API_KEY", args.api_key)
    
    # Start the server
    asyncio.run(main(port, fledge_api, tools_file, api_key, http_port)) 