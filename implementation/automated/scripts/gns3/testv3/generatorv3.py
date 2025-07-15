#!/usr/bin/env python3
"""
TestV3 - Network Creation and Ansible Implementation
Eduardo Junqueira IPVC-ESTG ERSC

TestV3 combines three main functions:
1. Network configuration creation
2. Ansible automation file generation  
3. Ansible playbook execution and implementation
"""

import os                   # OS utilities for file and path handling
import yaml                 # YAML file reading and writing
import json                 # JSON file operations
import subprocess           # Running system processes (e.g., Ansible commands)
from pathlib import Path    # For cross-platform filesystem paths
from typing import Dict, List, Optional    # Type hinting
import logging              # Logging for information and error tracking
from datetime import datetime   # For timestamping reports

# Configure logging for TestV3 operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('testv3_implementation.log'),  # Log to file
        logging.StreamHandler()                            # Log to console
    ]
)
logger = logging.getLogger(__name__)

class NetworkCreatorAndImplementer:
    """
    TestV3 Main Class - Complete Network Automation System
    Handles network creation, Ansible generation, and implementation
    """
    
    def __init__(self):
        """Initialize TestV3 network creator and implementer"""
        # Core data structure for network information
        self.network_data = {
            'departments': [],              # List of each department's network details
            'core_infrastructure': []       # List of core infrastructure devices (switch/router)
        }
        
        # Establish directory structure for output and Ansible files
        self.output_dir = Path("testv3_network_automation")
        self.ansible_dir = self.output_dir / "ansible"
        self.results = []      # Placeholder for any run results
        
        # Mapping device types to Ansible inventory groups
        self.device_types = {
            'switch': 'switches',
            'router': 'routers',
            'pc': 'pcs',
            'server': 'servers',
            'printer': 'printers'
        }
        
        logger.info("TestV3 Network Creator and Implementer initialized")

    def create_network_configuration(self) -> bool:
        """
        Step 1: Create the network configuration.
        Automatically generates network departments, device lists, IPs, VLANs, and core infra.
        """
        print("\nTESTV3 STEP 1: CREATING NETWORK CONFIGURATION")
        print("=" * 50)
        
        try:
            # Get the number of departments to create from the user (default 3)
            num_depts = self.get_input_number("Number of departments for TestV3", "3")
            
            # Create department data for each requested department
            for i in range(num_depts):
                dept = self.create_department_auto(i + 1)
                self.network_data['departments'].append(dept)
                logger.info(f"TestV3 created department: {dept['name']}")
            
            # Define core infrastructure (Switch & Router)
            self.network_data['core_infrastructure'] = [
                {'name': 'TestV3_CoreSwitch', 'type': 'switch', 'ip': '192.168.1.1'},
                {'name': 'TestV3_CoreRouter', 'type': 'router', 'ip': '192.168.1.2'}
            ]
            
            # Save the configuration to YAML for future use
            config_file = "testv3_network_data.yml"
            with open(config_file, 'w') as f:
                yaml.dump(self.network_data, f, default_flow_style=False, indent=2)
            
            print(f"TestV3 network configuration created: {num_depts} departments")
            print(f"TestV3 configuration saved to: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"TestV3 error creating network configuration: {e}")
            return False

    def create_department_auto(self, dept_number: int) -> Dict:
        """
        Automatically creates a single department configuration.
        Devices and addressing are generated based on user input and department number.
        """
        # Assign department name and VLAN based on index
        dept_name = f"TestV3_Department_{dept_number}"
        vlan_id = dept_number * 10
        subnet_base = f"192.168.{vlan_id}"
        
        # Prompt user for number of devices per type in this department
        print(f"\nConfiguring TestV3 {dept_name} (VLAN {vlan_id}):")
        switches = self.get_input_number("  Switches", "1")
        routers = self.get_input_number("  Routers", "1")
        pcs = self.get_input_number("  PCs", "3")
        servers = self.get_input_number("  Servers", "1")
        printers = self.get_input_number("  Printers", "1")
        
        # Build the department's devices list with generated IPs
        devices = []
        ip_counter = 10   # Start at this .x in the subnet
        
        # Switches
        for i in range(switches):
            devices.append({
                'name': f"TestV3_SW_{vlan_id}_{i+1}",
                'type': 'switch',
                'ip': f"{subnet_base}.{ip_counter}"
            })
            ip_counter += 1
        
        # Routers
        for i in range(routers):
            devices.append({
                'name': f"TestV3_R_{vlan_id}_{i+1}",
                'type': 'router',
                'ip': f"{subnet_base}.{ip_counter}"
            })
            ip_counter += 1
        
        # PCs
        for i in range(pcs):
            devices.append({
                'name': f"TestV3_PC_{vlan_id}_{i+1}",
                'type': 'pc',
                'ip': f"{subnet_base}.{ip_counter}"
            })
            ip_counter += 1
        
        # Servers
        for i in range(servers):
            devices.append({
                'name': f"TestV3_SRV_{vlan_id}_{i+1}",
                'type': 'server',
                'ip': f"{subnet_base}.{ip_counter}"
            })
            ip_counter += 1
        
        # Printers
        for i in range(printers):
            devices.append({
                'name': f"TestV3_PRT_{vlan_id}_{i+1}",
                'type': 'printer',
                'ip': f"{subnet_base}.{ip_counter}"
            })
            ip_counter += 1
        
        # Return all department info
        return {
            'name': dept_name,
            'vlan': vlan_id,
            'subnet': f"{subnet_base}.0/24",
            'gateway': f"{subnet_base}.1",
            'devices': devices
        }

    def generate_ansible_files(self) -> bool:
        """
        Step 2: Generate all Ansible files (inventory, playbooks, scripts).
        Automates the creation of the directory structure and relevant files.
        """
        print("\nTESTV3 STEP 2: GENERATING ANSIBLE FILES")
        print("=" * 50)
        try:
            # Ensure all necessary ansible directories exist
            self.create_ansible_directories()
            
            # Generate all the config files and playbooks needed
            self.generate_ansible_cfg()
            self.generate_inventory()
            self.generate_vlan_playbook()
            self.generate_interface_playbook()
            self.generate_pc_script()
            self.generate_main_playbook()
            
            print("TestV3 Ansible files generated successfully")
            return True
        except Exception as e:
            logger.error(f"TestV3 error generating Ansible files: {e}")
            return False

    def create_ansible_directories(self):
        """Create required directories for all Ansible assets."""
        directories = [
            self.output_dir,
            self.ansible_dir,
            self.ansible_dir / "inventories",
            self.ansible_dir / "playbooks",
            self.ansible_dir / "roles" / "testv3-network-config" / "tasks",
            self.ansible_dir / "roles" / "testv3-network-config" / "vars",
            self.ansible_dir / "scripts"
        ]
        # Create each directory, including any parent directories
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def generate_ansible_cfg(self):
        """Create ansible.cfg file for configuring Ansible behavior."""
        config_content = """[defaults]
# TestV3 Ansible Configuration
inventory = inventories/hosts.yml
remote_user = admin
host_key_checking = False
timeout = 30
retry_files_enabled = False
gathering = explicit
stdout_callback = default
deprecation_warnings = False
interpreter_python = auto_silent

[persistent_connection]
# TestV3 network device timeouts
connect_timeout = 30
command_timeout = 30
"""
        with open(self.ansible_dir / "ansible.cfg", 'w') as f:
            f.write(config_content)

    def generate_inventory(self):
        """Creates the Ansible inventory (hosts.yml) for all devices per group."""
        inventory = {
            'all': {
                'children': {
                    'switches': {'hosts': {}},
                    'routers': {'hosts': {}},
                    'pcs': {'hosts': {}},
                    'servers': {'hosts': {}},
                    'printers': {'hosts': {}}
                }
            }
        }
        # For each department, add devices to the relevant group
        for dept in self.network_data['departments']:
            for device in dept['devices']:
                device_info = {
                    'ansible_host': device['ip'],
                    'department': dept['name'],
                    'vlan_id': dept['vlan'],
                    'testv3_device': True
                }
                # Additional vars for network gear
                if device['type'] in ['switch', 'router']:
                    device_info.update({
                        'ansible_network_os': 'ios',
                        'ansible_connection': 'network_cli',
                        'ansible_user': 'admin',
                        'ansible_password': 'admin'
                    })
                else:
                    device_info.update({
                        'ansible_connection': 'ssh',
                        'ansible_user': 'admin'
                    })
                group = self.device_types.get(device['type'], 'others')
                inventory['all']['children'][group]['hosts'][device['name']] = device_info
        # Save full inventory as YAML
        with open(self.ansible_dir / "inventories" / "hosts.yml", 'w') as f:
            yaml.dump(inventory, f, default_flow_style=False, indent=2)

    def generate_vlan_playbook(self):
        """
        Generate the playbook for network VLAN configuration.
        Playbook only simulates the setup (debug output), not live changes.
        """
        playbook = """---
# TestV3 VLAN Configuration Playbook
- name: Configure TestV3 VLANs
  hosts: localhost
  gather_facts: no
  connection: local
  tasks:
    - name: Display TestV3 VLAN configuration
      debug:
        msg: "TestV3 would configure the following VLANs:"
        
    - name: Show TestV3 VLANs
      debug:
        msg: "VLAN {{ item.vlan }} - {{ item.name }}"
      loop:
"""
        # Add each VLAN in this loop
        for dept in self.network_data['departments']:
            vlan_name = dept['name'].replace(' ', '-')
            playbook += f"""        - vlan: {dept['vlan']}
          name: "{vlan_name}"
"""
        playbook += """
    - name: TestV3 configuration simulation completed
      debug:
        msg: "TestV3 VLAN configuration would be applied to switches"
"""
        with open(self.ansible_dir / "playbooks" / "testv3_configure_vlans.yml", 'w') as f:
            f.write(playbook)

    def generate_interface_playbook(self):
        """
        Generate playbook for switch interface assignments.
        Mandates which device is on which switch port and VLAN.
        """
        playbook = """---
# TestV3 Interface Configuration Playbook
- name: Configure TestV3 Interfaces
  hosts: localhost
  gather_facts: no
  connection: local
  tasks:
    - name: Display TestV3 interface configuration
      debug:
        msg: "TestV3 would configure the following interfaces:"
        
    - name: Show TestV3 interfaces
      debug:
        msg: "Interface FastEthernet0/{{ item.port }} - VLAN {{ item.vlan }} - Device {{ item.device }}"
      loop:
"""
        port_num = 1
        for dept in self.network_data['departments']:
            for device in dept['devices']:
                if device['type'] in ['pc', 'server', 'printer']:
                    playbook += f"""        - port: {port_num}
          vlan: {dept['vlan']}
          device: "{device['name']}"
"""
                    port_num += 1
        playbook += """
    - name: TestV3 interface configuration simulation completed
      debug:
        msg: "TestV3 interface configuration would be applied to switches"
"""
        with open(self.ansible_dir / "playbooks" / "testv3_configure_interfaces.yml", 'w') as f:
            f.write(playbook)

    def generate_pc_script(self):
        """
        Generate a bash script template (testv3_configure_pcs.sh)
        for PC/server network interface configuration.
        """
        script = """#!/bin/bash
# TestV3 PC Configuration Script
echo "Configuring TestV3 PC Network Settings..."

"""
        for dept in self.network_data['departments']:
            script += f"""
# TestV3 {dept['name']} (VLAN {dept['vlan']})
echo "Configuring TestV3 {dept['name']} devices..."
"""
            for device in dept['devices']:
                if device['type'] in ['pc', 'server']:
                    script += f"""
# Configure TestV3 {device['name']}
echo "  Setting up TestV3 {device['name']}: {device['ip']}"
# Linux command: sudo ip addr add {device['ip']}/24 dev eth0
# Linux command: sudo ip route add default via {dept['gateway']}
"""
        script += """
echo "TestV3 PC configuration completed"
"""
        with open(self.ansible_dir / "scripts" / "testv3_configure_pcs.sh", 'w') as f:
            f.write(script)
        # Set executable permission for script
        os.chmod(self.ansible_dir / "scripts" / "testv3_configure_pcs.sh", 0o755)

    def generate_main_playbook(self):
        """Create a master playbook to sequentially apply VLAN and interface playbooks."""
        playbook = """---
# TestV3 Main Deployment Playbook
- name: Deploy TestV3 Complete Network Configuration
  hosts: localhost
  gather_facts: no
  tasks:
    - name: Run TestV3 VLAN configuration
      include: testv3_configure_vlans.yml
    
    - name: Run TestV3 interface configuration  
      include: testv3_configure_interfaces.yml
    
    - name: Display TestV3 completion message
      debug:
        msg: "TestV3 network configuration deployment completed successfully"
"""
        with open(self.ansible_dir / "playbooks" / "testv3_deploy_network.yml", 'w') as f:
            f.write(playbook)

    def implement_ansible_configuration(self) -> bool:
        """
        Step 3: Run the Ansible configuration (playbook execution).
        Handles checking for Ansible install, valid inventory, and playbook execution.
        """
        print("\nTESTV3 STEP 3: IMPLEMENTING ANSIBLE CONFIGURATION")
        print("=" * 50)
        try:
            # Change current directory to Ansible directory
            original_dir = os.getcwd()
            os.chdir(self.ansible_dir)
            
            # Check if Ansible is installed on the system
            if not self.check_ansible_installation():
                print("Ansible is not installed for TestV3. Please install it first.")
                os.chdir(original_dir)
                return False
            
            # Validate the Ansible inventory
            if not self.test_inventory():
                print("TestV3 inventory test failed - continuing with simulation mode")
            
            # Run playbooks (syntax-check and execution)
            if not self.execute_playbooks():
                print("TestV3 playbook execution had issues but continuing...")
            
            # Restore the original working directory
            os.chdir(original_dir)
            print("TestV3 Ansible configuration implementation completed")
            return True
        except Exception as e:
            logger.error(f"TestV3 error implementing Ansible configuration: {e}")
            return False

    def check_ansible_installation(self) -> bool:
        """Returns True if Ansible is installed and accessible; otherwise False."""
        try:
            result = subprocess.run(['ansible', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("Ansible is installed for TestV3")
                return True
            else:
                print("Ansible is not installed for TestV3")
                return False
        except Exception as e:
            print(f"TestV3 error checking Ansible: {e}")
            return False

    def test_inventory(self) -> bool:
        """Tests the generated Ansible inventory file for formatting errors."""
        try:
            print("Testing TestV3 inventory...")
            result = subprocess.run(['ansible-inventory', '--list'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("TestV3 inventory is valid")
                return True
            else:
                print(f"TestV3 inventory error: {result.stderr}")
                return False
        except Exception as e:
            print(f"TestV3 error testing inventory: {e}")
            return False

    def execute_playbooks(self) -> bool:
        """
        Runs the generated playbooks with syntax check and user confirmation.
        Handles errors but continues with other playbooks if possible.
        """
        try:
            playbooks = [
                "playbooks/testv3_configure_vlans.yml",
                "playbooks/testv3_configure_interfaces.yml"
            ]
            for playbook in playbooks:
                print(f"\nExecuting TestV3: {playbook}")
                # Syntax check the playbook before execution
                result = subprocess.run([
                    'ansible-playbook', playbook, '--syntax-check'
                ], capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print(f"TestV3 {playbook} syntax check passed")
                    # Ask user before executing each playbook
                    if self.get_user_confirmation(f"Execute TestV3 {playbook}?"):
                        result = subprocess.run([
                            'ansible-playbook', playbook,
                            '--connection=local', '--verbose'
                        ], capture_output=True, text=True, timeout=300)
                        if result.returncode == 0:
                            print(f"TestV3 {playbook} executed successfully")
                        else:
                            print(f"TestV3 {playbook} failed")
                            print(f"Error output: {result.stderr}")
                            print(f"Standard output: {result.stdout}")
                            continue
                else:
                    print(f"TestV3 {playbook} syntax check failed")
                    print(f"Error: {result.stderr}")
                    continue
            return True
        except Exception as e:
            logger.error(f"TestV3 error executing playbooks: {e}")
            return False

    def generate_report(self):
        """
        Generates a summary report of the project, counting device types and generated files.
        Report is printed and saved as JSON.
        """
        print("\nTESTV3 IMPLEMENTATION REPORT")
        print("=" * 40)
        device_counts = {}
        total_devices = 0
        for dept in self.network_data['departments']:
            for device in dept['devices']:
                device_type = device['type']
                device_counts[device_type] = device_counts.get(device_type, 0) + 1
                total_devices += 1
        print(f"TestV3 Departments Created: {len(self.network_data['departments'])}")
        print(f"TestV3 Total Devices: {total_devices}")
        print(f"TestV3 Device Breakdown:")
        for device_type, count in device_counts.items():
            print(f"  - {device_type.title()}s: {count}")
        print(f"\nTestV3 Files Generated:")
        print(f"  - Network Config: testv3_network_data.yml")
        print(f"  - Ansible Directory: {self.ansible_dir}")
        print(f"  - Inventory: inventories/hosts.yml")
        print(f"  - Playbooks: playbooks/")
        print(f"  - Scripts: scripts/")
        # Save report as JSON
        report_data = {
            'testv3_version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'departments': len(self.network_data['departments']),
            'total_devices': total_devices,
            'device_counts': device_counts,
            'status': 'testv3_completed'
        }
        with open(self.output_dir / "testv3_implementation_report.json", 'w') as f:
            json.dump(report_data, f, indent=2)
        print(f"\nTestV3 report saved to: {self.output_dir}/testv3_implementation_report.json")

    def get_input_number(self, prompt: str, default: str) -> int:
        """Prompt user for a number with default fallback (for device counts)."""
        try:
            value = input(f"{prompt} [{default}]: ").strip()
            return int(value) if value else int(default)
        except:
            return int(default)

    def get_user_confirmation(self, prompt: str) -> bool:
        """Prompt user for yes/no (y/n) confirmation, default is yes."""
        response = input(f"{prompt} (y/n) [y]: ").strip().lower()
        return response in ['y', 'yes', ''] or response == 'y'

    def run(self):
        """
        Main orchestrator method for the project.
        Executes the three TestV3 phases in order, with user confirmation at key steps.
        """
        print("=" * 60)
        print("TESTV3: NETWORK CREATION AND ANSIBLE IMPLEMENTATION")
        print("=" * 60)
        try:
            if not self.create_network_configuration():
                print("TestV3 failed to create network configuration")
                return
            if not self.generate_ansible_files():
                print("TestV3 failed to generate Ansible files")
                return
            if self.get_user_confirmation("Proceed with TestV3 Ansible implementation?"):
                if not self.implement_ansible_configuration():
                    print("TestV3 failed to implement Ansible configuration")
                    return
            self.generate_report()
            print("\n" + "=" * 60)
            print("TESTV3 COMPLETED SUCCESSFULLY")
            print("=" * 60)
        except KeyboardInterrupt:
            print("\nTestV3 operation cancelled by user")
        except Exception as e:
            logger.error(f"TestV3 unexpected error: {e}")
            print(f"TestV3 error: {e}")

def main():
    """Entry point for TestV3 execution."""
    creator = NetworkCreatorAndImplementer()
    creator.run()

if __name__ == "__main__":
    main()
