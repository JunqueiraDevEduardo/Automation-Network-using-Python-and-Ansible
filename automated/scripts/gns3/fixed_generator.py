"""
Network Automation Generator:
All HTTP codes are here:https://umbraco.com/knowledge-base/http-status-codes/

This script correctly processes network_data.yml configuration structure, 
this structure was equals to the same structure of the manual network
and generates proper Ansible inventory and playbooks for network automation.
"""
##################################
#Imports
##################################
import yaml
import json
from pathlib import Path
import math
import os

class NetworkAutomationGenerator:
    """
    Main class responsible for converting network configurations into
    automated deployment files. Generates Ansible inventories, playbooks,
    configuration scripts, and network topology data.
    """
    
    def __init__(self, config_file: str = "config/network_data.yml"):
        """
        Initialize the generator with configuration file path.
        Sets up data structures for storing device, VLAN, and network information.
        """
        self.config_file = config_file
        self.load_config()
        
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
            # Try the provided path first
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                print(f"Configuration loaded from {self.config_file}")
                return
            
            # Try alternative paths if the provided path doesn't work
            possible_paths = [
                Path(__file__).parent.parent.parent / 'config' / 'network_data.yml',
                Path('automated/config/network_data.yml'),
                Path('config/network_data.yml'),
                Path('../config/network_data.yml')
            ]
            
            for path in possible_paths:
                if path.exists():
                    with open(path, 'r') as f:
                        self.config = yaml.safe_load(f)
                    print(f"Configuration loaded from {path}")
                    return
            
            # If no file found, create default configuration
            print(f"Configuration file {self.config_file} not found")
            self.config = {"departments": []}
            
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}")
            self.config = {"departments": []}
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.config = {"departments": []}

    def generate_network_inventory(self) -> dict:
        """
        Generate Ansible inventory structure from department configuration.
        Creates organized inventory with switches, routers, PCs, and servers.
        """
        departments = self.config.get('departments', [])
        
        # Initialize Ansible inventory structure with device type groups
        inventory = {
            'all': {
                'children': {
                    'switches': {'hosts': {}},
                    'routers': {'hosts': {}},
                    'pcs': {'hosts': {}},
                    'servers': {'hosts': {}}
                }
            }
        }
        
        # Process each department from configuration
        for dept in departments:
            dept_name = dept.get('name', 'Unknown')
            vlan_id = dept.get('vlan', 1)
            devices = dept.get('devices', [])
            
            # Process each device in the department
            for device in devices:
                device_name = device.get('name', 'unknown')
                device_type = device.get('type', 'unknown')
                device_ip = device.get('ip', '192.168.1.1')
                
                device_info = {
                    'ansible_host': device_ip,
                    'department': dept_name,
                    'vlan_id': vlan_id
                }
                
                # Categorize devices by type
                if device_type == 'switch':
                    inventory['all']['children']['switches']['hosts'][device_name] = device_info
                elif device_type == 'router':
                    inventory['all']['children']['routers']['hosts'][device_name] = device_info
                elif device_type == 'pc' and not device_name.startswith('server'):
                    inventory['all']['children']['pcs']['hosts'][device_name] = device_info
                
                # Handle servers
                if 'server' in device_name.lower() or device_name.startswith('Server'):
                    inventory['all']['children']['servers']['hosts'][device_name] = device_info
        
        return inventory

    def generate_vlan_config_playbook(self) -> str:
        """
        Generate Ansible playbook for configuring VLANs on network switches.
        """
        departments = self.config.get('departments', [])
        
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
        for dept in departments:
            vlan_id = dept.get('vlan', 1)
            clean_name = dept.get('name', 'Unknown').replace('/', '-').replace(' ', '-').replace('&', 'and')
            
            playbook += f"""          - vlan_id: {vlan_id}
            name: "{clean_name}"
            state: active
"""
        
        playbook += """        state: merged
        
    - name: Save configuration
      cisco.ios.ios_config:
        save_when: always
"""
        
        return playbook

    def generate_interface_config_playbook(self) -> str:
        """
        Generate Ansible playbook for configuring switch interfaces.
        """
        departments = self.config.get('departments', [])
        
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
        
        # Add interface configurations for access devices
        port_num = 1
        for dept in departments:
            vlan_id = dept.get('vlan', 1)
            devices = dept.get('devices', [])
            
            # Identify devices that need access ports
            access_devices = [d for d in devices if d.get('type') in ['pc'] or 'server' in d.get('name', '').lower()]
            
            for device in access_devices:
                interface = f"FastEthernet0/{port_num}"
                playbook += f"""          - name: {interface}
            access:
              vlan: {vlan_id}
"""
                port_num += 1
        
        playbook += """        state: merged
        
    - name: Save configuration
      cisco.ios.ios_config:
        save_when: always
"""
        
        return playbook

    def generate_pc_config_script(self) -> str:
        """
        Generate bash script for configuring PC network settings.
        """
        departments = self.config.get('departments', [])
        
        script = """#!/bin/bash
# PC Network Configuration Script
# Configures IP addresses and gateways for all department PCs and servers

echo "Configuring PC Network Settings..."

"""
        
        for dept in departments:
            dept_name = dept.get('name', 'Unknown')
            vlan_id = dept.get('vlan', 1)
            gateway = dept.get('gateway', '192.168.1.1')
            devices = dept.get('devices', [])
            
            script += f"""
# {dept_name} Department (VLAN {vlan_id})
echo "Configuring {dept_name} devices..."
"""
            
            for device in devices:
                if device.get('type') == 'pc' or 'server' in device.get('name', '').lower():
                    device_name = device.get('name', 'unknown')
                    device_ip = device.get('ip', '192.168.1.2')
                    
                    script += f"""
# Configure {device_name}
echo "  Setting up {device_name}: {device_ip}"
# For Ubuntu/Linux systems:
# sudo ip addr add {device_ip}/24 dev eth0
# sudo ip route add default via {gateway}
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static {device_ip} 255.255.255.0 {gateway}
# netsh interface ip set dns "Ethernet" static 8.8.8.8
"""
        
        script += """
echo "PC configuration completed!"
echo "Note: Uncomment and modify the appropriate commands for operating system"
"""
        
        return script

    def generate_network_diagram_data(self) -> dict:
        """
        Generate JSON data for network topology visualization.
        """
        departments = self.config.get('departments', [])
        
        diagram_data = {
            'nodes': [],
            'links': [],
            'vlans': {}
        }
        
        # Add central core switch
        diagram_data['nodes'].append({
            'id': 'CoreSwitch',
            'label': 'Core Switch',
            'type': 'switch',
            'x': 0,
            'y': 0,
            'color': '#FF6B6B'
        })
        
        # Calculate circular layout for departments
        num_depts = len(departments)
        radius = 300
        
        for i, dept in enumerate(departments):
            angle = (2 * math.pi * i) / num_depts if num_depts > 0 else 0
            x = int(radius * math.cos(angle))
            y = int(radius * math.sin(angle))
            
            dept_name = dept.get('name', 'Unknown')
            vlan_id = dept.get('vlan', 1)
            
            # Find department switch from devices
            dept_switch = None
            for device in dept.get('devices', []):
                if device.get('type') == 'switch' and not 'Server' in device.get('name', ''):
                    dept_switch = device
                    break
            
            if dept_switch:
                switch_id = dept_switch.get('name', f'SW-{i}')
                diagram_data['nodes'].append({
                    'id': switch_id,
                    'label': f"{switch_id}\n{dept_name}",
                    'type': 'switch',
                    'x': x,
                    'y': y,
                    'color': '#4ECDC4',
                    'vlan': vlan_id
                })
                
                # Link to core switch
                diagram_data['links'].append({
                    'source': 'CoreSwitch',
                    'target': switch_id,
                    'type': 'trunk',
                    'vlan': vlan_id
                })
            
            # Store VLAN information
            diagram_data['vlans'][vlan_id] = {
                'name': dept_name,
                'network': dept.get('subnet', '192.168.1.0/24'),
                'gateway': dept.get('gateway', '192.168.1.1'),
                'color': '#4ECDC4'
            }
        
        return diagram_data

    def generate_readme(self) -> str:
        """
        Generate README documentation file with usage instructions.
        """
        departments = self.config.get('departments', [])
        
        readme = f"""# Network Automation Files

This directory contains automated configuration files generated from network setup.

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

## Network Overview

**Departments:** {len(departments)}

### Department Summary:
"""
        
        for dept in departments:
            dept_name = dept.get('name', 'Unknown')
            vlan_id = dept.get('vlan', 1)
            subnet = dept.get('subnet', 'N/A')
            device_count = len(dept.get('devices', []))
            
            readme += f"""
- **{dept_name}**
  - VLAN: {vlan_id}
  - Subnet: {subnet}
  - Devices: {device_count}
"""
        
        readme += """
## Usage Instructions

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

This automation was generated from  network configuration file.
"""
        
        return readme

    def save_all_files(self):
        """
        Save all generated configuration files to the output directory.
        Creates inventory, playbooks, scripts, and documentation files.
        """
        print("\nSaving automation files...")
        
        # Create output directory for generated files
        output_dir = Path(__file__).parent / "network_automation"
        output_dir.mkdir(exist_ok=True)
        
        # Generate and save all files
        inventory = self.generate_network_inventory()
        with open(output_dir / "inventory.yml", 'w') as f:
            yaml.dump(inventory, f, default_flow_style=False, indent=2)
        print("Saved inventory.yml")
        
        vlan_playbook = self.generate_vlan_config_playbook()
        with open(output_dir / "configure_vlans.yml", 'w') as f:
            f.write(vlan_playbook)
        print("Saved configure_vlans.yml")
        
        interface_playbook = self.generate_interface_config_playbook()
        with open(output_dir / "configure_interfaces.yml", 'w') as f:
            f.write(interface_playbook)
        print("Saved configure_interfaces.yml")
        
        pc_script = self.generate_pc_config_script()
        with open(output_dir / "configure_pcs.sh", 'w') as f:
            f.write(pc_script)
        os.chmod(output_dir / "configure_pcs.sh", 0o755)
        print("Saved configure_pcs.sh")
        
        diagram_data = self.generate_network_diagram_data()
        with open(output_dir / "network_diagram.json", 'w') as f:
            json.dump(diagram_data, f, indent=2)
        print("Saved network_diagram.json")
        
        readme_content = self.generate_readme()
        with open(output_dir / "README.md", 'w') as f:
            f.write(readme_content)
        print("Saved README.md")
        
        print(f"\nAll files saved to '{output_dir}' directory")

    def run(self):
        """
        Main execution method that orchestrates the entire generation process.
        Displays network overview and generates all configuration files.
        """
        print("Network Automation Generator")
        print("=" * 50)
        
        departments = self.config.get('departments', [])
        print(f"Network Overview:")
        print(f"  Departments: {len(departments)}")
        
        total_devices = 0
        for dept in departments:
            devices = dept.get('devices', [])
            dept_total = len(devices)
            total_devices += dept_total
            print(f"  {dept['name']}: {dept_total} devices (VLAN {dept['vlan']})")
        
        print(f"  Total devices: {total_devices}")
        
        # Generate all configuration files
        self.save_all_files()
        
        print(f"\nNext Steps:")
        print(f"1. Check the 'network_automation' directory for generated files")
        print(f"2. Use the Ansible playbooks to configure  switches")
        print(f"3. Run the PC configuration script on  endpoints")

# Keep the main function for standalone execution
def main():
    """
    Main function that serves as the entry point for the script.
    """
    try:
        generator = NetworkAutomationGenerator()
        generator.run()
    except KeyboardInterrupt:
        print("\nCancelled by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()