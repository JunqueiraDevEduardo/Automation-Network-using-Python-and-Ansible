#!/usr/bin/env python3
"""
Network Automation Generator
Converts your manual Cisco configurations to automated network deployment
Works with existing GNS3 projects and generates Ansible playbooks
"""

# Import required libraries for YAML parsing, JSON handling, regex operations,
# type hints, file system operations, and IP address calculations
import yaml
import json
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import ipaddress

class NetworkAutomationGenerator:
    """
    Main class responsible for converting manual network configurations into
    automated deployment files. Generates Ansible inventories, playbooks,
    configuration scripts, and network topology data.
    """
    
    def __init__(self, config_file: str = "network_data.yml"):
        """
        Initialize the generator with configuration file path.
        Sets up data structures for storing device, VLAN, and network information.
        """
        self.config_file = config_file
        self.load_config()  # Load network configuration from YAML file
        
        # Initialize storage for parsed network components
        self.devices = {}   # Dictionary to store device configurations
        self.vlans = {}     # Dictionary to store VLAN information
        self.networks = {}  # Dictionary to store network segment data
        
    def load_config(self):
        """
        Load network configuration from YAML file.
        Handles file not found errors and creates default empty configuration.
        """
        try:
            # Attempt to open and parse the YAML configuration file
            with open(self.config_file, 'r') as file:
                self.config = yaml.safe_load(file)
            print(f"Loaded configuration from {self.config_file}")
        except FileNotFoundError:
            # Create default configuration if file doesn't exist
            print(f"Configuration file {self.config_file} not found")
            self.config = {"departments": []}  # Default empty departments list

    def parse_manual_config(self, config_text: str) -> Dict:
        """
        Parse manual Cisco configuration text into structured device configurations.
        Identifies device sections and extracts their configurations.
        
        Args:
            config_text: Raw configuration text with device sections
            
        Returns:
            Dictionary mapping device names to their configuration text
        """
        print("Parsing manual configuration...")
        
        # Initialize variables for parsing device sections
        devices = {}
        current_device = None
        current_config = []
        
        # Split configuration text into individual lines for processing
        lines = config_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check for device section headers (lines starting with '-')
            if line.startswith('-'):
                # Save previous device configuration if it exists
                if current_device and current_config:
                    devices[current_device] = '\n'.join(current_config)
                
                # Start new device section (remove '-' prefix)
                current_device = line[1:].strip()
                current_config = []
            elif line and current_device:
                # Add configuration line to current device
                current_config.append(line)
        
        # Save the last device configuration
        if current_device and current_config:
            devices[current_device] = '\n'.join(current_config)
        
        print(f"Parsed {len(devices)} device configurations")
        return devices

    def extract_device_info(self, config_text: str) -> Dict:
        """
        Extract structured device information from Cisco configuration text.
        Parses hostname, interfaces, VLANs, IP addresses, and device type.
        
        Args:
            config_text: Cisco configuration text for a single device
            
        Returns:
            Dictionary containing structured device information
        """
        # Initialize device information structure
        device_info = {
            'hostname': None,
            'interfaces': {},     # Interface configurations
            'vlans': {},         # VLAN definitions
            'type': 'unknown',   # Device type (switch/router/pc/server)
            'ip_addresses': [],  # List of IP addresses assigned to device
            'default_gateway': None
        }
        
        lines = config_text.split('\n')
        current_interface = None  # Track current interface being parsed
        
        for line in lines:
            line = line.strip()
            
            # Extract hostname and determine device type
            if line.startswith('hostname '):
                device_info['hostname'] = line.split()[1]
                
                # Determine device type based on hostname patterns
                hostname_lower = device_info['hostname'].lower()
                if 'switch' in hostname_lower or 'sw-' in hostname_lower:
                    device_info['type'] = 'switch'
                elif 'router' in hostname_lower or 'r-' in hostname_lower:
                    device_info['type'] = 'router'
                elif 'pc-' in hostname_lower:
                    device_info['type'] = 'pc'
                elif 'server' in hostname_lower:
                    device_info['type'] = 'server'
            
            # Extract VLAN configuration information
            elif line.startswith('vlan '):
                vlan_id = line.split()[1]
                device_info['vlans'][vlan_id] = {}
            elif line.startswith('name ') and len(device_info['vlans']) > 0:
                # Associate VLAN name with the most recently defined VLAN
                last_vlan = list(device_info['vlans'].keys())[-1]
                device_info['vlans'][last_vlan]['name'] = line.split()[1]
            
            # Extract interface configuration information
            elif line.startswith('interface '):
                current_interface = line.split()[1]
                device_info['interfaces'][current_interface] = {}
            elif current_interface and line.startswith('ip address '):
                # Parse IP address and netmask from interface configuration
                parts = line.split()
                if len(parts) >= 3:
                    ip_addr = parts[2]
                    netmask = parts[3] if len(parts) > 3 else '255.255.255.0'
                    device_info['interfaces'][current_interface]['ip'] = ip_addr
                    device_info['interfaces'][current_interface]['netmask'] = netmask
                    device_info['ip_addresses'].append(f"{ip_addr}/{netmask}")
            elif current_interface and line.startswith('switchport mode '):
                # Extract switchport mode (access/trunk)
                device_info['interfaces'][current_interface]['mode'] = line.split()[2]
            elif current_interface and line.startswith('switchport access vlan '):
                # Extract access VLAN assignment
                device_info['interfaces'][current_interface]['vlan'] = line.split()[3]
            elif current_interface and line.startswith('switchport trunk allowed vlan '):
                # Extract trunk allowed VLANs
                device_info['interfaces'][current_interface]['allowed_vlans'] = line.split()[4]
            
            # Extract default gateway configuration
            elif line.startswith('ip default-gateway '):
                device_info['default_gateway'] = line.split()[1]
        
        return device_info

    def generate_network_inventory(self) -> Dict:
        """
        Generate Ansible inventory structure from department configuration.
        Creates organized inventory with switches, routers, PCs, and servers.
        
        Returns:
            Dictionary containing Ansible inventory structure
        """
        print("Generating network inventory...")
        
        # Initialize Ansible inventory structure with device type groups
        inventory = {
            'all': {
                'children': {
                    'switches': {'hosts': {}},  # Network switches
                    'routers': {'hosts': {}},   # Network routers
                    'pcs': {'hosts': {}},       # End-user PCs
                    'servers': {'hosts': {}}    # Server devices
                }
            }
        }
        
        # Process each department from configuration
        for dept in self.config.get('departments', []):
            dept_name = dept['name']
            dept_code = dept['code']
            vlan_id = dept['vlan_id']
            network = dept['network']
            gateway = dept['gateway']
            
            # Create department switch entry with management information
            switch_name = f"SW-{dept_code}-{dept_name}"
            inventory['all']['children']['switches']['hosts'][switch_name] = {
                'ansible_host': gateway,    # Use gateway IP for switch management
                'department': dept_name,
                'vlan_id': vlan_id,
                'network': network,
                'mgmt_ip': gateway
            }
            
            # Get device counts for this department
            devices = dept.get('devices', {})
            
            # Generate PC entries with calculated IP addresses
            for i in range(devices.get('pc', 0)):
                pc_name = f"PC-{dept_code}-{i+1:02d}"
                try:
                    # Calculate PC IP address within department network
                    network_obj = ipaddress.IPv4Network(f"{network}/{dept.get('subnet_mask', '255.255.255.240')}", strict=False)
                    pc_ip = str(list(network_obj.hosts())[i+1])  # Skip gateway IP
                    
                    inventory['all']['children']['pcs']['hosts'][pc_name] = {
                        'ansible_host': pc_ip,
                        'department': dept_name,
                        'vlan_id': vlan_id,
                        'default_gateway': gateway
                    }
                except:
                    # Skip if IP calculation fails
                    pass
            
            # Generate server entries with calculated IP addresses
            for i in range(devices.get('server', 0)):
                server_name = f"Server-{dept_code}-{i+1:02d}"
                try:
                    # Calculate server IP address after PC range
                    network_obj = ipaddress.IPv4Network(f"{network}/{dept.get('subnet_mask', '255.255.255.240')}", strict=False)
                    server_ip = str(list(network_obj.hosts())[devices.get('pc', 0) + i + 2])
                    
                    inventory['all']['children']['servers']['hosts'][server_name] = {
                        'ansible_host': server_ip,
                        'department': dept_name,
                        'vlan_id': vlan_id,
                        'default_gateway': gateway
                    }
                except:
                    # Skip if IP calculation fails
                    pass
        
        return inventory

    def generate_vlan_config_playbook(self) -> str:
        """
        Generate Ansible playbook for configuring VLANs on network switches.
        Creates playbook with VLAN definitions for all departments.
        
        Returns:
            String containing complete Ansible playbook for VLAN configuration
        """
        print("Generating VLAN configuration playbook...")
        
        # Start with playbook header and connection settings
        playbook = """---
- name: Configure VLANs on Network Switches
  hosts: switches
  gather_facts: no
  connection: network_cli
  
  vars:
    ansible_network_os: ios
    ansible_user: admin
    ansible_password: admin
    ansible_become: yes
    ansible_become_method: enable
    
  tasks:
    - name: Configure VLANs
      cisco.ios.ios_vlans:
        config:
"""
        
        # Add VLAN configuration entries for each department
        for dept in self.config.get('departments', []):
            vlan_id = dept['vlan_id']
            vlan_name = dept['name'].replace('_', '-')  # Replace underscores for valid VLAN names
            
            playbook += f"""          - vlan_id: {vlan_id}
            name: "{vlan_name}"
            state: active
"""
        
        # Add playbook footer with merge state and save configuration
        playbook += """
        state: merged
        
    - name: Save configuration
      cisco.ios.ios_config:
        save_when: always
"""
        
        return playbook

    def generate_interface_config_playbook(self) -> str:
        """
        Generate Ansible playbook for configuring switch interfaces.
        Creates access port configurations based on department device counts.
        
        Returns:
            String containing complete Ansible playbook for interface configuration
        """
        print("Generating interface configuration playbook...")
        
        # Start with playbook header and connection settings
        playbook = """---
- name: Configure Switch Interfaces
  hosts: switches
  gather_facts: no
  connection: network_cli
  
  vars:
    ansible_network_os: ios
    ansible_user: admin
    ansible_password: admin
    ansible_become: yes
    ansible_become_method: enable
    
  tasks:
    - name: Configure access ports
      cisco.ios.ios_l2_interfaces:
        config:
"""
        
        # Generate interface configurations sequentially across departments
        port_num = 1  # Start with port 1
        for dept in self.config.get('departments', []):
            vlan_id = dept['vlan_id']
            devices = dept.get('devices', {})
            
            # Calculate total devices needing access ports
            total_devices = devices.get('pc', 0) + devices.get('server', 0) + devices.get('printer', 0)
            
            # Create access port configuration for each device
            for i in range(total_devices):
                interface = f"FastEthernet0/{port_num}"
                playbook += f"""          - name: {interface}
            access:
              vlan: {vlan_id}
"""
                port_num += 1  # Move to next port
        
        # Add playbook footer with merge state and save configuration
        playbook += """
        state: merged
        
    - name: Save configuration
      cisco.ios.ios_config:
        save_when: always
"""
        
        return playbook

    def generate_pc_config_script(self) -> str:
        """
        Generate bash script for configuring PC network settings.
        Creates script with IP configuration commands for both Linux and Windows.
        
        Returns:
            String containing complete bash script for PC configuration
        """
        print("Generating PC configuration script...")
        
        # Start with script header and description
        script = """#!/bin/bash
# PC Network Configuration Script
# Configures IP addresses and gateways for all department PCs

echo "Configuring PC Network Settings..."

"""
        
        # Generate configuration section for each department
        for dept in self.config.get('departments', []):
            dept_name = dept['name']
            dept_code = dept['code']
            network = dept['network']
            gateway = dept['gateway']
            subnet_mask = dept.get('subnet_mask', '255.255.255.240')
            
            devices = dept.get('devices', {})
            
            script += f"""
# {dept_name} Department (VLAN {dept['vlan_id']})
echo "Configuring {dept_name} PCs..."
"""
            
            try:
                # Calculate IP addresses for PCs in this department
                network_obj = ipaddress.IPv4Network(f"{network}/{subnet_mask}", strict=False)
                hosts = list(network_obj.hosts())
                
                # Generate configuration commands for each PC
                for i in range(devices.get('pc', 0)):
                    pc_name = f"PC-{dept_code}-{i+1:02d}"
                    pc_ip = str(hosts[i+1])  # Skip gateway IP (first host)
                    
                    script += f"""
# Configure {pc_name}
echo "  Setting up {pc_name}: {pc_ip}"
# For Ubuntu/Linux PCs:
# sudo ip addr add {pc_ip}/{network_obj.prefixlen} dev eth0
# sudo ip route add default via {gateway}
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static {pc_ip} {subnet_mask} {gateway}
# netsh interface ip set dns "Ethernet" static 8.8.8.8
"""
            except:
                # Add error comment if IP calculation fails
                script += f"# Error calculating IPs for {dept_name}\n"
        
        # Add script footer with completion message
        script += """
echo "PC configuration completed!"
echo "Note: Uncomment and modify the appropriate commands for your OS"
"""
        
        return script

    def generate_network_diagram_data(self) -> Dict:
        """
        Generate JSON data for network topology visualization.
        Creates nodes and links for a visual network diagram.
        
        Returns:
            Dictionary containing nodes, links, and VLAN information for visualization
        """
        print("Generating network diagram data...")
        
        # Initialize diagram data structure
        diagram_data = {
            'nodes': [],  # Network devices and endpoints
            'links': [],  # Connections between devices
            'vlans': {}   # VLAN information for color coding
        }
        
        # Add central core switch as the main hub
        diagram_data['nodes'].append({
            'id': 'CoreSwitch',
            'label': 'Core Switch',
            'type': 'switch',
            'x': 0,    # Center position
            'y': 0,
            'color': '#FF6B6B'  # Red color for core switch
        })
        
        # Calculate circular layout for departments around core switch
        import math
        num_depts = len(self.config.get('departments', []))
        radius = 300  # Distance from center for department switches
        
        for i, dept in enumerate(self.config.get('departments', [])):
            # Calculate position angle for even distribution
            angle = (2 * math.pi * i) / num_depts
            x = int(radius * math.cos(angle))
            y = int(radius * math.sin(angle))
            
            dept_name = dept['name']
            dept_code = dept['code']
            vlan_id = dept['vlan_id']
            
            # Add department switch node
            switch_id = f"SW-{dept_code}"
            diagram_data['nodes'].append({
                'id': switch_id,
                'label': f"Switch {dept_code}\n{dept_name}",
                'type': 'switch',
                'x': x,
                'y': y,
                'color': dept.get('color', '#4ECDC4'),  # Department color or default
                'vlan': vlan_id
            })
            
            # Create trunk link between core switch and department switch
            diagram_data['links'].append({
                'source': 'CoreSwitch',
                'target': switch_id,
                'type': 'trunk',
                'vlan': vlan_id
            })
            
            # Add end devices (PCs and servers) around department switch
            devices = dept.get('devices', {})
            device_radius = 100  # Distance from department switch
            device_count = devices.get('pc', 0) + devices.get('server', 0)
            
            for j in range(device_count):
                # Determine device type and create appropriate ID/label
                if j < devices.get('pc', 0):
                    device_id = f"PC-{dept_code}-{j+1}"
                    device_label = f"PC {j+1}"
                    device_type = 'pc'
                else:
                    server_num = j - devices.get('pc', 0) + 1
                    device_id = f"Server-{dept_code}-{server_num}"
                    device_label = f"Server {server_num}"
                    device_type = 'server'
                
                # Calculate device position around department switch
                if device_count == 1:
                    # Single device positioned directly below switch
                    dev_x, dev_y = x, y + device_radius
                else:
                    # Multiple devices distributed in circle around switch
                    dev_angle = (2 * math.pi * j) / device_count
                    dev_x = x + int(device_radius * math.cos(dev_angle))
                    dev_y = y + int(device_radius * math.sin(dev_angle))
                
                # Add device node
                diagram_data['nodes'].append({
                    'id': device_id,
                    'label': device_label,
                    'type': device_type,
                    'x': dev_x,
                    'y': dev_y,
                    'color': '#95E1D3',  # Light green for end devices
                    'vlan': vlan_id
                })
                
                # Create access link between department switch and device
                diagram_data['links'].append({
                    'source': switch_id,
                    'target': device_id,
                    'type': 'access',
                    'vlan': vlan_id
                })
            
            # Store VLAN information for reference
            diagram_data['vlans'][vlan_id] = {
                'name': dept_name,
                'network': dept['network'],
                'gateway': dept['gateway'],
                'color': dept.get('color', '#4ECDC4')
            }
        
        return diagram_data

    def save_all_files(self):
        """
        Save all generated configuration files to the output directory.
        Creates inventory, playbooks, scripts, and documentation files.
        """
        print("\nSaving automation files...")
        
        # Create output directory for generated files
        output_dir = Path("network_automation")
        output_dir.mkdir(exist_ok=True)
        
        # Generate and save Ansible inventory file
        inventory = self.generate_network_inventory()
        with open(output_dir / "inventory.yml", 'w') as f:
            yaml.dump(inventory, f, default_flow_style=False, indent=2)
        print(f"Saved inventory.yml")
        
        # Generate and save VLAN configuration playbook
        vlan_playbook = self.generate_vlan_config_playbook()
        with open(output_dir / "configure_vlans.yml", 'w') as f:
            f.write(vlan_playbook)
        print(f"Saved configure_vlans.yml")
        
        # Generate and save interface configuration playbook
        interface_playbook = self.generate_interface_config_playbook()
        with open(output_dir / "configure_interfaces.yml", 'w') as f:
            f.write(interface_playbook)
        print(f"Saved configure_interfaces.yml")
        
        # Generate and save PC configuration script
        pc_script = self.generate_pc_config_script()
        with open(output_dir / "configure_pcs.sh", 'w') as f:
            f.write(pc_script)
        (output_dir / "configure_pcs.sh").chmod(0o755)  # Make script executable
        print(f"Saved configure_pcs.sh")
        
        # Generate and save network diagram data for visualization
        diagram_data = self.generate_network_diagram_data()
        with open(output_dir / "network_diagram.json", 'w') as f:
            json.dump(diagram_data, f, indent=2)
        print(f"Saved network_diagram.json")
        
        # Generate and save README documentation
        readme_content = self.generate_readme()
        with open(output_dir / "README.md", 'w') as f:
            f.write(readme_content)
        print(f"Saved README.md")
        
        print(f"\nAll files saved to '{output_dir}' directory")

    def generate_readme(self) -> str:
        """
        Generate README documentation file with usage instructions.
        
        Returns:
            String containing complete README content in Markdown format
        """
        return f"""# Network Automation Files

This directory contains automated configuration files generated from your manual network setup.

## Generated Files

### Inventory
- `inventory.yml` - Ansible inventory with all network devices

### Playbooks
- `configure_vlans.yml` - Configures VLANs on switches
- `configure_interfaces.yml` - Configures switch interfaces

### Scripts
- `configure_pcs.sh` - Script to configure PC network settings

### Documentation
- `network_diagram.json` - Network topology data for visualization
- `README.md` - This file

## Usage

### 1. Configure Switches with Ansible
```bash
# Install Ansible and Cisco collection
pip install ansible
ansible-galaxy collection install cisco.ios

# Run VLAN configuration
ansible-playbook -i inventory.yml configure_vlans.yml

# Run interface configuration
ansible-playbook -i inventory.yml configure_interfaces.yml
```

### 2. Configure PCs
```bash
# Make script executable and run
chmod +x configure_pcs.sh
./configure_pcs.sh
```

### 3. Manual GNS3 Setup
1. Open GNS3 GUI
2. Create a new project
3. Add devices according to the network diagram
4. Use the generated configurations

## Network Overview

**Departments:** {len(self.config.get('departments', []))}
**VLANs configured:**
"""

    def run(self):
        """
        Main execution method that orchestrates the entire generation process.
        Displays network overview and generates all configuration files.
        """
        print("Network Automation Generator")
        print("=" * 50)
        
        # Display network overview information
        print(f"Network Overview:")
        departments = self.config.get('departments', [])
        print(f"  Departments: {len(departments)}")
        
        # Calculate and display device statistics
        total_devices = 0
        for dept in departments:
            devices = dept.get('devices', {})
            dept_total = sum(devices.values())  # Sum all device types in department
            total_devices += dept_total
            print(f"  {dept['name']}: {dept_total} devices (VLAN {dept['vlan_id']})")
        
        print(f"  Total devices: {total_devices}")
        
        # Generate all configuration files
        self.save_all_files()
        
        # Display next steps for user
        print(f"\nNext Steps:")
        print(f"1. Check the 'network_automation' directory for generated files")
        print(f"2. Create a GNS3 project manually using GNS3 GUI")
        print(f"3. Use the Ansible playbooks to configure your switches")
        print(f"4. Run the PC configuration script on your endpoints")
        print(f"5. Use network_diagram.json for network visualization")
        
        # Display documentation information
        print(f"\nDocumentation:")
        print(f"   All files are documented in network_automation/README.md")
        print(f"   Inventory contains {len(departments)} department networks")
        print(f"   Playbooks ready for Ansible automation")

def main():
    """
    Main function that serves as the entry point for the script.
    Handles initialization, execution, and error management.
    """
    try:
        # Create generator instance and run the automation process
        generator = NetworkAutomationGenerator()
        generator.run()
        
    except KeyboardInterrupt:
        # Handle user cancellation gracefully
        print("\nCancelled by user")
    except Exception as e:
        # Handle and display any unexpected errors
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()  # Print full stack trace for debugging

# Execute main function when script is run directly
if __name__ == "__main__":
    main()