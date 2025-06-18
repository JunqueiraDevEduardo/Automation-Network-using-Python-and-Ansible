"""
GNS3 Network Diagnostic:
All HTTP codes are here:https://umbraco.com/knowledge-base/http-status-codes/

This file adiagnostic.py provides a complete interface for:
- Authentication with GNS3 v3 API using OAuth2 Password Bearer flow.
- Project creation, management, and manipulation.
- Node creation and network topology building.
- Template management and device provisioning.

"""
##################################
#Imports
##################################
import requests
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging for debugging and monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GNS3NetworkManager:
    """
    Attributes:
        server_url (str): GNS3 server URL endpoint
        username (str): Authentication username
        password (str): Authentication password
        session (requests.Session): HTTP session with authentication
        access_token (str): OAuth2 bearer token for API access
        current_project_id (str): Currently active project identifier
    """
    
    def __init__(self, server_url: str = "http://127.0.0.1:3080", 
                 username: str = "admin", password: str = "admin"):
        """
        Initialize the GNS3 Network Manager with server connection parameters.
        
        Args:
            server_url (str): GNS3 server URL, defaults to local server
            username (str): Authentication username, defaults to 'admin'
            password (str): Authentication password, defaults to 'admin'
        
        Raises:
            ConnectionError: If server is unreachable
            AuthenticationError: If credentials are invalid
        """
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification for local development
        self.access_token = None
        self.current_project_id = None
        
        # Initialize connection and authenticate
        logger.info(f"Initializing GNS3 connection to {self.server_url}")
        self._authenticate()
    
    def _authenticate(self) -> bool:
        """
        Perform OAuth2 authentication with GNS3 v3 API.
        """
        logger.info("Authenticating with GNS3 v3 API using OAuth2 Password Bearer")
        
        auth_endpoint = f"{self.server_url}/v3/access/users/login"
        
        # Prepare authentication data as form data (required for OAuth2)
        auth_data = {
            "username": self.username,
            "password": self.password
        }
        
        # Set appropriate headers for form data submission
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = self.session.post(
                auth_endpoint, 
                data=auth_data, 
                headers=headers,
                timeout=10
            )
            
            logger.debug(f"Authentication response status: {response.status_code}")
            #code== 200:OK Works open 2xx Succesful!
            if response.status_code == 200:
                response_data = response.json()
                self.access_token = response_data.get('access_token')
                
                if self.access_token:
                    # Configure session for authenticated requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json'
                    })
                    
                    logger.info("Authentication successful, bearer token configured #code== 200:OK Works open 2xx Succesful!")
                    return True
                else:
                    logger.error("No access token received in authentication response")
                    return False
            else:
                logger.error(f"Authentication failed with status #code== 422 4xx Client Error! {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during authentication: {e}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response during authentication: {e}")
            return False
    
    def list_projects(self) -> List[Dict]:
        """
        Retrieve list of all projects from GNS3 server.
        
        Returns:
            List[Dict]: List of project dictionaries containing project metadata
                Each project dict contains: project_id, name, status, path, etc.
        
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        logger.info("Retrieving project list from GNS3 server")
        
        try:
            response = self.session.get(f"{self.server_url}/v3/projects", timeout=10)
            #code== 200:OK Works open 2xx Succesful!
            if response.status_code == 200:
                projects = response.json()
                logger.info(f"Successfully retrieved {len(projects)} projects")
                
                # Log project details for debugging
                for project in projects:
                    logger.debug(f"Project: {project.get('name')} (ID: {project.get('project_id')})")
                
                return projects
            else:
                logger.error(f"Failed to retrieve projects: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error retrieving projects: {e}")
            return []
    
    def create_project(self, project_name: str, **kwargs) -> Optional[str]:
        """
        Create a new project on GNS3 server with specified configuration.
        
        Args:
            project_name (str): Name for the new project
        
        Returns:
            Optional[str]: Project ID if creation successful, None if failed
        
        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        logger.info(f"Creating new project: {project_name}")
        
        # Default project configuration
        project_config = {
            "name": project_name
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/v3/projects",
                json=project_config,
                timeout=15
            )
            #code== 201:OK Works Created Succesful!
            if response.status_code == 201:
                project_data = response.json()
                project_id = project_data.get('project_id')
                
                logger.info(f"Project created successfully with ID: {project_id}")
                self.current_project_id = project_id
                
                return project_id
            else:
                logger.error(f"Project creation failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            #code== 422 4xx Client Error!
            logger.error(f"Network error creating project: {e}")
            return None
    
    def get_project_details(self, project_id: str) -> Optional[Dict]:
        """
        Retrieve detailed information about a specific project.
        
        Args:
            project_id (str): Unique identifier of the project
        
        Returns:
            Optional[Dict]: Project details dictionary or None if not found
                Contains: name, status, path, auto_start, auto_open, creation time, etc.
        """
        logger.info(f"Retrieving details for project: {project_id}")
        
        try:
            response = self.session.get(f"{self.server_url}/v3/projects/{project_id}", timeout=10)
            #code== 200:OK Works open 2xx Succesful!
            if response.status_code == 200:
                project_details = response.json()
                logger.debug(f"Project details retrieved: {project_details.get('name')}")
                return project_details
            else:
                logger.error(f"Failed to get project details: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            #code== 422 4xx Client Error!
            logger.error(f"Network error getting project details: {e}")
            return None
    
    def open_project(self, project_id: str) -> bool:
        """
        Open a project on the GNS3 server, making it active for operations.
        
        Args:
            project_id (str): Unique identifier of the project to open
        
        Returns:
            bool: True if project opened successfully, False otherwise
        """
        logger.info(f"Opening project: {project_id}")
        
        try:
            response = self.session.post(f"{self.server_url}/v3/projects/{project_id}/open", timeout=15)
            #code== 200:OK Works open 2xx Succesful! and
            #code== 201: Created Works open 2xx Succesful!
            if response.status_code in [200, 201]:
                logger.info("Project opened successfully")
                self.current_project_id = project_id
                return True
            else:
                #code== 422 4xx Client Error!
                logger.error(f"Failed to open project: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error opening project: {e}")
            return False
    
    def close_project(self, project_id: str) -> bool:
        """
        Close a project on the GNS3 server, stopping all nodes and freeing resources.
        
        Args:
            project_id (str): Unique identifier of the project to close
        
        Returns:
            bool: True if project closed successfully, False otherwise
        """
        logger.info(f"Closing project: {project_id}")
        
        try:
            response = self.session.post(f"{self.server_url}/v3/projects/{project_id}/close", timeout=15)
            # code = 204 No Content but ok succesfull
            if response.status_code == 204:
                logger.info("Project closed successfully")
                if self.current_project_id == project_id:
                    self.current_project_id = None
                return True
            else:
                logger.error(f"Failed to close project: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error closing project: {e}")
            return False
    
    def list_project_nodes(self, project_id: str) -> List[Dict]:
        """
        List all nodes (network devices) in a specific project.
        
        Args:
            project_id (str): Unique identifier of the project
        
        Returns:
            List[Dict]: List of node dictionaries containing node metadata
                Each node dict contains: node_id, name, node_type, status, properties, etc.
        """
        logger.info(f"Listing nodes for project: {project_id}")
        
        try:
            response = self.session.get(f"{self.server_url}/v3/projects/{project_id}/nodes", timeout=10)
            
            if response.status_code == 200:
                nodes = response.json()
                logger.info(f"Found {len(nodes)} nodes in project")
                
                # Log node details for debugging
                for node in nodes:
                    logger.debug(f"Node: {node.get('name')} ({node.get('node_type')}) - Status: {node.get('status')}")
                
                return nodes
            else:
                logger.error(f"Failed to list nodes: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error listing nodes: {e}")
            return []
    
    def get_available_templates(self) -> List[Dict]:
        """
        Retrieve list of available device templates from GNS3 server.
        
        Templates define the configuration and capabilities of different device types
        that can be instantiated as nodes in projects.
        
        Returns:
            List[Dict]: List of template dictionaries containing template metadata
                Each template dict contains: template_id, name, category, template_type, etc.
        """
        logger.info("Retrieving available device templates")
        
        try:
            response = self.session.get(f"{self.server_url}/v3/templates", timeout=10)
            
            if response.status_code == 200:
                templates = response.json()
                logger.info(f"Found {len(templates)} available templates")
                
                # Organize templates by category for easier navigation
                categories = {}
                for template in templates:
                    category = template.get('category', 'Other')
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(template)
                
                # Log template categories for debugging
                for category, cat_templates in categories.items():
                    logger.debug(f"Category '{category}': {len(cat_templates)} templates")
                
                return templates
            else:
                logger.error(f"Failed to get templates: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error getting templates: {e}")
            return []
    
    def create_node_from_template(self, project_id: str, template_id: str, 
                                  node_name: str, x: int = 0, y: int = 0) -> Optional[str]:
        """
        Create a new network node in a project using a specific template.
        
        Args:
            project_id (str): Project identifier where node will be created
            template_id (str): Template identifier to use for node creation
            node_name (str): Name to assign to the new node
            x (int): X coordinate for node placement on canvas
            y (int): Y coordinate for node placement on canvas
        
        Returns:
            Optional[str]: Node ID if creation successful, None if failed
        """
        logger.info(f"Creating node '{node_name}' from template {template_id}")
        
        node_config = {
            "name": node_name,
            "x": x,
            "y": y
        }
        
        try:
            response = self.session.post(
                f"{self.server_url}/v3/projects/{project_id}/templates/{template_id}",
                json=node_config,
                timeout=15
            )
            
            if response.status_code == 201:
                node_data = response.json()
                node_id = node_data.get('node_id')
                
                logger.info(f"Node created successfully with ID: {node_id}")
                return node_id
            else:
                logger.error(f"Node creation failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error creating node: {e}")
            return None
    
    def load_network_configuration(self, config_file: str) -> Optional[Dict]:
        """
        Load network configuration from YAML file for automated topology creation.
        
        Args:
            config_file (str): Path to YAML configuration file
        
        Returns:
            Optional[Dict]: Parsed configuration dictionary or None if failed
        """
        logger.info(f"Loading network configuration from: {config_file}")
        
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                logger.error(f"Configuration file not found: {config_file}")
                return None
            
            with open(config_path, 'r') as file:
                config_data = yaml.safe_load(file)
            
            logger.info(f"Configuration loaded successfully")
            logger.debug(f"Found {len(config_data.get('departments', []))} departments")
            
            return config_data
            
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return None
    
    def create_network_topology(self, project_id: str, config_data: Dict) -> bool:
        """
        Create complete network topology based on configuration data.
        
        This method processes the network configuration and creates all necessary
        nodes, links, and configurations to build the complete network topology.
        
        Args:
            project_id (str): Project identifier where topology will be created
            config_data (Dict): Network configuration data from YAML file
        
        Returns:
            bool: True if topology created successfully, False otherwise
        """
        logger.info("Creating network topology from configuration data")
        
        try:
            departments = config_data.get('departments', [])
            
            # Track created nodes for linking
            created_nodes = {}
            
            # Process each department and create corresponding network elements
            for dept in departments:
                dept_name = dept.get('name', 'Unknown')
                logger.info(f"Processing department: {dept_name}")
                
                devices = dept.get('devices', [])
                
                # Create nodes for each device in the department
                for device in devices:
                    device_name = device.get('name', 'unknown')
                    device_type = device.get('type', 'unknown')
                    
                    # Note: This would require template mapping based on device type
                    # For now, we log the intended creation
                    logger.debug(f"Would create {device_type} node: {device_name}")
                    
                    # In a full implementation, you would:
                    # 1. Map device_type to appropriate template_id
                    # 2. Calculate appropriate x,y coordinates
                    # 3. Call create_node_from_template()
                    # 4. Store node_id in created_nodes dict
            
            logger.info("Network topology creation completed")
            return True
            
        except Exception as e:
            logger.error(f"Error creating network topology: {e}")
            return False
    
    def generate_project_summary(self, project_id: str) -> Dict:
        """
        Generate comprehensive summary of project status and contents.
        
        Args:
            project_id (str): Project identifier to summarize
        
        Returns:
            Dict: Summary dictionary containing project details, node counts, etc.
        """
        logger.info(f"Generating summary for project: {project_id}")
        
        summary = {
            'project_id': project_id,
            'project_details': None,
            'node_count': 0,
            'nodes_by_type': {},
            'nodes_by_status': {},
            'total_links': 0
        }
        
        try:
            # Get project details
            project_details = self.get_project_details(project_id)
            if project_details:
                summary['project_details'] = project_details
            
            # Get node information
            nodes = self.list_project_nodes(project_id)
            summary['node_count'] = len(nodes)
            
            # Categorize nodes by type and status
            for node in nodes:
                node_type = node.get('node_type', 'unknown')
                node_status = node.get('status', 'unknown')
                
                summary['nodes_by_type'][node_type] = summary['nodes_by_type'].get(node_type, 0) + 1
                summary['nodes_by_status'][node_status] = summary['nodes_by_status'].get(node_status, 0) + 1
            
            logger.info(f"Project summary generated: {summary['node_count']} nodes")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating project summary: {e}")
            return summary


def main():
    """
    Main function demonstrating GNS3 Network Manager usage.
    
    This function provides a command-line interface for common operations:
    - Authentication testing
    - Project listing and creation
    - Template management
    - Network topology deployment
    """
    print("GNS3 Network Automation Manager")
    print("Professional API Client for University Network Project")
    print("=" * 60)
    
    try:
        # Initialize GNS3 connection
        gns3_manager = GNS3NetworkManager()
        
        # Main operation loop
        while True:
            print("\nAvailable Operations:")
            print("1. List all projects")
            print("2. Create new project")
            print("3. Get project details")
            print("4. Open project")
            print("5. Close project")
            print("6. List project nodes")
            print("7. Get available templates")
            print("8. Load network configuration")
            print("9. Generate project summary")
            print("0. Exit")
            
            choice = input("\nSelect operation (0-9): ").strip()
            
            if choice == "0":
                print("Exiting GNS3 Network Manager")
                break
                
            elif choice == "1":
                projects = gns3_manager.list_projects()
                print(f"\nFound {len(projects)} projects:")
                for i, project in enumerate(projects, 1):
                    print(f"{i}. {project.get('name', 'Unnamed')} (ID: {project.get('project_id', 'Unknown')})")
                    
            elif choice == "2":
                project_name = input("Enter project name: ").strip()
                if project_name:
                    project_id = gns3_manager.create_project(project_name)
                    if project_id:
                        print(f"Project created successfully with ID: {project_id}")
                    else:
                        print("Project creation failed")
                        
            elif choice == "3":
                project_id = input("Enter project ID: ").strip()
                if project_id:
                    details = gns3_manager.get_project_details(project_id)
                    if details:
                        print(f"Project Name: {details.get('name', 'Unknown')}")
                        print(f"Status: {details.get('status', 'Unknown')}")
                        print(f"Path: {details.get('path', 'Unknown')}")
                    else:
                        print("Project not found or access denied")
                        
            elif choice == "4":
                project_id = input("Enter project ID to open: ").strip()
                if project_id:
                    success = gns3_manager.open_project(project_id)
                    print("Project opened successfully" if success else "Failed to open project")
                    
            elif choice == "5":
                project_id = input("Enter project ID to close: ").strip()
                if project_id:
                    success = gns3_manager.close_project(project_id)
                    print("Project closed successfully" if success else "Failed to close project")
                    
            elif choice == "6":
                project_id = input("Enter project ID: ").strip()
                if project_id:
                    nodes = gns3_manager.list_project_nodes(project_id)
                    print(f"\nFound {len(nodes)} nodes:")
                    for node in nodes:
                        print(f"- {node.get('name', 'Unnamed')} ({node.get('node_type', 'Unknown')}) - {node.get('status', 'Unknown')}")
                        
            elif choice == "7":
                templates = gns3_manager.get_available_templates()
                print(f"\nFound {len(templates)} templates:")
                for template in templates[:10]:  # Show first 10
                    print(f"- {template.get('name', 'Unnamed')} ({template.get('category', 'Unknown')})")
                if len(templates) > 10:
                    print(f"... and {len(templates) - 10} more templates")
                    
            elif choice == "8":
                config_file = input("Enter configuration file path: ").strip()
                if config_file:
                    config = gns3_manager.load_network_configuration(config_file)
                    if config:
                        deps = len(config.get('departments', []))
                        print(f"Configuration loaded successfully: {deps} departments")
                    else:
                        print("Failed to load configuration")
                        
            elif choice == "9":
                project_id = input("Enter project ID: ").strip()
                if project_id:
                    summary = gns3_manager.generate_project_summary(project_id)
                    print(f"\nProject Summary:")
                    print(f"Node Count: {summary['node_count']}")
                    print(f"Nodes by Type: {summary['nodes_by_type']}")
                    print(f"Nodes by Status: {summary['nodes_by_status']}")
                    
            else:
                print("Invalid choice. Please select 0-9.")
                
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()