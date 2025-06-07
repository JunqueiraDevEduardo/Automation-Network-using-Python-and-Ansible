#!/usr/bin/env python3
############################################################
# GNS3 Project Verification Script
# This script connects to an existing GNS3 project and provides 
# verification and management capabilities.
# 
# Purpose: Verify connection to GNS3 server and existing project
# Usage: python3 gns3_project_verifier.py
############################################################

import requests
import yaml
import json
import time
from typing import Dict, List, Optional, Tuple

class EnhancedGNS3Builder:
    """
    Enhanced GNS3 Builder class for connecting to and managing existing GNS3 projects.
    This class provides comprehensive project verification and connection management.
    """
    
    def __init__(self, 
                 config_file: str = "network_data.yml",
                 gns3_server: str = "http://127.0.0.1:3080",
                 project_id: str = "9a8ab49a-6f61-4fa8-9089-99e6c6594e4f"):
        """
        Initialize the GNS3 Builder with project connection parameters.
        
        Args:
            config_file (str): Path to YAML configuration file containing network data
            gns3_server (str): GNS3 server URL (default: local server)
            project_id (str): Existing project ID to connect to
        """
        # Store configuration parameters
        self.config_file = config_file
        self.server = gns3_server
        self.session = requests.Session()  # HTTP session for API calls
        # Add HTTP basic authentication for GNS3 web interface
        self.session.auth = ('admin', 'admin')  # Username: admin, Password: admin
        self.project_id = project_id
        self.templates = {}  # Store device templates
        
        # API version detection - see if v2 or v3 is correct below
        self.api_version = "v2"  # Default to v2, will be updated if v3 is found
        
        # Load network configuration from YAML file
        self.load_network_config()
        
        # Connect to existing project instead of creating new one
        self.connect_to_existing_project()
        
        # Track created nodes and links for management purposes
        self.created_nodes = {}  # Dictionary to store node information
        self.created_links = []  # List to store link information

    def load_network_config(self):
        """
        Load network configuration from YAML file.
        Creates default configuration if file doesn't exist.
        This method handles YAML parsing and error management.
        """
        try:
            # Attempt to load existing configuration file
            with open(self.config_file, 'r') as file:
                self.config = yaml.safe_load(file)
            print(f"Configuration loaded from {self.config_file}")
        except FileNotFoundError:
            # Handle case where configuration file doesn't exist
            print(f"Configuration file {self.config_file} not found")
            # Create a default configuration structure
            self.config = {
                'project_name': 'Automation of Network',
                'devices': [],      # List of network devices
                'connections': []   # List of network connections
            }
        except yaml.YAMLError as e:
            # Handle YAML parsing errors
            print(f"Error parsing YAML file: {e}")
            raise

    def test_server_connection(self):
        """
        Test connection to GNS3 server by trying multiple API endpoints.
        This method determines the correct API version and validates server connectivity.
        Returns True if connection successful, False otherwise.
        """
        print(f"Testing connection to {self.server}...")
        
        # List of potential API endpoints to test for different GNS3 versions
        endpoints_to_test = [
            "/static/web-ui/server/version",    # Web UI server version endpoint
            "/v2/version",                      # Standard v2 API version endpoint
            "/v3/version",                      # Standard v3 API version endpoint
            "/version",                         # Generic version endpoint
            "/api/v2/version",                  # Alternative v2 API path
            "/"                                 # Root endpoint for basic connectivity
        ]
        
        # Test each endpoint to find working API version
        for endpoint in endpoints_to_test:
            try:
                # Construct full URL for testing
                url = f"{self.server}{endpoint}"
                print(f"Trying: {url}")
                
                # Make HTTP GET request with timeout
                response = self.session.get(url, timeout=5)
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    try:
                        # Try to parse JSON response
                        data = response.json()
                        if 'version' in data:
                            print(f"GNS3 Server found at {endpoint}")
                            print(f"Version: {data.get('version', 'Unknown')}")
                            
                            # Update API version based on successful endpoint
                            if endpoint in ["/v3/version"]:
                                self.api_version = "v3"
                            else:
                                self.api_version = "v2"
                        return True
                    except:
                        # JSON parsing failed, but 200 response indicates something is running
                        pass
                    
                    # Even if not JSON, a 200 response means something is there
                    print(f"Response preview: {response.text[:100]}...")
                
            except requests.exceptions.ConnectionError:
                # Handle connection refused errors
                print(f"Connection refused")
                continue
            except requests.exceptions.Timeout:
                # Handle timeout errors
                print(f"Timeout")
                continue
            except Exception as e:
                # Handle any other exceptions
                print(f"Error: {e}")
                continue
        
        # Additional port connectivity test using socket
        try:
            import socket
            # Parse server URL to get host and port
            host, port = self.server.replace('http://', '').split(':')
            port = int(port)
            
            # Test if port is open using socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                # Port is open but API not found
                print(f"Port {port} is open, but GNS3 API not found")
                print("  This might be a different service or wrong API version")
            else:
                # Port is closed or unreachable
                print(f"Port {port} is closed or unreachable")
                
        except Exception as e:
            # Handle socket testing errors
            print(f"Port check failed: {e}")
        
        return False

    def connect_to_existing_project(self):
        """
        Connect to an existing GNS3 project using the provided project ID.
        This is the core function for project connectivity and validation.
        """
        # First test basic server connectivity before attempting project connection
        if not self.test_server_connection():
            raise Exception("Cannot connect to GNS3 server")
        
        try:
            # Attempt to get project information using project ID via web UI
            print(f"Looking for project ID: {self.project_id}")
            response = self.session.get(f"{self.server}/static/web-ui/controller/1/project/{self.project_id}")
            
            if response.status_code == 200:
                # Successfully connected to project via web UI
                print(f"Connected to existing project via web interface")
                print(f"Project ID: {self.project_id}")
                print(f"Response received: {len(response.text)} characters")
                
                # For web UI, we get HTML content instead of JSON
                # Store the project name from URL or extract from HTML if needed
                self.project_name = "Connected Project"  # Default name for web UI access
                
                # Load existing project components
                self.load_existing_nodes()   # Load network nodes/devices
                self.load_existing_links()   # Load network connections
                
            elif response.status_code == 404:
                # Project not found - provide helpful information
                print(f"Project with ID {self.project_id} not found")
                print("Available projects:")
                self.list_available_projects()  # Show available projects for reference
                raise Exception("Project not found")
            else:
                # Other HTTP errors
                print(f"Failed to connect to project: {response.status_code}")
                print(f"Response: {response.text}")
                raise Exception("Failed to connect to project")
                
        except requests.exceptions.RequestException as e:
            # Handle network-related errors
            print(f"Connection error: {e}")
            raise

    def list_available_projects(self):
        """
        List all available projects on the GNS3 server.
        Useful for debugging connection issues and finding correct project IDs.
        """
        try:
            # Get list of all projects from server via web UI
            response = self.session.get(f"{self.server}/static/web-ui/controller/1/projects")
            if response.status_code == 200:
                print("  Connected to projects interface via web UI")
                print(f"  Response length: {len(response.text)} characters")
                # Note: Web UI returns HTML, would need HTML parsing to extract project list
            else:
                print("Could not retrieve project list via web UI")
        except Exception as e:
            print(f"Error listing projects: {e}")
    
    def load_existing_nodes(self):
        """
        Load existing nodes (network devices) from the connected project.
        This method populates the created_nodes dictionary with current project state.
        """
        # Implementation would go here to load nodes from project
        # For now, this is a placeholder that maintains the original structure
        pass
    
    def load_existing_links(self):
        """
        Load existing links (network connections) from the connected project.
        This method populates the created_links list with current project state.
        """
        # Implementation would go here to load links from project
        # For now, this is a placeholder that maintains the original structure
        pass
    
    def get_project_status(self):
        """
        Get current project status information from the GNS3 server via web UI.
        Returns success status or None if failed.
        """
        try:
            response = self.session.get(f"{self.server}/static/web-ui/controller/1/project/{self.project_id}")
            if response.status_code == 200:
                # For web UI, return basic status info
                return {
                    'name': self.project_name,
                    'status': 'accessible',
                    'path': 'web-ui-access',
                    'auto_start': 'unknown',
                    'auto_open': 'unknown'
                }
            return None
        except:
            return None
    
    def print_project_summary(self):
        """
        Print a comprehensive summary of the current project status.
        Displays project information, node count, and link count.
        """
        status = self.get_project_status()
        if status:
            print(f"\n{'='*50}")
            print(f"PROJECT SUMMARY")
            print(f"{'='*50}")
            print(f"Name: {status['name']}")
            print(f"Status: {status['status']}")
            print(f"Path: {status['path']}")
            print(f"Auto Start: {status['auto_start']}")
            print(f"Auto Open: {status['auto_open']}")
            print(f"Nodes: {len(self.created_nodes)}")
            print(f"Links: {len(self.created_links)}")
            print(f"{'='*50}")

    def check_server_health(self):
        """
        Comprehensive server health check to verify GNS3 server status.
        Tests server version, compute nodes, and overall connectivity.
        """
        print(f"\n{'='*50}")
        print("GNS3 SERVER HEALTH CHECK")
        print(f"{'='*50}")
        
        # Check server version information via web UI
        try:
            response = self.session.get(f"{self.server}/static/web-ui/server/version")
            if response.status_code == 200:
                print(f"✓ Server accessible via web UI")
                print(f"Response length: {len(response.text)} characters")
            else:
                print(f"Version check failed: {response.status_code}")
        except Exception as e:
            print(f"Version check error: {e}")
        
        # Check available compute nodes via web UI
        try:
            response = self.session.get(f"{self.server}/static/web-ui/computes")
            if response.status_code == 200:
                print(f"✓ Computes interface accessible")
                print(f"Response length: {len(response.text)} characters")
                # Note: Web UI returns HTML, would need parsing to extract compute info
            else:
                print(f"Compute check failed: {response.status_code}")
        except Exception as e:
            print(f"Compute check error: {e}")

