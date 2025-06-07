#!/usr/bin/env python3
############################################################
# Fixed GNS3 Software Company Network Builder
# This version fixes indentation, error handling, and logic issues
############################################################

import requests
import yaml
import json
import time
import math
import os
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

class SoftwareCompanyNetworkBuilder:
    """
    Enhanced GNS3 Builder for Software Company Network
    Builds a complete corporate network with 10 departments
    """
    
    def __init__(self, 
                 config_file: str = "network_data.yml",
                 gns3_server: str = "http://127.0.0.1:3080",
                 project_id: str = None):
        """
        Initialize the network builder
        """
        self.config_file = config_file
        self.server = gns3_server
        self.session = requests.Session()
        self.session.auth = ('admin', 'admin')
        self.project_id = project_id
        self.project_name = "Software_Company_Network"
        self.templates = {}
        self.api_version = "v2"
        
        # Load or create network configuration
        self.load_or_create_config()
        
        # Track created nodes and links
        self.created_nodes = {}
        self.created_links = []
        
        # Port tracking for systematic connections
        self.router_ports = {}
        self.switch_ports = {}

    def load_or_create_config(self):
        """Load existing config or create based on your specifications"""
        try:
            with open(self.config_file, 'r') as file:
                self.config = yaml.safe_load(file)
            print(f"✓ Loaded configuration from {self.config_file}")
        except FileNotFoundError:
            print(f"⚠ Creating new configuration based on Software Company specs")
            self.config = self.create_software_company_config()
            self.save_config()

    def create_software_company_config(self) -> Dict[str, Any]:
        """Create configuration based on your Excel specifications"""
        return {
            "project_name": "Software_Company_Network",
            "topology": {
                "center_position": {"x": 0, "y": 0},
                "department_radius": 400,
                "device_radius": 120
            },
            "infrastructure": {
                "core_router": {
                    "name": "Core-Router-Main",
                    "template": "c7200",
                    "position": {"x": 0, "y": 0},
                    "model": "Cisco C7200"
                },
                "core_switch": {
                    "name": "Core-Switch-Main",
                    "template": "ethernet_switch",
                    "position": {"x": 0, "y": -150},
                    "model": "Cisco Catalyst 3560"
                },
                "internet_cloud": {
                    "name": "Internet-Cloud",
                    "template": "cloud",
                    "position": {"x": 0, "y": -300}
                }
            },
            "departments": [
                {
                    "name": "Development_Engineering",
                    "code": "A",
                    "vlan_id": 10,
                    "network": "192.168.10.0",
                    "devices": {
                        "router": 1,
                        "switch": 1,
                        "pc": 3,
                        "server": 1
                    }
                },
                {
                    "name": "IT_Network",
                    "code": "B", 
                    "vlan_id": 30,
                    "network": "192.168.30.0",
                    "devices": {
                        "router": 1,
                        "switch": 1, 
                        "pc": 3,
                        "printer": 1
                    }
                },
                {
                    "name": "Sales_Marketing",
                    "code": "C",
                    "vlan_id": 40,
                    "network": "192.168.40.0", 
                    "devices": {
                        "router": 1,
                        "switch": 1,
                        "pc": 2,
                        "printer": 1
                    }
                }
            ]
        }

    def save_config(self):
        """Save current configuration to YAML file"""
        try:
            with open(self.config_file, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False, indent=2)
            print(f"✓ Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Error saving config: {e}")

    def test_server_connection(self) -> bool:
        """Test connection to GNS3 server"""
        print(f"🔍 Testing connection to {self.server}...")
        
        endpoints = [
            "/v2/version",
            "/v3/version", 
            "/version"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.server}{endpoint}"
                print(f"  Trying: {url}")
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✓ GNS3 Server found!")
                        print(f"  Version: {data.get('version', 'Unknown')}")
                        
                        if "/v3/" in endpoint:
                            self.api_version = "v3"
                        else:
                            self.api_version = "v2"
                        return True
                    except:
                        print(f"  Response not JSON, but server responded")
                        return True
                        
            except requests.exceptions.RequestException as e:
                print(f"  Failed: {e}")
                continue
        
        print("❌ Cannot connect to GNS3 server")
        return False

    def connect_to_project(self) -> bool:
        """Connect to existing project or create new one"""
        if not self.test_server_connection():
            return False
        
        # If no project ID provided, create new project
        if not self.project_id:
            print("⚠ No project ID provided, creating new project...")
            return self.create_new_project()
            
        # Try to connect to existing project
        try:
            url = f"{self.server}/{self.api_version}/projects/{self.project_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                project_data = response.json()
                print(f"✓ Connected to existing project: {project_data.get('name', 'Unknown')}")
                return True
            elif response.status_code == 404:
                print("⚠ Project not found, creating new project...")
                return self.create_new_project()
            else:
                print(f"❌ Failed to connect: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            return False

    def create_new_project(self) -> bool:
        """Create a new GNS3 project"""
        url = f"{self.server}/{self.api_version}/projects"
        data = {"name": self.project_name}
        
        try:
            response = self.session.post(url, json=data)
            if response.status_code == 201:
                project_data = response.json()
                self.project_id = project_data["project_id"]
                print(f"✓ Created new project: {self.project_name}")
                print(f"  Project ID: {self.project_id}")
                return True
            else:
                print(f"❌ Failed to create project: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error creating project: {e}")
            return False

    def get_templates(self) -> bool:
        """Get available templates from GNS3"""
        url = f"{self.server}/{self.api_version}/templates"
        
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                templates = response.json()
                print(f"✓ Found {len(templates)} templates:")
                
                for template in templates:
                    template_name = template.get('name', '').lower()
                    template_id = template.get('template_id', template.get('id', ''))
                    self.templates[template_name] = template_id
                    print(f"  - {template.get('name', 'Unknown')} ({template_id})")
                    
                return True
            else:
                print(f"❌ Could not get templates: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error getting templates: {e}")
            return False

    def find_template_id(self, template_type: str) -> Optional[str]:
        """Find appropriate template ID for device type"""
        template_type = template_type.lower()
        print(f"🔍 Looking for template: {template_type}")
        
        # Direct match first
        if template_type in self.templates:
            print(f"  ✓ Direct match found: {self.templates[template_type]}")
            return self.templates[template_type]
        
        # Template mappings for different device types
        mappings = {
            'router': ['c7200', 'c3725', 'c2691', 'router', 'cisco'],
            'switch': ['ethernet_switch', 'switch', 'c3560', 'catalyst'],
            'cloud': ['cloud', 'nat'],
            'vpcs': ['vpcs', 'pc'],
            'server': ['server', 'qemu', 'ubuntu']
        }
        
        if template_type in mappings:
            for candidate in mappings[template_type]:
                for template_name, template_id in self.templates.items():
                    if candidate in template_name:
                        print(f"  ✓ Match found: {template_name} -> {template_id}")
                        return template_id
        
        # List available templates for debugging
        print(f"  ❌ No template found for {template_type}")
        print(f"  Available templates: {list(self.templates.keys())}")
        
        return None

    def create_node(self, name: str, template_type: str, x: int, y: int) -> Optional[str]:
        """Create a network node"""
        print(f"🔧 Creating node: {name} ({template_type})")
        
        template_id = self.find_template_id(template_type)
        if not template_id:
            print(f"❌ No template found for {template_type}")
            return None
        
        url = f"{self.server}/{self.api_version}/projects/{self.project_id}/nodes"
        data = {
            "name": name,
            "template_id": template_id,
            "x": x,
            "y": y
        }
            
        try:
            response = self.session.post(url, json=data)
            if response.status_code == 201:
                node_data = response.json()
                node_id = node_data["node_id"]
                
                self.created_nodes[name] = {
                    "node_id": node_id,
                    "name": name,
                    "type": template_type,
                    "position": {"x": x, "y": y}
                }
                
                print(f"✓ Created {template_type}: {name} ({node_id})")
                return node_id
            else:
                print(f"❌ Failed to create {name}: {response.status_code}")
                print(f"  Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error creating {name}: {e}")
            return None

    def create_link(self, node1_name: str, node1_port: int, 
                   node2_name: str, node2_port: int) -> Optional[str]:
        """Create link between two nodes"""
        print(f"🔗 Linking: {node1_name}:{node1_port} ↔ {node2_name}:{node2_port}")
        
        if node1_name not in self.created_nodes or node2_name not in self.created_nodes:
            print(f"❌ Cannot link - missing nodes: {node1_name}, {node2_name}")
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
            response = self.session.post(url, json=data)
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
                
                print(f"✓ Link created: {link_id}")
                return link_id
            else:
                print(f"❌ Failed to create link: {response.status_code}")
                print(f"  Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error creating link: {e}")
            return None

    def calculate_department_positions(self) -> Dict[str, Dict[str, Tuple[int, int]]]:
        """Calculate positions for all departments in circular layout"""
        positions = {}
        
        topo = self.config.get("topology", {})
        center_x = topo.get("center_position", {}).get("x", 0)
        center_y = topo.get("center_position", {}).get("y", 0)
        dept_radius = topo.get("department_radius", 400)
        device_radius = topo.get("device_radius", 120)
        
        departments = self.config.get("departments", [])
        num_depts = len(departments)
        
        for i, dept in enumerate(departments):
            # Calculate department center position
            angle = (2 * math.pi * i) / num_depts - (math.pi / 2)  # Start from top
            dept_x = center_x + int(dept_radius * math.cos(angle))
            dept_y = center_y + int(dept_radius * math.sin(angle))
            
            dept_name = dept["name"]
            positions[dept_name] = {}
            
            # Department switch position
            positions[dept_name]["switch"] = (dept_x, dept_y)
            
            # Calculate device positions around the switch
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

    def build_complete_network(self):
        """Build the complete software company network"""
        print(f"\n🚀 Building Software Company Network")
        print("=" * 60)
        
        # Step 1: Connect to project
        print("\n📋 Step 1: Connecting to GNS3 Project...")
        if not self.connect_to_project():
            raise Exception("Failed to connect to GNS3 project")
        
        # Step 2: Get templates
        print("\n📋 Step 2: Loading GNS3 Templates...")
        if not self.get_templates():
            raise Exception("Failed to get GNS3 templates")
        
        # Step 3: Calculate positions
        print("\n📋 Step 3: Calculating Device Positions...")
        dept_positions = self.calculate_department_positions()
        
        # Step 4: Create core infrastructure
        print(f"\n📋 Step 4: Creating Core Infrastructure...")
        infra = self.config.get("infrastructure", {})
        
        for device_key, device_config in infra.items():
            pos = device_config["position"]
            node_id = self.create_node(
                name=device_config["name"],
                template_type=device_config["template"],
                x=pos["x"],
                y=pos["y"]
            )
            
            if node_id:
                # Initialize port tracking
                self.router_ports[device_config["name"]] = 0
                self.switch_ports[device_config["name"]] = 0
            else:
                print(f"❌ Failed to create {device_config['name']}")
                return False
        
        # Step 5: Link core infrastructure
        print(f"\n📋 Step 5: Linking Core Infrastructure...")
        core_router = infra["core_router"]["name"]
        core_switch = infra["core_switch"]["name"] 
        internet = infra["internet_cloud"]["name"]
        
        # Link core router to core switch
        if self.create_link(core_router, 0, core_switch, 0):
            self.router_ports[core_router] = 1
            self.switch_ports[core_switch] = 1
        
        # Link core router to internet
        if self.create_link(core_router, 1, internet, 0):
            self.router_ports[core_router] = 2
        
        # Step 6: Build departments
        print(f"\n📋 Step 6: Building Departments...")
        departments = self.config.get("departments", [])
        
        for dept in departments:
            dept_name = dept["name"]
            dept_code = dept["code"]
            vlan_id = dept["vlan_id"]
            
            print(f"\n  📁 Building Department {dept_code}: {dept_name} (VLAN {vlan_id})")
            
            # Create department switch
            switch_name = f"SW-{dept_code}-{dept_name}"
            switch_pos = dept_positions[dept_name]["switch"]
            
            if self.create_node(
                name=switch_name,
                template_type="switch",
                x=switch_pos[0],
                y=switch_pos[1]
            ):
                self.switch_ports[switch_name] = 0
                
                # Link department switch to core router
                core_port = self.router_ports[core_router]
                if self.create_link(core_router, core_port, switch_name, 0):
                    self.router_ports[core_router] += 1
                    self.switch_ports[switch_name] = 1
            
            # Create department devices
            devices = dept.get("devices", {})
            device_positions = dept_positions[dept_name]["devices"]
            pos_index = 0
            
            # Create PCs
            for i in range(devices.get("pc", 0)):
                if pos_index < len(device_positions):
                    pc_name = f"PC-{dept_code}-{i+1:02d}"
                    pos = device_positions[pos_index]
                    
                    if self.create_node(
                        name=pc_name,
                        template_type="vpcs",
                        x=pos[0],
                        y=pos[1]
                    ):
                        # Link to department switch
                        switch_port = self.switch_ports[switch_name]
                        if self.create_link(switch_name, switch_port, pc_name, 0):
                            self.switch_ports[switch_name] += 1
                    pos_index += 1
            
            # Create Servers
            for i in range(devices.get("server", 0)):
                if pos_index < len(device_positions):
                    server_name = f"SRV-{dept_code}-{i+1:02d}"
                    pos = device_positions[pos_index]
                    
                    if self.create_node(
                        name=server_name,
                        template_type="server",
                        x=pos[0],
                        y=pos[1]
                    ):
                        # Link to department switch
                        switch_port = self.switch_ports[switch_name]
                        if self.create_link(switch_name, switch_port, server_name, 0):
                            self.switch_ports[switch_name] += 1
                    pos_index += 1
        
        # Step 7: Generate summary
        self.print_build_summary()
        
        return True

    def print_build_summary(self):
        """Print comprehensive build summary"""
        print(f"\n✅ Network Build Complete!")
        print("=" * 60)
        print(f"📊 Build Summary:")
        print(f"   • Project: {self.project_name}")
        print(f"   • Project ID: {self.project_id}")
        print(f"   • Total Nodes: {len(self.created_nodes)}")
        print(f"   • Total Links: {len(self.created_links)}")
        print(f"   • Departments: {len(self.config.get('departments', []))}")
        
        # Department breakdown
        print(f"\n🏢 Department Summary:")
        departments = self.config.get("departments", [])
        for dept in departments:
            devices = dept.get("devices", {})
            total_devices = sum(devices.values())
            print(f"   • {dept['code']}: {dept['name']} (VLAN {dept['vlan_id']}) - {total_devices} devices")
        
        # Node type breakdown
        node_types = {}
        for node_name, node_info in self.created_nodes.items():
            node_type = node_info["type"]
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        print(f"\n📋 Node Type Breakdown:")
        for node_type, count in node_types.items():
            print(f"   • {node_type.title()}: {count}")

    def list_available_projects(self):
        """List all available projects"""
        try:
            url = f"{self.server}/{self.api_version}/projects"
            response = self.session.get(url)
            
            if response.status_code == 200:
                projects = response.json()
                print(f"\n📋 Available Projects ({len(projects)}):")
                for project in projects:
                    print(f"   • {project.get('name', 'Unknown')} ({project.get('project_id', 'Unknown')})")
            else:
                print(f"❌ Could not list projects: {response.status_code}")
        except Exception as e:
            print(f"❌ Error listing projects: {e}")

def main():
    """Main execution function"""
    print("🌐 GNS3 Software Company Network Builder (Fixed Version)")
    print("=" * 70)
    
    try:
        # Initialize builder (no project ID = create new project)
        builder = SoftwareCompanyNetworkBuilder()
        
        # Show available projects for reference
        print("\n📋 Checking Available Projects:")
        builder.list_available_projects()
        
        # Build the complete network
        print(f"\n🚀 Starting Network Build Process...")
        success = builder.build_complete_network()
        
        if success:
            print(f"\n🎉 Network build completed successfully!")
            print(f"🔗 Access your project at: {builder.server}")
            print(f"📋 Project ID: {builder.project_id}")
            
            # Ask user if they want to start all nodes
            try:
                start_nodes = input(f"\n🚀 Start all network nodes? (y/n): ").lower().strip()
                if start_nodes in ['y', 'yes']:
                    # Add a simple start nodes function
                    print("🚀 Starting nodes...")
                    for node_name, node_info in builder.created_nodes.items():
                        node_id = node_info["node_id"]
                        url = f"{builder.server}/{builder.api_version}/projects/{builder.project_id}/nodes/{node_id}/start"
                        try:
                            response = builder.session.post(url)
                            if response.status_code == 204:
                                print(f"✓ Started: {node_name}")
                            else:
                                print(f"⚠ Could not start {node_name}: {response.status_code}")
                        except Exception as e:
                            print(f"❌ Error starting {node_name}: {e}")
            except (EOFError, KeyboardInterrupt):
                print("\n⚠ Skipping node startup")
            
            print(f"\n✅ All operations completed!")
            
        else:
            print(f"\n❌ Network build failed!")
            
    except KeyboardInterrupt:
        print(f"\n⚠ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        
        # Provide troubleshooting help
        print(f"\n🔧 Troubleshooting Tips:")
        print("1. Make sure GNS3 server is running")
        print("2. Check server URL: http://127.0.0.1:3080")
        print("3. Verify GNS3 templates are available")
        print("4. Check GNS3 server logs for errors")

if __name__ == "__main__":
    main()