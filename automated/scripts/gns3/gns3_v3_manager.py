#!/usr/bin/env python3
"""
GNS3 v3 API Project Manager
Complete solution for creating, managing, and working with GNS3 projects using v3 API
with proper authentication support.
"""

import requests
import json
import yaml
from typing import Dict, List, Optional
import time

class GNS3v3Manager:
    """
    Complete GNS3 v3 API manager with authentication and project management capabilities.
    """
    
    def __init__(self, server_url: str = "http://127.0.0.1:3080", username: str = "admin", password: str = "admin"):
        """
        Initialize GNS3 v3 manager with server connection and authentication.
        
        Args:
            server_url: GNS3 server URL
            username: GNS3 username for authentication
            password: GNS3 password for authentication
        """
        self.server = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification for local development
        self.auth_token = None
        
        # Authenticate with the server
        self.authenticate()
    
    def authenticate(self) -> bool:
        """
        Authenticate with GNS3 v3 API and obtain access token.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        print("🔐 Authenticating with GNS3 v3 API...")
        
        try:
            # Try to get authentication token from v3 API
            auth_url = f"{self.server}/v3/access/users/login"
            auth_data = {
                "username": self.username,
                "password": self.password
            }
            
            response = self.session.post(auth_url, json=auth_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token') or data.get('token')
                
                if self.auth_token:
                    # Set authorization header for future requests
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}',
                        'Content-Type': 'application/json'
                    })
                    print("✅ Authentication successful!")
                    return True
                else:
                    print("❌ No token received in response")
                    return False
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                print(f"Response: {response.text}")
                
                # Try basic auth as fallback
                print("🔄 Trying basic authentication...")
                self.session.auth = (self.username, self.password)
                return self.test_basic_auth()
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            # Try basic auth as fallback
            print("🔄 Trying basic authentication as fallback...")
            self.session.auth = (self.username, self.password)
            return self.test_basic_auth()
    
    def test_basic_auth(self) -> bool:
        """
        Test if basic authentication works with v3 API.
        
        Returns:
            bool: True if basic auth works, False otherwise
        """
        try:
            response = self.session.get(f"{self.server}/v3/version", timeout=5)
            if response.status_code == 200:
                print("✅ Basic authentication working!")
                return True
            else:
                print(f"❌ Basic auth failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Basic auth test error: {e}")
            return False
    
    def list_projects(self) -> List[Dict]:
        """
        List all projects on the GNS3 server.
        
        Returns:
            List of project dictionaries
        """
        print("📋 Fetching projects from GNS3 server...")
        
        try:
            response = self.session.get(f"{self.server}/v3/projects", timeout=10)
            
            if response.status_code == 200:
                projects = response.json()
                print(f"✅ Found {len(projects)} projects")
                
                for i, project in enumerate(projects, 1):
                    print(f"{i}. {project.get('name', 'Unnamed')} (ID: {project.get('project_id', 'Unknown')})")
                    print(f"   Status: {project.get('status', 'Unknown')}")
                    print(f"   Created: {project.get('created_at', 'Unknown')}")
                    print()
                
                return projects
            else:
                print(f"❌ Failed to list projects: {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error listing projects: {e}")
            return []
    
    def create_project(self, project_name: str) -> Optional[str]:
        """
        Create a new project on GNS3 server.
        
        Args:
            project_name: Name for the new project
            
        Returns:
            str: Project ID if successful, None if failed
        """
        print(f"🆕 Creating new project: {project_name}")
        
        try:
            project_data = {
                "name": project_name,
                "auto_close": True,
                "auto_open": False,
                "auto_start": False,
                "drawing_grid_size": 25,
                "grid_size": 75,
                "scene_height": 1000,
                "scene_width": 2000,
                "show_grid": False,
                "show_interface_labels": False,
                "show_layers": False,
                "snap_to_grid": False,
                "supplier": None,
                "variables": None,
                "zoom": 100
            }
            
            response = self.session.post(
                f"{self.server}/v3/projects", 
                json=project_data, 
                timeout=15
            )
            
            if response.status_code == 201:
                project = response.json()
                project_id = project.get('project_id')
                print(f"✅ Project created successfully!")
                print(f"   Project ID: {project_id}")
                print(f"   Project Name: {project.get('name')}")
                print(f"   Status: {project.get('status')}")
                return project_id
            else:
                print(f"❌ Failed to create project: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating project: {e}")
            return None
    
    def get_project_info(self, project_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific project.
        
        Args:
            project_id: ID of the project to query
            
        Returns:
            Dict: Project information or None if failed
        """
        print(f"🔍 Getting project information for ID: {project_id}")
        
        try:
            response = self.session.get(f"{self.server}/v3/projects/{project_id}", timeout=10)
            
            if response.status_code == 200:
                project = response.json()
                print(f"✅ Project found:")
                print(f"   Name: {project.get('name', 'Unknown')}")
                print(f"   Status: {project.get('status', 'Unknown')}")
                print(f"   Path: {project.get('path', 'Unknown')}")
                print(f"   Auto Start: {project.get('auto_start', False)}")
                print(f"   Auto Open: {project.get('auto_open', False)}")
                return project
            else:
                print(f"❌ Project not found: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting project info: {e}")
            return None
    
    def open_project(self, project_id: str) -> bool:
        """
        Open a project on the GNS3 server.
        
        Args:
            project_id: ID of the project to open
            
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"🔓 Opening project: {project_id}")
        
        try:
            response = self.session.post(f"{self.server}/v3/projects/{project_id}/open", timeout=15)
            
            if response.status_code == 201:
                print("✅ Project opened successfully!")
                return True
            else:
                print(f"❌ Failed to open project: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error opening project: {e}")
            return False
    
    def close_project(self, project_id: str) -> bool:
        """
        Close a project on the GNS3 server.
        
        Args:
            project_id: ID of the project to close
            
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"🔒 Closing project: {project_id}")
        
        try:
            response = self.session.post(f"{self.server}/v3/projects/{project_id}/close", timeout=15)
            
            if response.status_code == 204:
                print("✅ Project closed successfully!")
                return True
            else:
                print(f"❌ Failed to close project: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error closing project: {e}")
            return False
    
    def list_project_nodes(self, project_id: str) -> List[Dict]:
        """
        List all nodes (devices) in a project.
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of node dictionaries
        """
        print(f"🖥️  Listing nodes in project: {project_id}")
        
        try:
            response = self.session.get(f"{self.server}/v3/projects/{project_id}/nodes", timeout=10)
            
            if response.status_code == 200:
                nodes = response.json()
                print(f"✅ Found {len(nodes)} nodes")
                
                for i, node in enumerate(nodes, 1):
                    print(f"{i}. {node.get('name', 'Unnamed')} ({node.get('node_type', 'Unknown')})")
                    print(f"   Status: {node.get('status', 'Unknown')}")
                    print(f"   ID: {node.get('node_id', 'Unknown')}")
                    print()
                
                return nodes
            else:
                print(f"❌ Failed to list nodes: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error listing nodes: {e}")
            return []
    
    def get_templates(self) -> List[Dict]:
        """
        Get available device templates from the server.
        
        Returns:
            List of template dictionaries
        """
        print("📋 Fetching available templates...")
        
        try:
            response = self.session.get(f"{self.server}/v3/templates", timeout=10)
            
            if response.status_code == 200:
                templates = response.json()
                print(f"✅ Found {len(templates)} templates")
                
                # Group templates by category
                categories = {}
                for template in templates:
                    category = template.get('category', 'Other')
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(template)
                
                # Display templates by category
                for category, cat_templates in categories.items():
                    print(f"\n📁 {category}:")
                    for template in cat_templates:
                        print(f"   - {template.get('name', 'Unnamed')} ({template.get('template_type', 'Unknown')})")
                
                return templates
            else:
                print(f"❌ Failed to get templates: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting templates: {e}")
            return []
    
    def create_node(self, project_id: str, template_id: str, name: str, x: int = 0, y: int = 0) -> Optional[str]:
        """
        Create a new node in a project.
        
        Args:
            project_id: ID of the project
            template_id: ID of the template to use
            name: Name for the new node
            x: X coordinate for node placement
            y: Y coordinate for node placement
            
        Returns:
            str: Node ID if successful, None if failed
        """
        print(f"🖥️  Creating node '{name}' in project {project_id}")
        
        try:
            node_data = {
                "name": name,
                "template_id": template_id,
                "x": x,
                "y": y
            }
            
            response = self.session.post(
                f"{self.server}/v3/projects/{project_id}/templates/{template_id}",
                json=node_data,
                timeout=15
            )
            
            if response.status_code == 201:
                node = response.json()
                node_id = node.get('node_id')
                print(f"✅ Node created successfully!")
                print(f"   Node ID: {node_id}")
                print(f"   Node Name: {node.get('name')}")
                return node_id
            else:
                print(f"❌ Failed to create node: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating node: {e}")
            return None

