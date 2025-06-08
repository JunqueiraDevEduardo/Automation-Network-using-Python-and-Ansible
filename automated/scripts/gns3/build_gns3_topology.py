#!/usr/bin/env python3
############################################################
# Enhanced GNS3 Small Network Builder for Software Company excel file
# Builds automated network topology based on department specifications
# Supports 10 departments with proper VLAN segmentation
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
                 project_id: str = "9a8ab49a-6f61-4fa8-9089-99e6c6594e4f"):
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
                "department_radius": 500,
                "device_radius": 180
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
                    "subnet_mask": "255.255.255.240",
                    "gateway": "192.168.10.1",
                    "first_host": "192.168.10.1",
                    "last_host": "192.168.10.14",
                    "broadcast": "192.168.10.15",
                    "max_hosts": 14,
                    "real_hosts": 9,
                    "devices": {
                        "router": 1,
                        "switch": 1,
                        "pc": 6,
                        "printer": 0,
                        "server": 1
                    },
                    "color": "#FF6B6B"
                },
                {
                    "name": "IT_Network",
                    "code": "B", 
                    "vlan_id": 30,
                    "network": "192.168.30.0",
                    "subnet_mask": "255.255.255.240",
                    "gateway": "192.168.30.1",
                    "first_host": "192.168.30.1",
                    "last_host": "192.168.30.14",
                    "broadcast": "192.168.30.15",
                    "max_hosts": 14,
                    "real_hosts": 9,
                    "devices": {
                        "router": 1,
                        "switch": 1, 
                        "pc": 6,
                        "printer": 1,
                        "server": 0
                    },
                    "color": "#4ECDC4"
                },
                {
                    "name": "Sales_Marketing",
                    "code": "C",
                    "vlan_id": 40,
                    "network": "192.168.40.0", 
                    "subnet_mask": "255.255.255.240",
                    "gateway": "192.168.40.1",
                    "first_host": "192.168.40.1",
                    "last_host": "192.168.40.14",
                    "broadcast": "192.168.40.15",
                    "max_hosts": 14,
                    "real_hosts": 6,
                    "devices": {
                        "router": 1,
                        "switch": 1,
                        "pc": 3,
                        "printer": 1,
                        "server": 0
                    },
                    "color": "#45B7D1"
                },
                {
                    "name": "Guest_Network",
                    "code": "D",
                    "vlan_id": 20,
                    "network": "192.168.20.0",
                    "subnet_mask": "255.255.255.240", 
                    "gateway": "192.168.20.1",
                    "first_host": "192.168.20.1",
                    "last_host": "192.168.20.14",
                    "broadcast": "192.168.20.15",
                    "max_hosts": 14,
                    "real_hosts": 7,
                    "devices": {
                        "router": 1,
                        "switch": 1,
                        "pc": 5,
                        "printer": 0,
                        "server": 0
                    },
                    "color": "#96CEB4"
                },
                {
                    "name": "Accounts_Finance",
                    "code": "E",
                    "vlan_id": 70,
                    "network": "192.168.70.0",
                    "subnet_mask": "255.255.255.240",
                    "gateway": "192.168.70.1", 
                    "first_host": "192.168.70.1",
                    "last_host": "192.168.70.14",
                    "broadcast": "192.168.70.15",
                    "max_hosts": 14,
                    "real_hosts": 5,
                    "devices": {
                        "router": 1,
                        "switch": 1,
                        "pc": 2,
                        "printer": 1,
                        "server": 0
                    },
                    "color": "#FFEAA7"
                },
                {
                    "name": "Human_Resources",
                    "code": "F",
                    "vlan_id": 60,
                    "network": "192.168.60.0",
                    "subnet_mask": "255.255.255.248",
                    "gateway": "192.168.60.1",
                    "first_host": "192.168.60.1", 
                    "last_host": "192.168.60.6",
                    "broadcast": "192.168.60.7",
                    "max_hosts": 14,
                    "real_hosts": 5,
                    "devices": {
                        "router": 1,
                        "switch": 1,
                        "pc": 2,
                        "printer": 0,
                        "server": 0
                    },
                    "color": "#DDA0DD"
                },
                {
                    "name": "Infrastructure_Security",
                    "code": "G",
                    "vlan_id": 0,
                    "network": "192.168.0.0",
                    "subnet_mask": "255.255.255.240",
                    "gateway": "192.168.0.1",
                    "first_host": "192.168.0.1",
                    "last_host": "192.168.0.14",
                    "broadcast": "192.168.0.15",
                    "max_hosts": 14,
                    "real_hosts": 12,
                    "devices": {
                        "router": 1,
                        "switch": 1,
                        "pc": 4,
                        "printer": 0,
                        "server": 6
                    },
                    "color": "#FF7675"
                },
                {
                    "name": "Admin_Department",
                    "code": "H",
                    "vlan_id": 50,
                    "network": "192.168.50.0",
                    "subnet_mask": "255.255.255.248",
                    "gateway": "192.168.50.1",
                    "first_host": "192.168.50.1",
                    "last_host": "192.168.50.6",
                    "broadcast": "192.168.50.7",
                    "max_hosts": 14,
                    "real_hosts": 4,
                    "devices": {
                        "router": 1,
                        "switch": 1,
                        "pc": 2,
                        "printer": 0,
                        "server": 0
                    },
                    "color": "#A29BFE"
                },
                {
                    "name": "Marketing_Department",
                    "code": "I", 
                    "vlan_id": 90,
                    "network": "192.168.90.0",
                    "subnet_mask": "255.255.255.240",
                    "gateway": "192.168.90.1",
                    "first_host": "192.168.90.1",
                    "last_host": "192.168.90.14",
                    "broadcast": "192.168.90.15",
                    "max_hosts": 14,
                    "real_hosts": 4,
                    "devices": {
                        "router": 1,
                        "switch": 1,
                        "pc": 2,
                        "printer": 0,
                        "server": 0
                    },
                    "color": "#6C5CE7"
                },
                {
                    "name": "Design_Department",
                    "code": "J",
                    "vlan_id": 80,
                    "network": "192.168.80.0",
                    "subnet_mask": "255.255.255.248",
                    "gateway": "192.168.80.1",
                    "first_host": "192.168.80.1",
                    "last_host": "192.168.80.6",
                    "broadcast": "192.168.80.7",
                    "max_hosts": 14,
                    "real_hosts": 4,
                    "devices": {
                        "router": 1,
                        "switch": 1,
                        "pc": 2,
                        "printer": 0,
                        "server": 0
                    },
                    "color": "#00B894"
                }
            ]
        }

    def save_config(self):
        """Save current configuration to YAML file"""
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file, default_flow_style=False, indent=2)
        print(f"✓ Configuration saved to {self.config_file}")

    def test_server_connection(self) -> bool:
        """Test connection to GNS3 server"""
        print(f"🔍 Testing connection to {self.server}...")
        
        endpoints = [
            "/v2/version",
            "/v3/version", 
            "/version",
            "/static/web-ui/server/version"
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.server}{endpoint}"
                response = self.session.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"✓ GNS3 Server accessible at {endpoint}")
                    if "/v3/" in endpoint:
                        self.api_version = "v3"
                    else:
                        self.api_version = "v2"
                    return True
                    
            except requests.exceptions.RequestException:
                continue
        
        print("❌ Cannot connect to GNS3 server")
        return False

    def connect_to_project(self) -> bool:
        """Connect to existing project or create new one"""
        if not self.test_server_connection():
            return False
            
        # Try to connect to existing project
        try:
            url = f"{self.server}/{self.api_version}/projects/{self.project_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                print(f"✓ Connected to existing project: {self.project_id}")
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
                print(f"❌ Failed to create project: {response.text}")
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
                for template in templates:
                    template_name = template.get('name', '').lower()
                    template_id = template.get('template_id', template.get('id', ''))
                    self.templates[template_name] = template_id
                    
                print(f"✓ Retrieved {len(self.templates)} templates")
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
                        return template_id
        
        # Fallback to first available template
        if self.templates:
            return list(self.templates.values())[0]
            
        return None

    def create_node(self, name: str, template_type: str, x: int, y: int, 
                   symbol: str = None) -> Optional[str]:
        """Create a network node"""
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
        
        if symbol:
            data["symbol"] = symbol
            
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
                
                print(f"✓ Created {template_type}: {name}")
                return node_id
            else:
                print(f"❌ Failed to create {name}: {response.text}")
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
                
                print(f"✓ Linked {node1_name}:{node1_port} ↔ {node2_name}:{node2_port}")
                return link_id
            else:
                print(f"❌ Failed to create link: {response.text}")
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
        dept_radius = topo.get("department_radius", 500)
        device_radius = topo.get("device_radius", 180)
        
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
        if not self.connect_to_project():
            raise Exception("Failed to connect to GNS3 project")
        
        # Step 2: Get templates
        if not self.get_templates():
            raise Exception("Failed to get GNS3 templates")
        
        # Step 3: Calculate positions
        dept_positions = self.calculate_department_positions()
        
        # Step 4: Create core infrastructure
        print(f"\n🏗️  Creating Core Infrastructure...")
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
        
        # Step 5: Link core infrastructure
        print(f"\n🔗 Linking Core Infrastructure...")
        core_router = infra["core_router"]["name"]
        core_switch = infra["core_switch"]["name"] 
        internet = infra["internet_cloud"]["name"]
        
        # Link core router to core switch
        self.create_link(core_router, 0, core_switch, 0)
        self.router_ports[core_router] = 1
        self.switch_ports[core_switch] = 1
        
        # Link core router to internet
        self.create_link(core_router, 1, internet, 0)
        self.router_ports[core_router] = 2
        
        # Step 6: Build departments
        print(f"\n🏢 Building Departments...")
        departments = self.config.get("departments", [])
        
        for dept in departments:
            dept_name = dept["name"]
            dept_code = dept["code"]
            vlan_id = dept["vlan_id"]
            
            print(f"\n  📁 Building Department {dept_code}: {dept_name} (VLAN {vlan_id})")
            
            # Create department switch
            switch_name = f"SW-{dept_code}-{dept_name}"
            switch_pos = dept_positions[dept_name]["switch"]
            
            self.create_node(
                name=switch_name,
                template_type="switch",
                x=switch_pos[0],
                y=switch_pos[1]
            )
            
            self.switch_ports[switch_name] = 0
            
            # Link department switch to core router
            core_port = self.router_ports[core_router]
            self.create_link(core_router, core_port, switch_name, 0)
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
                    
                    self.create_node(
                        name=pc_name,
                        template_type="vpcs",
                        x=pos[0],
                        y=pos[1]
                    )
                    
                    # Link to department switch
                    switch_port = self.switch_ports[switch_name]
                    self.create_link(switch_name, switch_port, pc_name, 0)
                    self.switch_ports[switch_name] += 1
                    pos_index += 1
            
            # Create Servers
            for i in range(devices.get("server", 0)):
                if pos_index < len(device_positions):
                    server_name = f"SRV-{dept_code}-{i+1:02d}"
                    pos = device_positions[pos_index]
                    
                    self.create_node(
                        name=server_name,
                        template_type="server",
                        x=pos[0],
                        y=pos[1]
                    )
                    
                    # Link to department switch
                    switch_port = self.switch_ports[switch_name]
                    self.create_link(switch_name, switch_port, server_name, 0)
                    self.switch_ports[switch_name] += 1
                    pos_index += 1
            
            # Create Printers
            for i in range(devices.get("printer", 0)):
                if pos_index < len(device_positions):
                    printer_name = f"PRT-{dept_code}-{i+1:02d}"
                    pos = device_positions[pos_index]
                    
                    self.create_node(
                        name=printer_name,
                        template_type="vpcs",  # Using VPCS for printers
                        x=pos[0],
                        y=pos[1]
                    )
                    
                    # Link to department switch
                    switch_port = self.switch_ports[switch_name]
                    self.create_link(switch_name, switch_port, printer_name, 0)
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
def export_network_documentation(self):
        """Export network documentation"""
        doc_content = f"""# Software Company Network Documentation
Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}
Project: {self.project_name}
Project ID: {self.project_id}

## Network Overview
This network represents a complete software company infrastructure with 10 departments,
each properly segmented using VLANs and appropriate IP addressing schemes.

## Department Summary
"""
        
        departments = self.config.get("departments", [])
        for dept in departments:
            devices = dept.get("devices", {})
            doc_content += f"""
### {dept['code']}. {dept['name']}
- VLAN ID: {dept['vlan_id']}
- Network: {dept['network']}/{dept['subnet_mask']}
- Gateway: {dept['gateway']}
- Max Hosts: {dept['max_hosts']}
- Real Hosts: {dept['real_hosts']}
- Devices: {devices}
"""
        
        doc_content += f"""
## Created Nodes ({len(self.created_nodes)} total)
"""
        
        # Group nodes by type for better documentation
        node_types = {}
        for node_name, node_info in self.created_nodes.items():
            node_type = node_info["type"]
            if node_type not in node_types:
                node_types[node_type] = []
            node_types[node_type].append(node_name)
        
        for node_type, nodes in node_types.items():
            doc_content += f"""
### {node_type.title()} Nodes ({len(nodes)}):
"""
            for node in nodes:
                node_info = self.created_nodes[node]
                pos = node_info["position"]
                doc_content += f"- {node} (Position: {pos['x']}, {pos['y']})\n"
        
        doc_content += f"""
## Network Links ({len(self.created_links)} total)
"""
        
        for i, link in enumerate(self.created_links, 1):
            doc_content += f"""
### Link {i}:
- Connection: {link['node1']}:{link['port1']} ↔ {link['node2']}:{link['port2']}
- Link ID: {link['link_id']}
"""
        
        doc_content += f"""
## Network Architecture Details

### Core Infrastructure
- **Core Router**: Central routing device connecting all departments
- **Core Switch**: Main switching infrastructure
- **Internet Cloud**: External connectivity simulation

### Department Structure
Each department follows a standardized structure:
- Department Switch: Connects to core router
- End Devices: PCs, Servers, Printers connected to department switch
- VLAN Segmentation: Each department has its own VLAN for security

### IP Addressing Scheme
- Development Engineering: 192.168.10.0/28 (VLAN 10)
- Guest Network: 192.168.20.0/28 (VLAN 20)  
- IT Network: 192.168.30.0/28 (VLAN 30)
- Sales Marketing: 192.168.40.0/28 (VLAN 40)
- Admin Department: 192.168.50.0/29 (VLAN 50)
- Human Resources: 192.168.60.0/29 (VLAN 60)
- Accounts Finance: 192.168.70.0/28 (VLAN 70)
- Design Department: 192.168.80.0/29 (VLAN 80)
- Marketing Department: 192.168.90.0/28 (VLAN 90)
- Infrastructure Security: 192.168.0.0/28 (VLAN 0)

### Security Considerations
- VLAN segmentation isolates department traffic
- Centralized routing through core router
- Separate guest network for visitors
- Infrastructure security department has dedicated VLAN

## Configuration Files
- Network configuration saved to: {self.config_file}
- GNS3 project location: {self.server}
- API Version: {self.api_version}

## Usage Instructions
1. Ensure GNS3 server is running
2. Load this project using the Project ID
3. Start all nodes to begin network simulation
4. Configure router interfaces and VLAN settings as needed
5. Test connectivity between departments

## Troubleshooting
- Verify GNS3 server is accessible at {self.server}
- Check that all required templates are available
- Ensure sufficient system resources for all nodes
- Verify port assignments don't conflict

---
*This documentation was automatically generated by the GNS3 Network Builder*
"""
        
        # Save documentation to file
        doc_filename = f"{self.project_name}_Documentation.md"
        try:
            with open(doc_filename, 'w') as doc_file:
                doc_file.write(doc_content)
            print(f"✓ Network documentation exported to: {doc_filename}")
        except Exception as e:
            print(f"⚠ Could not save documentation file: {e}")
        
        return doc_content

