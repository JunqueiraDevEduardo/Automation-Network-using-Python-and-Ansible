#!/usr/bin/env python3
"""
Fixed Network Automation Generator
This script correctly processes your network_data.yml configuration structure
and generates proper Ansible inventory and playbooks for network automation.

The original script expected different field names, but this version works
with your actual configuration structure.
"""

import yaml
import json
from pathlib import Path

def generate_from_your_config():
    """
    Main function that processes your network configuration and generates
    all necessary Ansible automation files including inventory and playbooks.
    """
    print("Loading your configuration...")
    
    # Load your actual network configuration from YAML file
    # This reads the config/network_data.yml file with your department structure
    with open('../config/network_data.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Extract departments list from configuration
    departments = config.get('departments', [])
    print(f"Found {len(departments)} departments")
    
    # Initialize Ansible inventory structure with device type groups
    # This creates the standard Ansible inventory format with host groups
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
    
    # Initialize list to store VLAN configurations for playbook generation
    vlan_config = []
    
    # Process each department from your configuration
    for dept in departments:
        # Extract department information using your config field names
        dept_name = dept.get('name', 'Unknown')
        vlan_id = dept.get('vlan', 1)  # Your config uses 'vlan', not 'vlan_id'
        devices = dept.get('devices', [])
        
        print(f"Processing {dept_name} - VLAN {vlan_id} - {len(devices)} devices")
        
        # Add VLAN configuration for this department
        # Clean up department name for valid VLAN naming
        clean_name = dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
        vlan_config.append({
            'vlan_id': vlan_id,
            'name': clean_name,
            'state': 'active'
        })
        
        # Process each device in the department
        for device in devices:
            device_name = device.get('name', 'unknown')
            device_type = device.get('type', 'unknown')
            device_ip = device.get('ip', '192.168.1.1')
            
            # Categorize devices by type and add to appropriate inventory group
            if device_type == 'switch':
                inventory['all']['children']['switches']['hosts'][device_name] = {
                    'ansible_host': device_ip,
                    'department': dept_name,
                    'vlan_id': vlan_id
                }
            elif device_type == 'router':
                inventory['all']['children']['routers']['hosts'][device_name] = {
                    'ansible_host': device_ip,
                    'department': dept_name,
                    'vlan_id': vlan_id
                }
            elif device_type == 'pc' and not device_name.startswith('server'):
                # Regular PCs (excluding servers that might be marked as 'pc')
                inventory['all']['children']['pcs']['hosts'][device_name] = {
                    'ansible_host': device_ip,
                    'department': dept_name,
                    'vlan_id': vlan_id
                }
            
            # Handle servers (some are marked as 'pc' but have 'server' in name)
            # This catches both explicit servers and server devices marked as other types
            if 'server' in device_name.lower() or device_name.startswith('Server'):
                inventory['all']['children']['servers']['hosts'][device_name] = {
                    'ansible_host': device_ip,
                    'department': dept_name,
                    'vlan_id': vlan_id
                }
    
    # Create output directory for generated files
    Path("network_automation").mkdir(exist_ok=True)
    
    # Save the generated inventory to YAML file
    with open('network_automation/inventory.yml', 'w') as f:
        yaml.dump(inventory, f, default_flow_style=False, indent=2)
    
    # Generate VLAN configuration playbook
    # This creates an Ansible playbook to configure VLANs on all switches
    vlan_playbook = """---
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
    
    # Add each VLAN configuration to the playbook
    for vlan in vlan_config:
        vlan_playbook += f"""          - vlan_id: {vlan['vlan_id']}
            name: "{vlan['name']}"
            state: {vlan['state']}
"""
    
    # Add playbook footer with merge operation and configuration save
    vlan_playbook += """        state: merged
        
    - name: Save configuration
      cisco.ios.ios_config:
        save_when: always
"""
    
    # Save VLAN configuration playbook
    with open('network_automation/configure_vlans.yml', 'w') as f:
        f.write(vlan_playbook)
    
    # Generate interface configuration playbook
    # This creates switch port configurations for end devices
    interface_playbook = """---
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
    port_num = 1  # Start with port 1
    for dept in departments:
        vlan_id = dept.get('vlan', 1)
        devices = dept.get('devices', [])
        
        # Identify devices that need access ports (PCs and servers)
        access_devices = [d for d in devices if d.get('type') in ['pc'] or 'server' in d.get('name', '').lower()]
        
        # Configure access port for each end device
        for device in access_devices:
            interface = f"FastEthernet0/{port_num}"
            interface_playbook += f"""          - name: {interface}
            access:
              vlan: {vlan_id}
"""
            port_num += 1  # Move to next available port
    
    # Add interface playbook footer
    interface_playbook += """        state: merged
        
    - name: Save configuration
      cisco.ios.ios_config:
        save_when: always
"""
    
    # Save interface configuration playbook
    with open('network_automation/configure_interfaces.yml', 'w') as f:
        f.write(interface_playbook)
    
    # Generate PC configuration script for end devices
    pc_script = """#!/bin/bash
# PC Network Configuration Script
# Configures IP addresses and gateways for all department PCs and servers

echo "Configuring PC Network Settings..."

"""
    
    # Add configuration commands for each department
    for dept in departments:
        dept_name = dept.get('name', 'Unknown')
        vlan_id = dept.get('vlan', 1)
        gateway = dept.get('gateway', '192.168.1.1')
        devices = dept.get('devices', [])
        
        pc_script += f"""
# {dept_name} Department (VLAN {vlan_id})
echo "Configuring {dept_name} devices..."
"""
        
        # Add configuration for each PC/server in the department
        for device in devices:
            if device.get('type') == 'pc' or 'server' in device.get('name', '').lower():
                device_name = device.get('name', 'unknown')
                device_ip = device.get('ip', '192.168.1.2')
                
                pc_script += f"""
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
    
    pc_script += """
echo "PC configuration completed!"
echo "Note: Uncomment and modify the appropriate commands for your operating system"
"""
    
    # Save PC configuration script and make it executable
    with open('network_automation/configure_pcs.sh', 'w') as f:
        f.write(pc_script)
    
    # Make the script executable
    import os
    os.chmod('network_automation/configure_pcs.sh', 0o755)
    
    # Generate network diagram data for visualization
    diagram_data = generate_network_diagram(departments)
    with open('network_automation/network_diagram.json', 'w') as f:
        json.dump(diagram_data, f, indent=2)
    
    # Generate README documentation
    readme_content = generate_readme_content(departments, vlan_config)
    with open('network_automation/README.md', 'w') as f:
        f.write(readme_content)
    
    # Print generation summary
    print("Generated files successfully!")
    print(f"- Inventory with {len(departments)} departments")
    print(f"- VLAN config with {len(vlan_config)} VLANs")
    print(f"- Interface config with ports for access devices")
    print(f"- PC configuration script")
    print(f"- Network diagram data")
    print(f"- README documentation")
    
    # Display device summary statistics
    total_switches = len(inventory['all']['children']['switches']['hosts'])
    total_routers = len(inventory['all']['children']['routers']['hosts']) 
    total_pcs = len(inventory['all']['children']['pcs']['hosts'])
    total_servers = len(inventory['all']['children']['servers']['hosts'])
    
    print(f"\nDevice Summary:")
    print(f"- Switches: {total_switches}")
    print(f"- Routers: {total_routers}")
    print(f"- PCs: {total_pcs}")
    print(f"- Servers: {total_servers}")

def generate_network_diagram(departments):
    """
    Generate network topology data for visualization tools.
    Creates nodes and links representing the network structure.
    
    Args:
        departments: List of department configurations
        
    Returns:
        Dictionary containing nodes, links, and VLAN information
    """
    import math
    
    # Initialize diagram data structure
    diagram_data = {
        'nodes': [],  # Network devices and endpoints
        'links': [],  # Connections between devices
        'vlans': {}   # VLAN information for visualization
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
    
    # Position each department switch in a circle around core switch
    for i, dept in enumerate(departments):
        angle = (2 * math.pi * i) / num_depts
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

def generate_readme_content(departments, vlan_config):
    """
    Generate comprehensive README documentation for the automation files.
    
    Args:
        departments: List of department configurations
        vlan_config: List of VLAN configurations
        
    Returns:
        String containing complete README content
    """
    readme = f"""# Network Automation Files

This directory contains automated configuration files generated from your network setup.

## Generated Files

### Inventory
- `inventory.yml` - Ansible inventory with all network devices organized by type

### Playbooks  
- `configure_vlans.yml` - Configures VLANs on network switches
- `configure_interfaces.yml` - Configures switch access ports for end devices

### Scripts
- `configure_pcs.sh` - Shell script to configure PC and server network settings

### Documentation
- `network_diagram.json` - Network topology data for visualization tools
- `README.md` - This documentation file

## Network Overview

**Departments:** {len(departments)}
**VLANs configured:** {len(vlan_config)}

### Department Summary:
"""
    
    # Add department details to README
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

### 1. Deploy Switch Configurations with Ansible

```bash
# Install Ansible and required collections
pip install ansible
ansible-galaxy collection install cisco.ios

# Configure VLANs on all switches
ansible-playbook -i inventory.yml configure_vlans.yml

# Configure switch interfaces  
ansible-playbook -i inventory.yml configure_interfaces.yml
```

### 2. Configure PC Network Settings

Make the script executable and run it:
```bash
chmod +x configure_pcs.sh
./configure_pcs.sh
```

Note: Edit the script to uncomment the appropriate commands for your operating system (Linux or Windows).

### 3. Verify Network Configuration

After running the playbooks, you can verify the configuration:

```bash
# Check VLAN configuration
ansible switches -i inventory.yml -m cisco.ios.ios_command -a "commands='show vlan brief'"

# Check interface configuration  
ansible switches -i inventory.yml -m cisco.ios.ios_command -a "commands='show interfaces status'"

# Test connectivity between departments
ansible pcs -i inventory.yml -m ping -a "dest=<target_ip>"
```

## Network Architecture

The network is structured with:

- **Core Switch**: Central hub connecting all department switches
- **Department Switches**: One per department, connects local devices
- **VLANs**: Isolate traffic by department for security and performance
- **Access Ports**: Connect end devices (PCs/servers) to department switches

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Update ansible_user and ansible_password in playbooks
   - Ensure SSH/Telnet access is configured on switches

2. **VLAN Configuration Issues**
   - Verify VLAN IDs don't conflict with existing VLANs
   - Check that trunk ports are configured between switches

3. **Interface Configuration Issues**
   - Ensure interface names match your switch hardware
   - Update interface naming convention if needed (e.g., GigabitEthernet vs FastEthernet)

4. **PC Configuration Issues**
   - Verify IP addresses don't conflict with existing devices
   - Update gateway addresses to match your network design

### Customization

To customize the configuration:

1. **Modify VLAN IDs**: Update the `vlan` field in your network_data.yml
2. **Change Interface Names**: Edit the interface_playbook section in the generator
3. **Update Credentials**: Modify the vars section in each playbook
4. **Add Device Types**: Extend the device categorization logic in the generator

## Security Considerations

- Change default credentials in playbooks before deployment
- Consider using Ansible Vault for credential management
- Implement proper access controls on network devices
- Regularly update device firmware and security patches

## File Structure

```
network_automation/
├── inventory.yml          # Ansible inventory
├── configure_vlans.yml    # VLAN configuration playbook
├── configure_interfaces.yml # Interface configuration playbook  
├── configure_pcs.sh       # PC network configuration script
├── network_diagram.json   # Network topology data
└── README.md             # This documentation
```

## Support

For issues with this automation:
1. Check the troubleshooting section above
2. Verify your network_data.yml file format
3. Test connectivity to network devices
4. Review Ansible output for specific error messages

## Version History

- v1.0: Initial release with VLAN and interface configuration
- Compatible with Cisco IOS switches
- Supports Linux and Windows PC configuration
"""
    
    return readme

def validate_configuration(config_file='config/network_data.yml'):
    """
    Validate the network configuration file before processing.
    
    Args:
        config_file: Path to the configuration file
        
    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        return False, [f"Configuration file not found: {config_file}"]
    except yaml.YAMLError as e:
        return False, [f"Invalid YAML format: {e}"]
    
    # Check for required top-level structure
    if 'departments' not in config:
        errors.append("Missing 'departments' key in configuration")
        return False, errors
    
    departments = config['departments']
    if not isinstance(departments, list):
        errors.append("'departments' must be a list")
        return False, errors
    
    # Validate each department
    used_vlans = set()
    used_ips = set()
    
    for i, dept in enumerate(departments):
        dept_prefix = f"Department {i+1}"
        
        # Check required fields
        if 'name' not in dept:
            errors.append(f"{dept_prefix}: Missing 'name' field")
        
        if 'vlan' not in dept:
            errors.append(f"{dept_prefix}: Missing 'vlan' field")
        else:
            vlan_id = dept['vlan']
            if not isinstance(vlan_id, int) or vlan_id < 1 or vlan_id > 4094:
                errors.append(f"{dept_prefix}: Invalid VLAN ID {vlan_id} (must be 1-4094)")
            elif vlan_id in used_vlans:
                errors.append(f"{dept_prefix}: Duplicate VLAN ID {vlan_id}")
            else:
                used_vlans.add(vlan_id)
        
        # Check devices
        if 'devices' not in dept:
            errors.append(f"{dept_prefix}: Missing 'devices' field")
        elif not isinstance(dept['devices'], list):
            errors.append(f"{dept_prefix}: 'devices' must be a list")
        else:
            devices = dept['devices']
            for j, device in enumerate(devices):
                device_prefix = f"{dept_prefix}, Device {j+1}"
                
                # Check required device fields
                required_fields = ['name', 'type', 'ip']
                for field in required_fields:
                    if field not in device:
                        errors.append(f"{device_prefix}: Missing '{field}' field")
                
                # Check device type
                if 'type' in device:
                    valid_types = ['switch', 'router', 'pc', 'server']
                    if device['type'] not in valid_types:
                        errors.append(f"{device_prefix}: Invalid device type '{device['type']}' (must be one of {valid_types})")
                
                # Check IP address format and uniqueness
                if 'ip' in device:
                    ip_addr = device['ip']
                    if ip_addr in used_ips:
                        errors.append(f"{device_prefix}: Duplicate IP address {ip_addr}")
                    else:
                        used_ips.add(ip_addr)
                    
                    # Basic IP format validation
                    import re
                    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
                    if not re.match(ip_pattern, ip_addr):
                        errors.append(f"{device_prefix}: Invalid IP address format {ip_addr}")
    
    return len(errors) == 0, errors

def main():
    """
    Main entry point for the network automation generator.
    Validates configuration and generates automation files.
    """
    print("Network Automation Generator Starting...")
    print("=" * 50)
    
    # Validate configuration before processing
    print("Validating configuration...")
    is_valid, errors = validate_configuration()
    
    if not is_valid:
        print("❌ Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease fix the configuration errors and try again.")
        return 1
    
    print("✅ Configuration validation passed")
    
    try:
        # Generate automation files
        generate_from_your_config()
        print("\n✅ Network automation files generated successfully!")
        print("\nNext steps:")
        print("1. Review the generated files in the 'network_automation' directory")
        print("2. Update credentials in the playbook files") 
        print("3. Test the configuration on a lab environment first")
        print("4. Deploy to production network")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating automation files: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())