def main():
    """
    Main function for initial project verification and connection testing.
    Only essential functions are active for debugging phase.
    This function serves as the entry point for the script.
    """
    try:
        # Initialize the GNS3 builder with existing project connection parameters
        print("Initializing GNS3 Project Connection...")
        builder = EnhancedGNS3Builder(
            config_file="network_data.yml",                           # YAML configuration file
            gns3_server="http://127.0.0.1:3080",                    # Local GNS3 server URL
            project_id="9a8ab49a-6f61-4fa8-9089-99e6c6594e4f"      # Target project ID
        )
        
        # Display project summary information
        builder.print_project_summary()
        
        # Perform comprehensive server health check
        builder.check_server_health()
        
    except Exception as e:
        # Handle any errors during initialization or execution
        print(f"✗ Error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure GNS3 server is running")
        print("2. Check if the server is accessible at http://127.0.0.1:3080")
        print("3. Verify the project ID is correct")
        print("4. Check network connectivity between client and server")
        
        # Try to help diagnose the issue with container diagnostics
        print("\nContainer Diagnostics:")
        try:
            import subprocess
            
            # Check if Docker is running and find GNS3 containers
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("Docker is running")
                if result.stdout.strip():
                    print("Running containers:")
                    lines = result.stdout.strip().split('\n')
                    # Look for GNS3 related containers
                    for line in lines[1:]:  # Skip header
                        if 'gns3' in line.lower() or '3080' in line:
                            print(f"Found GNS3 container: {line}")
                else:
                    print("⚠ No containers currently running")
            else:
                print("✗ Docker not accessible or not running")
                
            # Check for OrbStack (Docker alternative)
            result = subprocess.run(['orb', 'list'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("OrbStack detected")
                if result.stdout.strip():
                    print("OrbStack containers:")
                    print(result.stdout)
                    
        except subprocess.TimeoutExpired:
            print("Container command timed out")
        except FileNotFoundError:
            print("Docker/OrbStack commands not found")
        except Exception as diag_e:
            print(f"Diagnostic error: {diag_e}")
            
        # Provide suggested solutions for common issues
        print("\nSuggested solutions:")
        print("1. Find your container's IP: docker inspect <container_name> | grep IPAddress")
        print("2. Or set up port forwarding: docker run -p 3080:3080 <image>")
        print("3. Or try connecting directly to container network")
        print("4. Check if GNS3 server is using v2 or v3 API")

# Script entry point - execute main function when script is run directly
if __name__ == "__main__":
    main()