def cleanup_project(self):
        """Clean up project resources"""
        print(f"\n🧹 Cleaning up project resources...")
        
        try:
            # Stop all nodes first
            for node_name, node_info in self.created_nodes.items():
                node_id = node_info["node_id"]
                url = f"{self.server}/{self.api_version}/projects/{self.project_id}/nodes/{node_id}/stop"
                response = self.session.post(url)
                if response.status_code == 204:
                    print(f"✓ Stopped node: {node_name}")
                else:
                    print(f"⚠ Could not stop node {node_name}: {response.status_code}")
            
            print(f"✓ Project cleanup completed")
            
        except Exception as e:
            print(f"⚠ Error during cleanup: {e}")

def start_all_nodes(self):
        """Start all nodes in the project"""
        print(f"\n🚀 Starting all network nodes...")
        
        started_count = 0
        failed_count = 0
        
        for node_name, node_info in self.created_nodes.items():
            node_id = node_info["node_id"]
            url = f"{self.server}/{self.api_version}/projects/{self.project_id}/nodes/{node_id}/start"
            
            try:
                response = self.session.post(url)
                if response.status_code == 204:
                    print(f"✓ Started: {node_name}")
                    started_count += 1
                else:
                    print(f"⚠ Failed to start {node_name}: {response.status_code}")
                    failed_count += 1
                    
                # Small delay to prevent overwhelming the server
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error starting {node_name}: {e}")
                failed_count += 1
        
        print(f"\n📊 Startup Summary:")
        print(f"   • Started: {started_count} nodes")
        print(f"   • Failed: {failed_count} nodes")
        print(f"   • Total: {len(self.created_nodes)} nodes")

