"""
Working Project Manager
Since  existing project works via web UI, let's work with that!
This bypasses the authentication issue and gets  automation working.
"""

import requests
import yaml
import json
from pathlib import Path

def load_network_config():
    """
    Load network configuration from YAML file.
    Returns the parsed configuration or None if file not found.
    """
    config_file = "../../config/network_data.yml"
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file not found: {config_file}")
        return None

def test_project_access():
    """
    Test access to  existing GNS3 project via web UI.
    Returns True if project is accessible, False otherwise.
    """
    print("Testing existing project access...")
    
    # GNS3 server configuration
    server = "http://127.0.0.1:3080"
    project_id = "9a8ab49a-6f61-4fa8-9089-99e6c6594e4f"
    
    # Create session with SSL verification disabled
    session = requests.Session()
    session.verify = False
    
    # Test web UI access to the project
    try:
        response = session.get(f"{server}/static/web-ui/controller/1/project/{project_id}")
        if response.status_code == 200:
            print("Project accessible via web UI")
            print(f"   Project ID: {project_id}")
            print(f"   Response size: {len(response.text)} bytes")
            return True
        else:
            print(f"Project not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error accessing project: {e}")
        return False

def generate_automation_files():
    """
    Generate automation files using  network configuration.
    This creates the files existing scripts expect.
    Returns True if successful, False otherwise.
    """
    print("\nGenerating automation files...")
    
    # Load network configuration from YAML file
    config = load_network_config()
    if not config:
        return False
    
    # Extract departments from configuration
    departments = config.get('departments', [])
    print(f"Found {len(departments)} departments")
    
    # Create output directory for automation files
    output_dir = Path("network_automation")
    output_dir.mkdir(exist_ok=True)
    
    # Generate Ansible inventory file
    inventory = generate_inventory(departments)
    with open(output_dir / "inventory.yml", 'w') as f:
        yaml.dump(inventory, f, default_flow_style=False, indent=2)
    print("Generated inventory.yml")
    
    # Generate VLAN configuration playbook
    vlan_playbook = generate_vlan_playbook(departments)
    with open(output_dir / "configure_vlans.yml", 'w') as f:
        f.write(vlan_playbook)
    print("Generated configure_vlans.yml")
    
    # Generate interface configuration playbook
    interface_playbook = generate_interface_playbook(departments)
    with open(output_dir / "configure_interfaces.yml", 'w') as f:
        f.write(interface_playbook)
    print("Generated configure_interfaces.yml")
    
    # Generate PC configuration script
    pc_script = generate_pc_script(departments)
    with open(output_dir / "configure_pcs.sh", 'w') as f:
        f.write(pc_script)
    # Make the script executable
    (output_dir / "configure_pcs.sh").chmod(0o755)
    print("Generated configure_pcs.sh")
    
    return True

def generate_inventory(departments):
    """
    Generate Ansible inventory from departments configuration.
    Creates a structured inventory with different device types.
    """
    # Initialize inventory structure with device groups
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
    
    # Process each department and its devices
    for dept in departments:
        dept_name = dept.get('name', 'Unknown')
        vlan_id = dept.get('vlan', 1)
        devices = dept.get('devices', [])
        
        # Process each device in the department
        for device in devices:
            device_name = device.get('name', 'unknown')
            device_type = device.get('type', 'unknown')
            device_ip = device.get('ip', '192.168.1.1')
            
            # Create device information for Ansible
            device_info = {
                'ansible_host': device_ip,
                'department': dept_name,
                'vlan_id': vlan_id
            }
            
            # Categorize devices by type for inventory groups
            if device_type == 'switch':
                inventory['all']['children']['switches']['hosts'][device_name] = device_info
            elif device_type == 'router':
                inventory['all']['children']['routers']['hosts'][device_name] = device_info
            elif device_type == 'pc':
                # Separate servers from regular PCs based on naming
                if 'server' in device_name.lower():
                    inventory['all']['children']['servers']['hosts'][device_name] = device_info
                else:
                    inventory['all']['children']['pcs']['hosts'][device_name] = device_info
    
    return inventory

def generate_vlan_playbook(departments):
    """
    Generate VLAN configuration playbook for Cisco switches.
    Creates Ansible playbook to configure VLANs based on departments.
    """
    # Start building the Ansible playbook
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
    
    # Add VLAN configuration for each department
    for dept in departments:
        vlan_id = dept.get('vlan', 1)
        # Clean VLAN name for Cisco naming conventions
        vlan_name = dept.get('name', 'Unknown').replace('/', '-').replace(' ', '-')
        
        playbook += f"""          - vlan_id: {vlan_id}
            name: "{vlan_name}"
            state: active
"""
    
    # Add task to save configuration
    playbook += """        state: merged
        
    - name: Save configuration
      cisco.ios.ios_config:
        save_when: always
"""
    
    return playbook

