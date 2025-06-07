#!/usr/bin/env python3

###############################
##              Enhanced GNS3 Topology Builder
##Integrates with existing Ansible automation project
##Reads from network_data.yml and generates GNS3 topology
############################################################

#Enhanced GNS3 Topology Builder
#=============================
#This script automates the creation of network topologies in GNS3 (Graphical Network Simulator)
#It reads network configuration from YAML files and creates a complete corporate network
#with multiple departments, VLANs, and proper network segmentation.
#Key Features:
#- Reads network configuration from YAML files
#- Creates GNS3 projects programmatically via REST API
#- Builds multi-department corporate networks
#- Calculates optimal device positioning
#- Generates Ansible inventory files
#- Handles VLAN segmentation and IP addressing

import requests      # For HTTP requests to GNS3 API Server "http://127.0.0.1:3080" 
import json         # For JSON data handling
import yaml         # For YAML configuration files
import math         # For circular positioning calculations  
import time         # For timestamps
import os           # For file operations
from typing import Dict, List, Tuple, Any  # Type hints for better code clarity
from pathlib import Path  # Modern path handling

class EnhancedGNS3Builder:
    def __init__(self, 
                 config_file: str = "network_data.yml",
                 gns3_server: str = "http://127.0.0.1:3080",
                 project_name: str = "Automation of Network"):
        
        self.config_file = config_file
        self.server = gns3_server
        self.session = requests.Session()
        self.project_id = "9a8ab49a-6f61-4fa8-9089-99e6c6594e4f"
        self.templates = {}
        
        # Load network configuration
        self.load_network_config()
        
        #Load project, because i already have the project crfeated
        # Set project name
        self.project_name = project_name or self.config.get('project_name', 'Automated_Network')
        
        # Track created nodes and links
        self.created_nodes = {}
        self.created_links = []
        
    def load_network_config(self):
        """Load network configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            print(f"✓ Loaded configuration from {self.config_file}")
        except FileNotFoundError:
            print(f"⚠ Config file {self.config_file} not found, using default configuration")
            self.config = self._default_config()
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML: {e}")
            raise
    
    def _default_config(self) -> Dict[str, Any]:
        """Default network configuration if file doesn't exist"""
        return {
            "project_name": "Software_Company_Network",
            "topology": {
                "center_position": {"x": 0, "y": 0},
                "department_radius": 400,
                "device_radius": 150
            },
            "infrastructure": {
                "core_router": {
                    "name": "Core-Router",
                    "template": "router",
                    "position": {"x": 0, "y": 0}
                },
                "core_switch": {
                    "name": "Core-Switch", 
                    "template": "switch",
                    "position": {"x": 0, "y": -100}
                },
                "internet_cloud": {
                    "name": "Internet",
                    "template": "cloud",
                    "position": {"x": 0, "y": -250}
                }
            },
            "departments": [
                {
                    "name": "IT_Security",
                    "vlan_id": 10,
                    "network": "192.168.10.0/24",
                    "gateway": "192.168.10.1",
                    "device_count": 6,
                    "color": "#8A2BE2",
                    "has_server": True
                },
                {
                    "name": "Development", 
                    "vlan_id": 20,
                    "network": "192.168.20.0/24",
                    "gateway": "192.168.20.1",
                    "device_count": 8,
                    "color": "#4169E1",
                    "has_server": True
                },
                {
                    "name": "Marketing",
                    "vlan_id": 30, 
                    "network": "192.168.30.0/24",
                    "gateway": "192.168.30.1",
                    "device_count": 5,
                    "color": "#32CD32",
                    "has_server": False
                },
                {
                    "name": "Sales",
                    "vlan_id": 40,
                    "network": "192.168.40.0/24", 
                    "gateway": "192.168.40.1",
                    "device_count": 7,
                    "color": "#FF8C00",
                    "has_server": True
                },
                {
                    "name": "HR",
                    "vlan_id": 50,
                    "network": "192.168.50.0/24",
                    "gateway": "192.168.50.1", 
                    "device_count": 4,
                    "color": "#DC143C",
                    "has_server": False
                }
            ]
        }
    
    def create_project(self) -> str:
        """Create GNS3 project"""
        url = f"{self.server}/v2/projects"
        data = {"name": self.project_name}
        
        try:
            response = self.session.post(url, json=data)
            if response.status_code == 201:
                project_data = response.json()
                self.project_id = project_data["project_id"]
                print(f"✓ Created project: {self.project_name}")
                print(f"  Project ID: {self.project_id}")
                return self.project_id
            else:
                raise Exception(f"Failed to create project: {response.text}")
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to GNS3 server. Is GNS3 running?")
    
    def get_templates(self):
        """Retrieve available GNS3 templates"""
        url = f"{self.server}/v2/templates"
        response = self.session.get(url)
        
        if response.status_code == 200:
            templates = response.json()
            for template in templates:
                self.templates[template['name'].lower()] = template['template_id']
            print(f"✓ Found {len(self.templates)} available templates")
        else:
            print(f"⚠ Could not retrieve templates: {response.text}")
    
    def create_node(self, name: str, template_type: str, x: int, y: int, symbol: str = None) -> str:
        """Create a network node"""
        url = f"{self.server}/v2/projects/{self.project_id}/nodes"
        
        # Find matching template
        template_id = self._find_template(template_type)
        
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
                print(f"⚠ Failed to create {name}: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error creating node {name}: {str(e)}")
            return None
    
    def _find_template(self, template_type: str) -> str:
        """Find template ID by type"""
        template_type = template_type.lower()
        
        # Try exact match first
        if template_type in self.templates:
            return self.templates[template_type]
        
        # Try partial matches
        for template_name, template_id in self.templates.items():
            if template_type in template_name or template_name in template_type:
                return template_id
        
        # Default fallbacks
        fallbacks = {
            'router': ['c7200', 'c3725', 'c2691', 'router'],
            'switch': ['switch', 'c3560', 'c2960', 'ethernet_switch'],
            'cloud': ['cloud', 'nat'],
            'vpcs': ['vpcs', 'pc'],
            'server': ['server', 'qemu']
        }
        
        if template_type in fallbacks:
            for fallback in fallbacks[template_type]:
                for template_name, template_id in self.templates.items():
                    if fallback in template_name:
                        return template_id
        
        # Return first available template as last resort
        if self.templates:
            return list(self.templates.values())[0]
        
        raise Exception(f"No suitable template found for {template_type}")
    
    def create_link(self, node1_name: str, node1_port: int, node2_name: str, node2_port: int) -> str:
        """Create link between nodes"""
        if node1_name not in self.created_nodes or node2_name not in self.created_nodes:
            print(f"⚠ Cannot link {node1_name} to {node2_name} - one or both nodes not found")
            return None
        
        url = f"{self.server}/v2/projects/{self.project_id}/links"
        
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
                print(f"⚠ Failed to create link: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error creating link: {str(e)}")
            return None
    
    def calculate_positions(self) -> Dict[str, List[Tuple[int, int]]]:
        """Calculate positions for all network elements"""
        positions = {}
        
        # Get topology settings
        topo = self.config.get("topology", {})
        center_x = topo.get("center_position", {}).get("x", 0)
        center_y = topo.get("center_position", {}).get("y", 0)
        dept_radius = topo.get("department_radius", 400)
        device_radius = topo.get("device_radius", 150)
        
        # Infrastructure positions (from config or defaults)
        infra = self.config.get("infrastructure", {})
        positions["infrastructure"] = {}
        for device_name, device_config in infra.items():
            pos = device_config.get("position", {"x": center_x, "y": center_y})
            positions["infrastructure"][device_name] = (pos["x"], pos["y"])
        
        # Department positions in circle
        departments = self.config.get("departments", [])
        num_depts = len(departments)
        positions["departments"] = {}
        
        for i, dept in enumerate(departments):
            angle = (2 * math.pi * i) / num_depts - (math.pi / 2)  # Start from top
            dept_x = center_x + int(dept_radius * math.cos(angle))
            dept_y = center_y + int(dept_radius * math.sin(angle))
            
            positions["departments"][dept["name"]] = {
                "switch": (dept_x, dept_y),
                "devices": self._calculate_device_positions(
                    dept_x, dept_y, dept["device_count"], device_radius
                )
            }
            
            # Server position if exists
            if dept.get("has_server", False):
                positions["departments"][dept["name"]]["server"] = (dept_x + 120, dept_y + 120)
        
        return positions
    
    def _calculate_device_positions(self, center_x: int, center_y: int, 
                                   count: int, radius: int) -> List[Tuple[int, int]]:
        """Calculate device positions in circle around department switch"""
        if count == 0:
            return []
        if count == 1:
            return [(center_x, center_y + radius)]
        
        positions = []
        for i in range(count):
            angle = (2 * math.pi * i) / count
            x = center_x + int(radius * math.cos(angle))
            y = center_y + int(radius * math.sin(angle))
            positions.append((x, y))
        
        return positions
    
    def build_topology(self):
        """Build the complete network topology"""
        print(f"\n🚀 Building GNS3 Topology: {self.project_name}")
        print("=" * 60)
        
        # Step 1: Create project
        self.create_project()
        
        # Step 2: Get templates
        self.get_templates()
        
        # Step 3: Calculate all positions
        positions = self.calculate_positions()
        
        # Step 4: Create infrastructure
        print(f"\n🏗️  Creating Core Infrastructure...")
        infra = self.config.get("infrastructure", {})
        
        for device_name, device_config in infra.items():
            pos = positions["infrastructure"][device_name]
            self.create_node(
                name=device_config["name"],
                template_type=device_config["template"],
                x=pos[0],
                y=pos[1]
            )
        
        # Step 5: Link core infrastructure
        print(f"\n🔗 Linking Core Infrastructure...")
        core_router = infra.get("core_router", {}).get("name", "Core-Router")
        core_switch = infra.get("core_switch", {}).get("name", "Core-Switch") 
        internet = infra.get("internet_cloud", {}).get("name", "Internet")
        
        if core_router in self.created_nodes and core_switch in self.created_nodes:
            self.create_link(core_router, 0, core_switch, 0)
        
        if core_router in self.created_nodes and internet in self.created_nodes:
            self.create_link(internet, 0, core_router, 1)
        
        # Step 6: Create departments
        print(f"\n🏢 Creating Departments...")
        departments = self.config.get("departments", [])
        router_port = 2  # Ports 0,1 used for core connectivity
        
        for dept in departments:
            dept_name = dept["name"]
            print(f"\n  📁 Building {dept_name} Department (VLAN {dept['vlan_id']})")
            
            # Create department switch
            switch_name = f"SW-{dept_name}"
            dept_positions = positions["departments"][dept_name]
            switch_pos = dept_positions["switch"]
            
            self.create_node(
                name=switch_name,
                template_type="switch", 
                x=switch_pos[0],
                y=switch_pos[1]
            )
            
            # Link department switch to core router
            if switch_name in self.created_nodes and core_router in self.created_nodes:
                self.create_link(core_router, router_port, switch_name, 0)
                router_port += 1
            
            # Create department devices
            device_positions = dept_positions["devices"]
            switch_port = 1
            
            for i, (dev_x, dev_y) in enumerate(device_positions):
                if i < dept["device_count"]:
                    device_name = f"PC-{dept_name}-{i+1:02d}"
                    self.create_node(
                        name=device_name,
                        template_type="vpcs",
                        x=dev_x,
                        y=dev_y
                    )
                    
                    # Link device to department switch
                    if device_name in self.created_nodes:
                        self.create_link(switch_name, switch_port, device_name, 0)
                        switch_port += 1
            
            # Create department server if specified
            if dept.get("has_server", False):
                server_name = f"SRV-{dept_name}"
                server_pos = dept_positions["server"]
                
                self.create_node(
                    name=server_name,
                    template_type="server",
                    x=server_pos[0],
                    y=server_pos[1]
                )
                
                if server_name in self.created_nodes:
                    self.create_link(switch_name, switch_port, server_name, 0)
        
        # Step 7: Generate summary
        self._print_build_summary()
        
        return self.created_nodes
    
    def _print_build_summary(self):
        """Print build summary"""
        print(f"\n✅ Topology Build Complete!")
        print("=" * 60)
        print(f"📊 Build Summary:")
        print(f"   • Project: {self.project_name}")
        print(f"   • Project ID: {self.project_id}")
        print(f"   • Total Nodes: {len(self.created_nodes)}")
        print(f"   • Total Links: {len(self.created_links)}")
        print(f"   • Departments: {len(self.config.get('departments', []))}")
        
        # Node breakdown
        node_types = {}
        for node_name, node_info in self.created_nodes.items():
            node_type = node_info["type"]
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        print(f"\n📋 Node Breakdown:")
        for node_type, count in node_types.items():
            print(f"   • {node_type.title()}: {count}")
    
    def export_to_ansible_inventory(self, output_file: str = "ansible/inventory.ini"):
        """Export topology to Ansible inventory format"""
        inventory_content = """# Generated Ansible Inventory from GNS3 Topology
# Project: {project_name}
# Generated: {timestamp}

[routers]
""".format(
            project_name=self.project_name,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Add routers
        for node_name, node_info in self.created_nodes.items():
            if "router" in node_info["type"].lower():
                inventory_content += f"{node_name} ansible_host=192.168.1.1 device_type=cisco_ios\n"
        
        inventory_content += "\n[switches]\n"
        
        # Add switches
        for node_name, node_info in self.created_nodes.items():
            if "switch" in node_name.lower():
                inventory_content += f"{node_name} ansible_host=192.168.1.2 device_type=cisco_ios\n"
        
        # Add department groups
        departments = self.config.get("departments", [])
        for dept in departments:
            dept_name = dept["name"]
            inventory_content += f"\n[{dept_name.lower()}]\n"
            
            for node_name in self.created_nodes:
                if dept_name in node_name:
                    gateway = dept.get("gateway", "192.168.1.1")
                    inventory_content += f"{node_name} ansible_host={gateway}\n"
        
        # Write to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(inventory_content)
        
        print(f"✓ Ansible inventory exported to {output_file}")
    
    def generate_network_data_yaml(self, output_file: str = "network_data.yml"):
        """Generate or update network_data.yml with current topology"""
        if os.path.exists(output_file):
            print(f"⚠ {output_file} already exists, backing up...")
            backup_file = f"{output_file}.backup"
            os.rename(output_file, backup_file)
        
        with open(output_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)
        
        print(f"✓ Network configuration saved to {output_file}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced GNS3 Topology Builder')
    parser.add_argument('--config', '-c', default='network_data.yml',
                       help='Network configuration file (default: network_data.yml)')
    parser.add_argument('--server', '-s', default='http://127.0.0.1:3080',
                       help='GNS3 server URL (default: http://127.0.0.1:3080)')
    parser.add_argument('--project', '-p', default=None,
                       help='Project name (default: from config file)')
    parser.add_argument('--export-inventory', action='store_true',
                       help='Export Ansible inventory after build')
    parser.add_argument('--generate-config', action='store_true',
                       help='Generate sample network_data.yml')
    
    args = parser.parse_args()
    
    try:
        builder = EnhancedGNS3Builder(
            config_file=args.config,
            gns3_server=args.server,
            project_name=args.project
        )
        
        if args.generate_config:
            builder.generate_network_data_yaml()
            return
        
        # Build the topology
        nodes = builder.build_topology()
        
        # Export to Ansible inventory if requested
        if args.export_inventory:
            builder.export_to_ansible_inventory()
        
        print(f"\n🎉 Success! Your network topology is ready in GNS3.")
        print(f"📋 Next steps:")
        print(f"   1. Open GNS3 and load project: {builder.project_name}")
        print(f"   2. Start the nodes to begin testing")
        print(f"   3. Use Ansible playbooks to configure devices")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()