def get_project_status(self):
        """Get current project status and statistics"""
        print(f"\n📊 Project Status Report")
        print("=" * 50)
        
        try:
            # Get project information
            url = f"{self.server}/{self.api_version}/projects/{self.project_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                project_data = response.json()
                print(f"✓ Project: {project_data.get('name', 'Unknown')}")
                print(f"  Status: {project_data.get('status', 'Unknown')}")
                print(f"  Created: {project_data.get('created_at', 'Unknown')}")
                
                # Get nodes status
                nodes_url = f"{self.server}/{self.api_version}/projects/{self.project_id}/nodes"
                nodes_response = self.session.get(nodes_url)
                
                if nodes_response.status_code == 200:
                    nodes = nodes_response.json()
                    node_status = {}
                    
                    for node in nodes:
                        status = node.get('status', 'unknown')
                        node_status[status] = node_status.get(status, 0) + 1
                    
                    print(f"\n🖥️  Node Status:")
                    for status, count in node_status.items():
                        print(f"   • {status.title()}: {count}")
                
                # Get links status
                links_url = f"{self.server}/{self.api_version}/projects/{self.project_id}/links"
                links_response = self.session.get(links_url)
                
                if links_response.status_code == 200:
                    links = links_response.json()
                    print(f"\n🔗 Network Links: {len(links)} total")
                
            else:
                print(f"❌ Could not get project status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error getting project status: {e}")

def main():
    """Main execution function"""
    print("🌐 GNS3 Software Company Network Builder")
    print("=" * 60)
    
    try:
        # Initialize builder
        builder = SoftwareCompanyNetworkBuilder()
        
        # Build the complete network
        success = builder.build_complete_network()
        
        if success:
            print(f"\n🎉 Network build completed successfully!")
            
            # Export documentation
            builder.export_network_documentation()
            
            # Get project status
            builder.get_project_status()
            
            # Ask user if they want to start all nodes
            start_nodes = input(f"\n🚀 Start all network nodes? (y/n): ").lower().strip()
            if start_nodes in ['y', 'yes']:
                builder.start_all_nodes()
            
            print(f"\n✅ All operations completed!")
            print(f"🔗 Access your project at: {builder.server}")
            print(f"📋 Project ID: {builder.project_id}")
            
        else:
            print(f"\n❌ Network build failed!")
            
    except KeyboardInterrupt:
        print(f"\n⚠ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()