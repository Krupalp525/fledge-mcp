#!/usr/bin/env python3
"""
Setup script for the Fledge MCP Server.
Installs dependencies and configures the environment.
"""

import subprocess
import sys
import os
import time

def print_header(message):
    """Print a formatted header message."""
    print("\n" + "=" * 60)
    print(message)
    print("=" * 60)

def check_prerequisites():
    """Check if all prerequisites are installed."""
    print_header("Checking Prerequisites")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("ERROR: Python 3.8 or higher is required.")
        return False
    
    # Check pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
        print("pip is installed.")
    except subprocess.CalledProcessError:
        print("ERROR: pip is not installed or not working properly.")
        return False
    
    # Check if Fledge is installed (if possible)
    try:
        # Just check if the fledge command exists, don't actually run it
        subprocess.run(["fledge", "--version"], capture_output=True)
        print("Fledge is installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("WARNING: Fledge command not found. This is only a problem if you're running on the same machine as Fledge.")
        print("If Fledge is running on a different machine, update the FLEDGE_API variable in mcp_server.py.")
    
    return True

def install_dependencies():
    """Install required Python packages."""
    print_header("Installing Dependencies")
    print("Installing required packages from requirements.txt...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        return False

def test_connection():
    """Test connection to the Fledge API if possible."""
    import requests
    
    print_header("Testing Fledge Connection")
    print("Attempting to connect to Fledge API at http://localhost:8081/fledge...")
    
    try:
        response = requests.get("http://localhost:8081/fledge/ping")
        if response.status_code == 200:
            print("Successfully connected to Fledge!")
            print(f"Fledge response: {response.json()}")
            return True
        else:
            print(f"Warning: Received status code {response.status_code} from Fledge.")
            print("Check if Fledge is running or update FLEDGE_API in mcp_server.py.")
            return False
    except requests.exceptions.ConnectionError:
        print("Warning: Could not connect to Fledge at http://localhost:8081.")
        print("If Fledge is running on a different machine or port, update FLEDGE_API in mcp_server.py.")
        return False

def main():
    """Run the setup process."""
    print_header("Fledge MCP Server Setup")
    
    if not check_prerequisites():
        print("Failed prerequisite check. Please resolve issues and try again.")
        return
    
    if not install_dependencies():
        print("Failed to install dependencies. Please resolve issues and try again.")
        return
    
    try:
        # This import will fail if dependencies weren't installed
        import requests
        test_connection()
    except ImportError:
        print("Warning: Could not import requests module. Connection test skipped.")
    
    print_header("Setup Complete")
    print("You can now run the MCP server using:")
    print("  python mcp_server.py  # Standard server")
    print("  python secure_mcp_server.py  # Server with API key authentication")
    print("\nTo test the server:")
    print("  python test_mcp.py  # Test standard server")
    print("  python test_secure_mcp.py  # Test secure server")

if __name__ == "__main__":
    main() 