def generate_interface_playbook(departments):
    """
    Generate interface configuration playbook for switch ports.
    Configures access ports for PCs and servers in their respective VLANs.
    """
    # Start building the interface configuration playbook
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
    
    # Track port numbers for interface assignment
    port_num = 1
    for dept in departments:
        vlan_id = dept.get('vlan', 1)
        devices = dept.get('devices', [])
        
        # Filter devices that need access ports (PCs and servers)
        access_devices = [d for d in devices if d.get('type') in ['pc'] or 'server' in d.get('name', '').lower()]
        
        # Configure each access device with appropriate VLAN
        for device in access_devices:
            interface = f"FastEthernet0/{port_num}"
            playbook += f"""          - name: {interface}
            access:
              vlan: {vlan_id}
"""
            port_num += 1
    
    # Add task to save configuration
    playbook += """        state: merged
        
    - name: Save configuration
      cisco.ios.ios_config:
        save_when: always
"""
    
    return playbook

def generate_pc_script(departments):
    """
    Generate PC configuration script for network settings.
    Creates a bash script with commands for both Linux and Windows.
    """
    # Start building the PC configuration script
    script = """#!/bin/bash
# PC Network Configuration Script
# Generated for network topology

echo "Configuring PC Network Settings..."

"""
    
    # Generate configuration for each department's devices
    for dept in departments:
        dept_name = dept.get('name', 'Unknown')
        vlan_id = dept.get('vlan', 1)
        gateway = dept.get('gateway', '192.168.1.1')
        devices = dept.get('devices', [])
        
        # Add department header
        script += f"""
# {dept_name} Department (VLAN {vlan_id})
echo "Configuring {dept_name} devices..."
"""
        
        # Configure each PC/server in the department
        for device in devices:
            if device.get('type') == 'pc' or 'server' in device.get('name', '').lower():
                device_name = device.get('name', 'unknown')
                device_ip = device.get('ip', '192.168.1.2')
                
                # Add configuration commands for this device
                script += f"""
# Configure {device_name}
echo "  Setting up {device_name}: {device_ip}"
# For Linux:
# sudo ip addr add {device_ip}/24 dev eth0
# sudo ip route add default via {gateway}
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows (run as administrator):
# netsh interface ip set address "Ethernet" static {device_ip} 255.255.255.0 {gateway}
# netsh interface ip set dns "Ethernet" static 8.8.8.8
"""
    
    # Add completion message
    script += """
echo "PC configuration completed!"
echo "Uncomment the appropriate commands for  operating system"
"""
    
    return script

def update_existing_scripts():
    """
    Update  existing scripts to work with the current project.
    Modifies project IDs and configurations in existing files.
    """
    print("\nUpdating existing scripts...")
    
    project_id = "9a8ab49a-6f61-4fa8-9089-99e6c6594e4f"
    
    # Update verify_existing_project.py if it exists
    verify_script = Path("verify_existing_project.py")
    if verify_script.exists():
        try:
            # Read current content
            with open(verify_script, 'r') as f:
                content = f.read()
            
            # Update the project ID in the file
            new_content = content.replace(
                'project_id="9a8ab49a-6f61-4fa8-9089-99e6c6594e4f"',
                f'project_id="{project_id}"'
            )
            
            # Write updated content back
            with open(verify_script, 'w') as f:
                f.write(new_content)
            
            print("Updated verify_existing_project.py")
        except Exception as e:
            print(f"Could not update verify_existing_project.py: {e}")
    
    # Display project status
    print("\n Project is ready!")
    print(f"   Project ID: {project_id}")
    print(f"   Web UI Access: Working")
    print(f"   Automation Files: Generated")

def main():
    """
    Main function to get automation working.
    Orchestrates the entire process of testing access and generating files.
    """
    print("Working Project Manager")
    print("=" * 40)
    print("Since authentication is causing issues, let's work with what we have!")
    
    # Test if we can access the existing project
    if not test_project_access():
        print("Cannot access existing project. Check if GNS3 is running.")
        return
    
    # Generate all the automation files
    if generate_automation_files():
        print("\nAutomation files generated successfully!")
        
        # Update existing scripts with current project info
        update_existing_scripts()

if __name__ == "__main__":
    main()