def main():
    """
    Main function to demonstrate and test GNS3 v3 API functionality.
    """
    print("🚀 GNS3 v3 API Manager")
    print("=" * 50)
    
    # Initialize GNS3 manager
    gns3 = GNS3v3Manager()
    
    while True:
        print("\n🔧 Available Operations:")
        print("1. List all projects")
        print("2. Create new project")
        print("3. Get project information")
        print("4. Open project")
        print("5. Close project")
        print("6. List project nodes")
        print("7. Get available templates")
        print("8. Create node in project")
        print("0. Exit")
        
        try:
            choice = input("\n👉 Select operation (0-8): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
                
            elif choice == "1":
                gns3.list_projects()
                
            elif choice == "2":
                name = input("Enter project name: ").strip()
                if name:
                    project_id = gns3.create_project(name)
                    if project_id:
                        print(f"\n🎉 Success! New project ID: {project_id}")
                        print(f"💡 Save this ID for future use!")
                        
                        # Ask if user wants to open the new project
                        open_choice = input("Open this project now? (y/n): ").strip().lower()
                        if open_choice == 'y':
                            gns3.open_project(project_id)
                else:
                    print("❌ Project name required")
                    
            elif choice == "3":
                project_id = input("Enter project ID: ").strip()
                if project_id:
                    gns3.get_project_info(project_id)
                else:
                    print("❌ Project ID required")
                    
            elif choice == "4":
                project_id = input("Enter project ID to open: ").strip()
                if project_id:
                    gns3.open_project(project_id)
                else:
                    print("❌ Project ID required")
                    
            elif choice == "5":
                project_id = input("Enter project ID to close: ").strip()
                if project_id:
                    gns3.close_project(project_id)
                else:
                    print("❌ Project ID required")
                    
            elif choice == "6":
                project_id = input("Enter project ID: ").strip()
                if project_id:
                    gns3.list_project_nodes(project_id)
                else:
                    print("❌ Project ID required")
                    
            elif choice == "7":
                gns3.get_templates()
                
            elif choice == "8":
                project_id = input("Enter project ID: ").strip()
                template_id = input("Enter template ID: ").strip()
                node_name = input("Enter node name: ").strip()
                
                if project_id and template_id and node_name:
                    gns3.create_node(project_id, template_id, node_name)
                else:
                    print("❌ All fields required")
                    
            else:
                print("❌ Invalid choice")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\n⏸️  Press Enter to continue...")

if __name__ == "__main__":
    main()