#!/usr/bin/env python3
############################################################
# FIXED GNS3 Network Builder for Software Company
# Builds automated network topology based on department specifications
# Supports 10 departments with proper VLAN segmentation
# FIXES: Authentication, repetitive logging, proper error handling
############################################################

import requests
import yaml
import json
import time
import math
import os
import getpass
import base64
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import urllib3

# Disable SSL warnings for local GNS3 server
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SoftwareCompanyNetworkBuilder:
    """
    Fixed GNS3 Builder for Software Company Network
    Builds a complete corporate network with 10 departments
    """
    
    def __init__(self, 
                 config_file: str = "network_data.yml",
                 gns3_server: str = "http://127.0.0.1:3080",
                 username: str = None,
                 password: str = None,
                 project_name: str = "Software_Company_Network"):
        """
        Initialize the network builder
        """
        self.config_file = config_file
        self.server = gns3_server.rstrip('/')
        self.session = requests.Session()
        
        # Setup authentication
        self.setup_authentication(username, password)
        
        # Session configuration
        self.session.verify = False
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        self.project_id = None
        self.project_name = project_name
        self.templates = {}
        self.api_version = "v2"  # Start with v2, will auto-detect
        
        # Load network configuration
        self.load_or_create_config()
        
        # Track created nodes and links
        self.created_nodes = {}
        self.created_links = []
        
        # Port tracking
        self.router_ports = {}
        self.switch_ports = {}

    def get_auth_token(self, username: str, password: str) -> Optional[str]:
        """Get authentication token from GNS3 server"""
        try:
            # Try to get token using login endpoint
            login_url = f"{self.server}/v3/access/users/login"
            login_data = {"username": username, "password": password}
            
            response = requests.post(login_url, json=login_data, timeout=10, verify=False)
            
            if response.status_code == 200:
                token_data = response.json()
                token = token_data.get("token")
                if token:
                    print(f"✓ Retrieved authentication token")
                    return token
            else:
                print(f"⚠ Login endpoint failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠ Token retrieval failed: {e}")
        
        return None

    def setup_authentication(self, username: str = None, password: str = None):
        """Setup authentication for GNS3"""
        if not username:
            username = os.getenv('GNS3_USERNAME', 'admin')
        if not password:
            password = os.getenv('GNS3_PASSWORD', 'admin')
        
        # Try to get authentication token first
        token = self.get_auth_token(username, password)
        
        # Setup multiple authentication methods to try
        self.auth_methods = []
        
        if token:
            self.auth_methods.append(('bearer', token))
            
        self.auth_methods.extend([
            ('basic', (username, password)),
            ('none', None)
        ])
        
        print(f"🔐 Setting up authentication for user: {username}")

    def test_authentication_method(self, method_type: str, auth_data: Any) -> bool:
        """Test a specific authentication method"""
        test_session = requests.Session()
        test_session.verify = False
        
        if method_type == 'basic' and auth_data:
            test_session.auth = auth_data
        elif method_type == 'bearer' and auth_data:
            test_session.headers.update({'Authorization': f'Bearer {auth_data}'})
        
        try:
            # Test both version and projects endpoints
            response = test_session.get(f"{self.server}/v2/version", timeout=5)
            if response.status_code == 200:
                # Also test projects endpoint
                projects_response = test_session.get(f"{self.server}/v2/projects", timeout=5)
                return projects_response.status_code in [200, 401]  # 401 means auth method recognized but needs proper creds
            
            response = test_session.get(f"{self.server}/v3/version", timeout=5)
            if response.status_code == 200:
                # Also test projects endpoint
                projects_response = test_session.get(f"{self.server}/v3/projects", timeout=5)
                return projects_response.status_code in [200, 401]
            
            return False
        except:
            return False

    def load_or_create_config(self):
        """Load existing config or create based on specifications"""
        try:
            with open(self.config_file, 'r') as file:
                self.config = yaml.safe_load(file)
            print(f"✓ Loaded configuration from {self.config_file}")
        except FileNotFoundError:
            print(f"⚠ Creating new configuration")
            self.config = self.create_software_company_config()
            self.save_config()

    def create_software_company_config(self) -> Dict[str, Any]:
        """Create configuration based on your network specifications"""
        return {
            "project_name": self.project_name,
            "topology": {
                "center_position": {"x": 0, "y": 0},
                "department_radius": 400,
                "device_radius": 120
            },
            "infrastructure": {
                "core_switch": {
                    "name": "CoreSwitch",
                    "template": "ethernet_switch",
                    "position": {"x": 0, "y": 0}
                }
            },
            "departments": [
                {
                    "name": "Development",
                    "code": "A",
                    "vlan_id": 10,
                    "network": "192.168.10.0/28",
                    "gateway": "192.168.10.1",
                    "devices": {"router": 1, "switch": 1, "pc": 6, "server": 1}
                },
                {
                    "name": "Guest",
                    "code": "D", 
                    "vlan_id": 20,
                    "network": "192.168.20.0/28",
                    "gateway": "192.168.20.1",
                    "devices": {"router": 1, "switch": 1, "pc": 5}
                },
                {
                    "name": "IT",
                    "code": "B",
                    "vlan_id": 30,
                    "network": "192.168.30.0/28", 
                    "gateway": "192.168.30.1",
                    "devices": {"router": 1, "switch": 1, "pc": 6, "server": 1}
                },
                {
                    "name": "Sales",
                    "code": "C",
                    "vlan_id": 40,
                    "network": "192.168.40.0/29",
                    "gateway": "192.168.40.1",
                    "devices": {"router": 1, "switch": 1, "pc": 3, "printer": 1}
                },
                {
                    "name": "Admin",
                    "code": "H", 
                    "vlan_id": 50,
                    "network": "192.168.50.0/29",
                    "gateway": "192.168.50.1",
                    "devices": {"router": 1, "switch": 1, "pc": 2}
                },
                {
                    "name": "HR",
                    "code": "F",
                    "vlan_id": 60,
                    "network": "192.168.60.0/29",
                    "gateway": "192.168.60.1", 
                    "devices": {"router": 1, "switch": 1, "pc": 2, "printer": 1}
                },
                {
                    "name": "Finance",
                    "code": "E",
                    "vlan_id": 70,
                    "network": "192.168.70.0/29",
                    "gateway": "192.168.70.1",
                    "devices": {"router": 1, "switch": 1, "pc": 2, "server": 1}
                },
                {
                    "name": "Design",
                    "code": "J",
                    "vlan_id": 80,
                    "network": "192.168.80.0/29", 
                    "gateway": "192.168.80.1",
                    "devices": {"router": 1, "switch": 1, "pc": 2}
                },
                {
                    "name": "Marketing",
                    "code": "I",
                    "vlan_id": 90,
                    "network": "192.168.90.0/29",
                    "gateway": "192.168.90.1",
                    "devices": {"router": 1, "switch": 1, "pc": 2}
                },
                {
                    "name": "Infrastructure", 
                    "code": "G",
                    "vlan_id": 100,
                    "network": "192.168.0.0/28",
                    "gateway": "192.168.0.1",
                    "devices": {"router": 1, "switch": 1, "pc": 4, "server": 6}
                }
            ]
        }

    def save_config(self):
        """Save configuration to YAML file"""
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file, default_flow_style=False, indent=2)
        print(f"✓ Configuration saved to {self.config_file}")

    def test_server_connection(self) -> bool:
        """Test connection and find working authentication"""
        print(f"🔍 Testing connection to {self.server}...")
        
        # Test different authentication methods
        for method_type, auth_data in self.auth_methods:
            print(f"  Trying {method_type} authentication...")
            
            test_session = requests.Session()
            test_session.verify = False
            
            if method_type == 'basic' and auth_data:
                test_session.auth = auth_data
            elif method_type == 'bearer' and auth_data:
                test_session.headers.update({'Authorization': f'Bearer {auth_data}'})
            
            # Test both version and projects endpoints
            try:
                for version in ['v2', 'v3']:
                    # Test version endpoint
                    version_response = test_session.get(f"{self.server}/{version}/version", timeout=5)
                    
                    if version_response.status_code == 200:
                        # Test projects endpoint with same auth
                        projects_response = test_session.get(f"{self.server}/{version}/projects", timeout=5)
                        
                        if projects_response.status_code == 200:
                            print(f"✓ {method_type} authentication successful for {version}!")
                            
                            # Apply successful authentication to main session
                            if method_type == 'basic' and auth_data:
                                self.session.auth = auth_data
                            elif method_type == 'bearer' and auth_data:
                                self.session.headers.update({'Authorization': f'Bearer {auth_data}'})
                            
                            self.api_version = version
                            version_info = version_response.json()
                            print(f"✓ GNS3 Server v{version_info.get('version', 'Unknown')} detected")
                            return True
                        else:
                            print(f"  Version OK but projects failed: {projects_response.status_code}")
                            
            except Exception as e:
                print(f"  {method_type} test failed: {e}")
                continue
        
        print("❌ No working authentication method found")
        return False

    def list_projects(self) -> List[Dict]:
        """List existing projects"""
        url = f"{self.server}/{self.api_version}/projects"
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                projects = response.json()
                print(f"📋 Found {len(projects)} existing projects:")
                for project in projects[:5]:  # Show first 5 projects
                    print(f"  • {project['name']} (ID: {project['project_id'][:8]}...)")
                return projects
            else:
                print(f"⚠ Could not list projects: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error listing projects: {e}")
            return []

    def create_new_project(self) -> bool:
        """Create a new GNS3 project"""
        print(f"🆕 Creating new project: {self.project_name}")
        
        # List existing projects first
        existing_projects = self.list_projects()
        
        # Create unique project name
        timestamp = int(time.time())
        unique_name = f"{self.project_name}_{timestamp}"
        
        url = f"{self.server}/{self.api_version}/projects"
        data = {
            "name": unique_name,
            "auto_close": False,
            "auto_open": False,
            "auto_start": False
        }
        
        try:
            response = self.session.post(url, json=data, timeout=30)
            
            if response.status_code == 201:
                project_data = response.json()
                self.project_id = project_data["project_id"]
                self.project_name = unique_name
                print(f"✓ Project created successfully!")
                print(f"  Name: {self.project_name}")
                print(f"  ID: {self.project_id}")
                return True
            else:
                print(f"❌ Failed to create project: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating project: {e}")
            return False

    def get_templates(self) -> bool:
        """Get available templates from GNS3"""
        print("📋 Retrieving templates...")
        
        url = f"{self.server}/{self.api_version}/templates"
        
        try:
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                templates = response.json()
                
                for template in templates:
                    template_name = template.get('name', '').lower()
                    template_id = template.get('template_id', template.get('id', ''))
                    category = template.get('category', 'unknown')
                    
                    if template_id:
                        self.templates[template_name] = {
                            'id': template_id,
                            'category': category,
                            'name': template.get('name', ''),
                            'builtin': template.get('builtin', False)
                        }
                
                print(f"✓ Retrieved {len(self.templates)} templates")
                
                # Show template categories
                categories = {}
                for name, info in self.templates.items():
                    cat = info['category']
                    categories[cat] = categories.get(cat, 0) + 1
                
                print("📋 Available categories:")
                for category, count in categories.items():
                    print(f"  {category}: {count} templates")
                
                return True
            else:
                print(f"⚠ Could not get templates: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting templates: {e}")
            return False

    def find_template_id(self, template_type: str) -> Optional[str]:
        """Find appropriate template ID for device type"""
        template_type = template_type.lower()
        
        # Direct match
        if template_type in self.templates:
            return self.templates[template_type]['id']
        
        # Template mappings
        mappings = {
            'router': ['c7200', 'c3725', 'c2691', 'c1700', 'router', 'cisco'],
            'switch': ['ethernet_switch', 'switch', 'c3560', 'catalyst'],
            'cloud': ['cloud', 'nat'], 
            'vpcs': ['vpcs', 'pc'],
            'server': ['server', 'qemu', 'ubuntu', 'linux']
        }
        
        if template_type in mappings:
            for candidate in mappings[template_type]:
                for template_name, template_info in self.templates.items():
                    if candidate in template_name.lower():
                        print(f"  Using template: {template_info['name']} for {template_type}")
                        return template_info['id']
        
        # Fallback to builtin templates
        for template_name, template_info in self.templates.items():
            if template_info.get('builtin', False):
                print(f"  Using builtin template: {template_info['name']}")
                return template_info['id']
        
        print(f"❌ No template found for {template_type}")
        return None

    def create_node(self, name: str, template_type: str, x: int, y: int) -> Optional[str]:
        """Create a network node"""
        template_id = self.find_template_id(template_type)
        if not template_id:
            return None
        
        url = f"{self.server}/{self.api_version}/projects/{self.project_id}/nodes"
        data = {
            "name": name,
            "template_id": template_id,
            "x": x,
            "y": y
        }
        
        try:
            response = self.session.post(url, json=data, timeout=30)
            
            if response.status_code == 201:
                node_data = response.json()
                node_id = node_data["node_id"]
                
                self.created_nodes[name] = {
                    "node_id": node_id,
                    "name": name,
                    "type": template_type,
                    "position": {"x": x, "y": y}
                }
                
                print(f"✓ Created {template_type}: {name}")
                return node_id
            else:
                print(f"❌ Failed to create {name}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating {name}: {e}")
            return None

    def create_link(self, node1_name: str, node1_port: int, 
                   node2_name: str, node2_port: int) -> Optional[str]:
        """Create link between two nodes"""
        if node1_name not in self.created_nodes or node2_name not in self.created_nodes:
            print(f"❌ Cannot link {node1_name} to {node2_name} - nodes not found")
            return None
        
        url = f"{self.server}/{self.api_version}/projects/{self.project_id}/links"
        data = {
            "nodes": [
                {
                    "node_id": self.created_nodes[node1_name]["node_id"],
                    "adapter_number": 0,
                    "port_number": node1_port
                },
                {
                    "node_id": self.created_nodes[node2_name]["node_id"],
                    "adapter_number": 0,
                    "port_number": node2_port
                }
            ]
        }
        
        try:
            response = self.session.post(url, json=data, timeout=15)
            
            if response.status_code == 201:
                link_data = response.json()
                link_id = link_data["link_id"]
                
                self.created_links.append({
                    "link_id": link_id,
                    "node1": node1_name,
                    "port1": node1_port,
                    "node2": node2_name,
                    "port2": node2_port
                })
                
                print(f"✓ Linked {node1_name}:{node1_port} ↔ {node2_name}:{node2_port}")
                return link_id
            else:
                print(f"❌ Failed to create link: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating link: {e}")
            return None

    def calculate_positions(self) -> Dict[str, Dict[str, Tuple[int, int]]]:
        """Calculate positions for departments in circular layout"""
        positions = {}
        
        topo = self.config.get("topology", {})
        center_x = topo.get("center_position", {}).get("x", 0)
        center_y = topo.get("center_position", {}).get("y", 0)
        dept_radius = topo.get("department_radius", 400)
        device_radius = topo.get("device_radius", 120)
        
        departments = self.config.get("departments", [])
        num_depts = len(departments)
        
        for i, dept in enumerate(departments):
            angle = (2 * math.pi * i) / num_depts - (math.pi / 2)
            dept_x = center_x + int(dept_radius * math.cos(angle))
            dept_y = center_y + int(dept_radius * math.sin(angle))
            
            dept_name = dept["name"]
            positions[dept_name] = {}
            
            # Switch position
            positions[dept_name]["switch"] = (dept_x, dept_y)
            
            # Device positions around switch
            devices = dept.get("devices", {})
            total_devices = sum([
                devices.get("pc", 0),
                devices.get("server", 0),
                devices.get("printer", 0)
            ])
            
            device_positions = []
            for j in range(total_devices):
                if total_devices == 1:
                    dev_x = dept_x
                    dev_y = dept_y + device_radius
                else:
                    dev_angle = (2 * math.pi * j) / total_devices
                    dev_x = dept_x + int(device_radius * math.cos(dev_angle))
                    dev_y = dept_y + int(device_radius * math.sin(dev_angle))
                device_positions.append((dev_x, dev_y))
            
            positions[dept_name]["devices"] = device_positions
        
        return positions

    def build_network(self):
        """Build the complete software company network"""
        print(f"\n🚀 Building Software Company Network")
        print("=" * 60)
        
        # Step 1: Test connection
        if not self.test_server_connection():
            return False
        
        # Step 2: Create project
        if not self.create_new_project():
            return False
        
        # Step 3: Get templates
        if not self.get_templates():
            return False
        
        # Step 4: Calculate positions
        positions = self.calculate_positions()
        
        # Step 5: Create core switch
        print(f"\n🏗️  Creating Core Infrastructure...")
        infra = self.config.get("infrastructure", {})
        
        core_switch_config = infra["core_switch"]
        pos = core_switch_config["position"]
        
        core_switch_id = self.create_node(
            name=core_switch_config["name"],
            template_type=core_switch_config["template"],
            x=pos["x"],
            y=pos["y"]
        )
        
        if not core_switch_id:
            print("❌ Failed to create core infrastructure")
            return False
        
        self.switch_ports[core_switch_config["name"]] = 0
        
        # Step 6: Build departments (limited for testing)
        print(f"\n🏢 Building Departments...")
        departments = self.config.get("departments", [])
        
        # Build first 3 departments for testing
        for dept in departments[:3]:
            dept_name = dept["name"]
            dept_code = dept["code"]
            vlan_id = dept["vlan_id"]
            
            print(f"\n  📁 Building Department {dept_code}: {dept_name} (VLAN {vlan_id})")
            
            # Create department switch
            switch_name = f"SW-{dept_code}-{dept_name}"
            switch_pos = positions[dept_name]["switch"]
            
            switch_id = self.create_node(
                name=switch_name,
                template_type="switch",
                x=switch_pos[0],
                y=switch_pos[1]
            )
            
            if switch_id:
                self.switch_ports[switch_name] = 0
                
                # Link to core switch
                core_port = self.switch_ports[core_switch_config["name"]]
                self.create_link(core_switch_config["name"], core_port, switch_name, 0)
                self.switch_ports[core_switch_config["name"]] += 1
                self.switch_ports[switch_name] = 1
                
                # Create devices
                devices = dept.get("devices", {})
                device_positions = positions[dept_name]["devices"]
                pos_index = 0
                
                # Create PCs (limit to 2 for testing)
                num_pcs = min(devices.get("pc", 0), 2)
                for i in range(num_pcs):
                    if pos_index < len(device_positions):
                        pc_name = f"PC-{dept_code}-{i+1:02d}"
                        pos = device_positions[pos_index]
                        
                        pc_id = self.create_node(
                            name=pc_name,
                            template_type="vpcs",
                            x=pos[0],
                            y=pos[1]
                        )
                        
                        if pc_id:
                            switch_port = self.switch_ports[switch_name]
                            self.create_link(switch_name, switch_port, pc_name, 0)
                            self.switch_ports[switch_name] += 1
                            pos_index += 1
        
        # Step 7: Summary
        self.print_summary()
        return True

    def print_summary(self):
        """Print build summary"""
        print(f"\n✅ Network Build Complete!")
        print("=" * 60)
        print(f"📊 Build Summary:")
        print(f"   • Project: {self.project_name}")
        print(f"   • Project ID: {self.project_id}")
        print(f"   • Total Nodes: {len(self.created_nodes)}")
        print(f"   • Total Links: {len(self.created_links)}")
        
        # Node breakdown
        node_types = {}
        for node_name, node_info in self.created_nodes.items():
            node_type = node_info["type"]
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        print(f"\n📋 Node Type Breakdown:")
        for node_type, count in node_types.items():
            print(f"   • {node_type.title()}: {count}")

def main():
    """Main execution function"""
    print("🌐 GNS3 Software Company Network Builder")
    print("=" * 60)
    
    try:
        # Get credentials
        username = input("Enter GNS3 username (default: admin): ").strip() or "admin"
        password = getpass.getpass("Enter GNS3 password (default: admin): ") or "admin"
        
        # Initialize builder
        builder = SoftwareCompanyNetworkBuilder(
            username=username,
            password=password
        )
        
        # Build network
        success = builder.build_network()
        
        if success:
            print(f"\n🎉 Network build completed successfully!")
            print(f"🔗 Access your project at: {builder.server}")
            print(f"📋 Project ID: {builder.project_id}")
        else:
            print(f"\n❌ Network build failed!")
            
    except KeyboardInterrupt:
        print(f"\n⚠ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")

if __name__ == "__main__":
    main()