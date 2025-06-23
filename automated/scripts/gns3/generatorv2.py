"""
Project 2 Eduardo Junqueira IPVC-ESTG ERSC
Network Automation Generator V2
Reads network_data.yml and generates complete Ansible automation structure
Creates proper inventory, playbooks, roles, and configuration files
"""

import yaml
import os
from pathlib import Path

class NetworkAutomationGenerator:
    """
    Main generator class that converts network_data.yml into complete Ansible automation
    Creates proper directory structure, inventory, playbooks, and configuration files
    All templates embedded in code - no external template files needed
    """
    def __init__(self, network_data_file: str = "network_data.yml"):
        """
        Initialize Network Automation Generator
        """
        
        # File and directory configuration
        self.network_data_file = network_data_file
        self.output_dir = "ansibleconf"
        
        # Data containers - populated when loading YAML configuration
        self.network_data = None
        self.departments = []
        self.core_infrastructure = []
        
        # Ansible inventory grouping - maps device types to Ansible groups
        self.device_type_mapping = {
            'switch': 'switches',
            'router': 'routers',
            'pc': 'pcs',
            'lp': 'pcs',        # Laptops grouped with PCs
            'server': 'servers',
            'printer': 'printers'
        }

    def load_network_data(self):
        """
        Load network configuration from YAML file.
        """
        try:
            # Check if configuration file exists
            if not os.path.exists(self.network_data_file):
                print(f"Error: Network data file {self.network_data_file} not found")
                return False
            
            # Load and parse YAML file
            with open(self.network_data_file, 'r') as f:
                self.network_data = yaml.safe_load(f)
            
            # Validate loaded data structure
            if not isinstance(self.network_data, dict):
                print("Error: Invalid YAML structure - expected dictionary")
                return False
            
            # Extract network components
            self.departments = self.network_data.get('departments', [])
            self.core_infrastructure = self.network_data.get('core_infrastructure', [])
            
            # Validate extracted data
            if not self.departments:
                print("Warning: No departments found in configuration")
            
            print(f"Loaded: {len(self.departments)} departments, {len(self.core_infrastructure)} core devices")
            return True
            
        except yaml.YAMLError as e:
            print(f"YAML parsing error: {e}")
            return False
        except Exception as e:
            print(f"File loading error: {e}")
            return False

    def create_directory_structure(self):
        """
        Create folders for network automation files.
        FIXED: Now creates all required directories including group_vars
        """
        
        # Main folder - holds all automation files
        Path(self.output_dir).mkdir(exist_ok=True)
        
        # Inventories folder - device lists with IPs
        Path(self.output_dir + "/inventories").mkdir(exist_ok=True)
        
        # Playbooks folder - automation scripts
        Path(self.output_dir + "/playbooks").mkdir(exist_ok=True)
        
        # FIXED: Create group_vars directory
        Path(self.output_dir + "/group_vars").mkdir(exist_ok=True)
        
        # Tasks folder - Cisco commands for switch and router configuration
        Path(self.output_dir + "/roles/network-config/tasks").mkdir(parents=True, exist_ok=True)
        
        # Variables folder - VLAN numbers and IP address ranges
        Path(self.output_dir + "/roles/network-config/vars").mkdir(exist_ok=True)
        
        # Handlers folder - for service restarts
        Path(self.output_dir + "/roles/network-config/handlers").mkdir(exist_ok=True)
        
        print(f"Created network automation folders in {self.output_dir}")

    def generate_ansible_cfg(self):
        """
        Generate ansible.cfg file with network device settings.
        """
        
        config_content = """[defaults]
# Basic Ansible settings for network automation
inventory = inventories/hosts.yml
remote_user = admin
host_key_checking = False
timeout = 30
retry_files_enabled = False
gathering = explicit
stdout_callback = yaml
forks = 10

[persistent_connection]
# Network device connection timeouts
connect_timeout = 30
command_timeout = 30

[ssh_connection]
# SSH optimization for network devices
ssh_args = -o ControlMaster=auto -o ControlPersist=60s -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
pipelining = True

[privilege_escalation]
# Enable mode for network devices
become = True
become_method = enable
become_user = admin
become_ask_pass = False
"""
        
        # Write configuration file to output directory
        with open(f"{self.output_dir}/ansible.cfg", 'w') as f:
            f.write(config_content)
        
        print("Generated ansible.cfg for network device automation")

    def generate_inventory(self):
        """
        Generate Ansible inventory from network_data.yml
        Uses only real values from network configuration
        """
        # Initialize basic inventory structure with device type groups
        inventory = {
            'all': {
                'children': {
                    'switches': {'hosts': {}},
                    'routers': {'hosts': {}},
                    'pcs': {'hosts': {}},
                    'servers': {'hosts': {}},
                    'printers': {'hosts': {}},
                    'core_infrastructure': {'hosts': {}}
                }
            }
        }
        
        # Process core infrastructure devices
        for device in self.core_infrastructure:
            device_name = device['name']
            device_info = {
                'ansible_host': device['ip'],
                'device_type': device['type'],
                'department': 'core'
            }
            inventory['all']['children']['core_infrastructure']['hosts'][device_name] = device_info
        
        # Process each department using only real values
        for dept in self.departments:
            dept_name = dept['name']
            vlan_id = dept['vlan']
            subnet = dept['subnet']
            gateway = dept['gateway']
            devices = dept.get('devices', [])
            
            # Create department-specific group
            dept_group_name = f"dept_{vlan_id}"
            inventory['all']['children'][dept_group_name] = {
                'hosts': {},
                'vars': {
                    'department': dept_name,
                    'vlan_id': vlan_id,
                    'subnet': subnet,
                    'gateway': gateway
                }
            }
            
            # Process each device in the department
            for device in devices:
                device_name = device['name']
                device_type = device['type']
                device_ip = device['ip']
                
                # Create device information with real values
                device_info = {
                    'ansible_host': device_ip,
                    'device_type': device_type,
                    'department': dept_name,
                    'vlan_id': vlan_id,
                    'subnet': subnet,
                    'gateway': gateway
                }
                
                # Add connection settings based on device type
                if device_type in ['switch', 'router']:
                    device_info.update({
                        'ansible_network_os': 'ios',
                        'ansible_connection': 'network_cli',
                        'ansible_user': 'admin',
                        'ansible_password': 'admin',
                        'ansible_become': 'yes',
                        'ansible_become_method': 'enable'
                    })
                elif device_type in ['pc', 'server', 'printer']:
                    device_info.update({
                        'ansible_connection': 'ssh',
                        'ansible_user': 'admin',
                        'ansible_become': 'yes',
                        'ansible_become_method': 'sudo'
                    })
                
                # Place device in correct group
                if device_type in self.device_type_mapping:
                    group_name = self.device_type_mapping[device_type]
                    inventory['all']['children'][group_name]['hosts'][device_name] = device_info
                else:
                    print(f"Warning: Unknown device type '{device_type}' for device '{device_name}'")
                
                # Also add device to its department group
                inventory['all']['children'][dept_group_name]['hosts'][device_name] = device_info
        
        # Save inventory file
        with open(f"{self.output_dir}/inventories/hosts.yml", 'w') as f:
            yaml.dump(inventory, f, default_flow_style=False, indent=2, sort_keys=False)
        
        # Count total devices for confirmation
        total_devices = sum(len(group['hosts']) for group in inventory['all']['children'].values())
        print(f"Generated inventory: {total_devices} devices in {self.output_dir}/inventories/hosts.yml")

    def generate_group_department(self):
        """
        Generate group variables for device types and departments
        FIXED: Now writes to the correct group_vars directory
        """
        
        # Variables for switches group
        switches_vars = {
            'ansible_network_os': 'ios',
            'ansible_connection': 'network_cli',
            'ansible_user': 'admin',
            'ansible_password': 'admin',
            'ansible_become': 'yes',
            'ansible_become_method': 'enable',
            'dns_servers': ['8.8.8.8', '8.8.4.4'],
            'domain_name': 'company.local'
        }
        
        with open(f"{self.output_dir}/group_vars/switches.yml", 'w') as f:
            yaml.dump(switches_vars, f, default_flow_style=False, indent=2)
        
        # Variables for routers group
        routers_vars = {
            'ansible_network_os': 'ios',
            'ansible_connection': 'network_cli',
            'ansible_user': 'admin',
            'ansible_password': 'admin',
            'ansible_become': 'yes',
            'ansible_become_method': 'enable',
            'dns_servers': ['8.8.8.8', '8.8.4.4'],
            'domain_name': 'company.local'
        }
        
        with open(f"{self.output_dir}/group_vars/routers.yml", 'w') as f:
            yaml.dump(routers_vars, f, default_flow_style=False, indent=2)
        
        # Variables for PCs group
        pcs_vars = {
            'ansible_connection': 'ssh',
            'ansible_user': 'admin',
            'ansible_become': 'yes',
            'ansible_become_method': 'sudo',
            'dns_servers': ['8.8.8.8', '8.8.4.4'],
            'domain_name': 'company.local'
        }
        
        with open(f"{self.output_dir}/group_vars/pcs.yml", 'w') as f:
            yaml.dump(pcs_vars, f, default_flow_style=False, indent=2)
        
        # Variables for servers group
        servers_vars = {
            'ansible_connection': 'ssh',
            'ansible_user': 'admin',
            'ansible_become': 'yes',
            'ansible_become_method': 'sudo',
            'dns_servers': ['8.8.8.8', '8.8.4.4'],
            'domain_name': 'company.local'
        }
        
        with open(f"{self.output_dir}/group_vars/servers.yml", 'w') as f:
            yaml.dump(servers_vars, f, default_flow_style=False, indent=2)
        
        # Variables for printers group
        printers_vars = {
            'ansible_connection': 'ssh',
            'ansible_user': 'admin',
            'ansible_become': 'yes',
            'ansible_become_method': 'sudo',
            'dns_servers': ['8.8.8.8', '8.8.4.4'],
            'domain_name': 'company.local'
        }
        
        with open(f"{self.output_dir}/group_vars/printers.yml", 'w') as f:
            yaml.dump(printers_vars, f, default_flow_style=False, indent=2)
        
        # Variables for core infrastructure
        core_vars = {
            'ansible_network_os': 'ios',
            'ansible_connection': 'network_cli',
            'ansible_user': 'admin',
            'ansible_password': 'admin',
            'ansible_become': 'yes',
            'ansible_become_method': 'enable',
            'dns_servers': ['8.8.8.8', '8.8.4.4'],
            'domain_name': 'company.local'
        }
        
        with open(f"{self.output_dir}/group_vars/core_infrastructure.yml", 'w') as f:
            yaml.dump(core_vars, f, default_flow_style=False, indent=2)
        
        # Generate department-specific group variables
        for dept in self.departments:
            dept_name = dept['name']
            vlan_id = dept['vlan']
            subnet = dept['subnet']
            gateway = dept['gateway']
            
            dept_vars = {
                'department_name': dept_name,
                'vlan_id': vlan_id,
                'subnet': subnet,
                'gateway': gateway,
                'vlan_name': dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
            }
            
            with open(f"{self.output_dir}/group_vars/dept_{vlan_id}.yml", 'w') as f:
                yaml.dump(dept_vars, f, default_flow_style=False, indent=2)
        
        print("Generated group variables for all device types and departments")
        print(f"Created {len(self.departments) + 6} group variable files")

    def generate_network_role(self):
        """
        Generate complete network configuration role for switches and routers
        """
        
        network_tasks = """---
# Network Configuration Tasks for Switches and Routers Only

# Configure VLANs on switches using real department data
- name: Configure department VLANs on switches
  cisco.ios.ios_vlans:
    config: "{{ department_vlans }}"
    state: merged
  when: device_type == "switch"
  tags: [vlans, switches]

# Configure basic switch settings
- name: Configure switch base configuration
  cisco.ios.ios_config:
    lines:
      - "hostname {{ inventory_hostname }}"
      - "service password-encryption"
      - "ip domain-name {{ domain_name }}"
      - "enable secret admin"
      - "username admin privilege 15 secret admin"
      - "crypto key generate rsa modulus 1024"
      - "ip ssh version 2"
    parents: []
  when: device_type == "switch"
  tags: [base_config, switches]

# Configure switch management interface with real subnet mask
- name: Configure switch management interface
  cisco.ios.ios_config:
    lines:
      - "ip address {{ ansible_host }} {{ subnet | ipaddr('netmask') }}"
      - "no shutdown"
      - "description Management Interface for {{ department }}"
    parents: interface vlan1
  when: device_type == "switch"
  tags: [mgmt_interface, switches]

# Configure default gateway for switches
- name: Configure switch default gateway
  cisco.ios.ios_config:
    lines:
      - "ip default-gateway {{ gateway }}"
    parents: []
  when: device_type == "switch"
  tags: [gateway, switches]

# Configure router base settings
- name: Configure router base configuration
  cisco.ios.ios_config:
    lines:
      - "hostname {{ inventory_hostname }}"
      - "service password-encryption"
      - "ip domain-name {{ domain_name }}"
      - "enable secret admin"
      - "username admin privilege 15 secret admin"
      - "ip routing"
      - "ip cef"
      - "crypto key generate rsa modulus 1024"
      - "ip ssh version 2"
    parents: []
  when: device_type == "router"
  tags: [base_config, routers]

# Configure router department interface
- name: Configure router department LAN interface
  cisco.ios.ios_config:
    lines:
      - "ip address {{ ansible_host }} {{ subnet | ipaddr('netmask') }}"
      - "no shutdown"
      - "description {{ department }} Department LAN Gateway"
    parents: interface GigabitEthernet0/0
  when: device_type == "router"
  tags: [interfaces, routers]

# Configure SSH access for all network devices
- name: Configure VTY lines for SSH access
  cisco.ios.ios_config:
    lines:
      - "login local"
      - "transport input ssh"
      - "exec-timeout 30 0"
    parents: line vty 0 15
  when: device_type in ["switch", "router"]
  tags: [ssh_access, network_devices]

# Save configuration on all network devices
- name: Save running configuration
  cisco.ios.ios_config:
    save_when: always
  when: device_type in ["switch", "router"]
  tags: [save, network_devices]
"""
        
        # Write the tasks file
        with open(f"{self.output_dir}/roles/network-config/tasks/main.yml", 'w') as f:
            f.write(network_tasks)
        
        # Generate role variables using real department data
        network_vars = {
            'domain_name': 'company.local',
            'department_vlans': []
        }
        
        # Generate VLAN configurations using real department data
        for dept in self.departments:
            vlan_id = dept['vlan']
            dept_name = dept['name']
            clean_vlan_name = dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
            
            network_vars['department_vlans'].append({
                'vlan_id': vlan_id,
                'name': clean_vlan_name,
                'state': 'active'
            })
        
        # Write the variables file
        with open(f"{self.output_dir}/roles/network-config/vars/main.yml", 'w') as f:
            yaml.dump(network_vars, f, default_flow_style=False, indent=2)
        
        print("Generated complete network configuration role for switches and routers")
        print(f"Created VLAN configurations for {len(self.departments)} departments")

    def generate_end_devices_role(self):
        """
        Generate end devices configuration role for PCs, servers, and printers
        """
        
        end_devices_tasks = """---
# End Devices Configuration Tasks

# Configure network interface using netplan
- name: Configure network interface using netplan
  copy:
    content: |
      network:
        version: 2
        renderer: networkd
        ethernets:
          {{ ansible_default_ipv4.interface | default('eth0') }}:
            addresses:
              - {{ ansible_host }}/{{ subnet.split('/')[1] }}
            gateway4: {{ gateway }}
            nameservers:
              addresses:
                - 8.8.8.8
                - 8.8.4.4
              search:
                - company.local
    dest: /etc/netplan/01-network-config.yaml
    backup: yes
  when: 
    - ansible_os_family == "Debian"
    - ansible_distribution_major_version|int >= 18
  notify: apply netplan
  tags: [network, ubuntu]

# Install basic packages for PCs and servers
- name: Install basic packages for PCs and servers
  package:
    name: "{{ basic_packages }}"
    state: present
  when: device_type in ["pc", "server"]
  tags: [packages]

# Install server additional packages
- name: Install server additional packages
  package:
    name: "{{ server_packages }}"
    state: present
  when: device_type == "server"
  tags: [packages, servers]

# Configure DNS resolver
- name: Configure DNS resolver for all end devices
  copy:
    content: |
      nameserver 8.8.8.8
      nameserver 8.8.4.4
      search company.local
    dest: /etc/resolv.conf
    backup: yes
  tags: [dns]

# Set hostname
- name: Set hostname for all end devices
  hostname:
    name: "{{ inventory_hostname }}"
  tags: [hostname]

# Configure printer services
- name: Configure printer services for printers only
  service:
    name: cups
    state: started
    enabled: yes
  when: device_type == "printer"
  ignore_errors: yes
  tags: [printers]
"""
        
        # Write tasks file
        with open(f"{self.output_dir}/roles/network-config/tasks/end_devices.yml", 'w') as f:
            f.write(end_devices_tasks)
        
        # Create handlers
        end_devices_handlers = """---
# End Devices Configuration Handlers

- name: apply netplan
  command: netplan apply
  become: yes

- name: restart network
  service:
    name: network
    state: restarted
  become: yes
"""
        
        # Write handlers file
        with open(f"{self.output_dir}/roles/network-config/handlers/main.yml", 'w') as f:
            f.write(end_devices_handlers)
        
        # Define variables for end device configuration
        end_devices_vars = {
            'basic_packages': [
                'curl', 'wget', 'net-tools', 'openssh-server', 'htop', 'vim', 'git'
            ],
            'server_packages': [
                'nginx', 'mysql-server', 'fail2ban', 'ufw', 'rsync'
            ],
            'update_packages': False,
            'domain_name': 'company.local'
        }
        
        # Read existing variables and merge
        vars_file = f"{self.output_dir}/roles/network-config/vars/main.yml"
        try:
            with open(vars_file, 'r') as f:
                existing_vars = yaml.safe_load(f) or {}
        except FileNotFoundError:
            existing_vars = {}
        
        existing_vars.update(end_devices_vars)
        
        # Write updated variables file
        with open(vars_file, 'w') as f:
            yaml.dump(existing_vars, f, default_flow_style=False, indent=2)
        
        print("Generated end devices configuration for PCs, servers, and printers")

    def generate_playbooks(self):
        """
        Generate main playbooks for network deployment
        """
        
        # Main site deployment playbook
        site_playbook = """---
# Main Site Deployment Playbook

# Configure Network Infrastructure Devices
- name: Configure Network Infrastructure Devices
  hosts: switches:routers:core_infrastructure
  gather_facts: no
  connection: network_cli
  vars:
    ansible_network_os: ios
    ansible_user: admin
    ansible_password: admin
  roles:
    - network-config
  tags: [network, infrastructure, switches, routers]

# Configure End User Devices  
- name: Configure End User Devices
  hosts: pcs:servers:printers
  gather_facts: yes
  become: yes
  connection: ssh
  vars:
    ansible_user: admin
  roles:
    - network-config
  tags: [endpoints, end_devices, pcs, servers, printers]
"""
        
        with open(f"{self.output_dir}/site.yml", 'w') as f:
            f.write(site_playbook)
        
        # Network devices only playbook
        network_playbook = f"""---
# Network Infrastructure Only Playbook

- name: Configure Network Infrastructure Only
  hosts: switches:routers:core_infrastructure
  gather_facts: no
  connection: network_cli
  vars:
    ansible_network_os: ios
    ansible_user: admin
    ansible_password: admin
  
  tasks:
    # Configure department VLANs on switches
    - name: Configure department VLANs on switches using real data
      cisco.ios.ios_vlans:
        config:"""
        
        # Add VLAN configurations
        for dept in self.departments:
            vlan_id = dept['vlan']
            dept_name = dept['name']
            clean_name = dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
            network_playbook += f"""
          - vlan_id: {vlan_id}
            name: "{clean_name}"
            state: active"""
        
        network_playbook += """
        state: merged
      when: device_type == "switch"
      tags: [vlans, switches]

    # Save configuration
    - name: Save running configuration
      cisco.ios.ios_config:
        save_when: always
      when: device_type in ["switch", "router"]
      tags: [save, network_devices]
"""
        
        with open(f"{self.output_dir}/playbooks/deploy_network.yml", 'w') as f:
            f.write(network_playbook)
        
        print("Generated complete set of playbooks")
        print(f"Configured {len(self.departments)} department VLANs using real data")

    def generate_network_documentation(self):
        """
        Generate comprehensive network documentation
        """
        
        total_dept_devices = sum(len(dept['devices']) for dept in self.departments)
        total_devices = total_dept_devices + len(self.core_infrastructure)
        
        readme_content = f"""# University Network Automation Project

## Project Overview
This project demonstrates automated network deployment using Python and Ansible.

## Network Statistics
- **Total Departments:** {len(self.departments)}
- **Total Network Devices:** {total_devices}
- **Department Devices:** {total_dept_devices}
- **Core Infrastructure:** {len(self.core_infrastructure)} devices
- **VLANs Configured:** {len(self.departments)}

## Network Architecture

### Departments and VLANs
"""
        
        # Add department information
        for dept in self.departments:
            dept_name = dept['name']
            vlan_id = dept['vlan']
            subnet = dept['subnet']
            gateway = dept['gateway']
            devices = dept['devices']
            
            readme_content += f"""
#### {dept_name} (VLAN {vlan_id})
- **Subnet:** {subnet}
- **Gateway:** {gateway}
- **Total Devices:** {len(devices)}

**Device Details:**
"""
            
            for device in devices:
                device_name = device['name']
                device_type = device['type']
                device_ip = device['ip']
                readme_content += f"  - `{device_name}` ({device_type}): {device_ip}\n"
        
        # Add core infrastructure
        readme_content += f"""
### Core Infrastructure
"""
        for device in self.core_infrastructure:
            device_name = device['name']
            device_type = device['type']
            device_ip = device['ip']
            readme_content += f"- `{device_name}` ({device_type}): {device_ip}\n"
        
        readme_content += """
## Usage Instructions

### Complete Network Deployment
```bash
ansible-playbook site.yml
```

### Network Infrastructure Only
```bash
ansible-playbook playbooks/deploy_network.yml
```

## Generated Files
- `ansible.cfg` - Ansible configuration
- `inventories/hosts.yml` - Device inventory
- `group_vars/` - Device group variables
- `roles/network-config/` - Network configuration role
- `site.yml` - Complete deployment playbook
- `playbooks/deploy_network.yml` - Network infrastructure only
"""
        
        # Write README file
        with open(f"{self.output_dir}/README.md", 'w') as f:
            f.write(readme_content)
        
        print("Generated comprehensive project documentation")

    def run_generation(self):
        """
        Main execution method - FIXED VERSION
        """
        
        print("Network Automation Generator for University Project")
        print("Manual to Automated Network Deployment Transformation")
        print("=" * 60)
        print(f"Source Configuration: {self.network_data_file}")
        print(f"Output Directory: {self.output_dir}")
        print("=" * 60)
        
        # PHASE 1: Load network configuration
        print("\nPHASE 1: Loading Network Configuration Data")
        print("-" * 45)
        
        if not self.load_network_data():
            print("ERROR: Failed to load network configuration data")
            return False
        
        print("Successfully loaded network configuration")
        print(f"Found {len(self.departments)} departments")
        print(f"Found {len(self.core_infrastructure)} core infrastructure devices")
        
        total_devices = sum(len(dept['devices']) for dept in self.departments) + len(self.core_infrastructure)
        print(f"Total devices to configure: {total_devices}")
        
        # PHASE 2: Create directory structure
        print("\nPHASE 2: Creating Ansible Project Structure")
        print("-" * 45)
        
        try:
            self.create_directory_structure()
            print("Created simplified Ansible directory structure")
        except Exception as e:
            print(f"ERROR: Failed to create directory structure: {e}")
            return False
        
        # PHASE 3: Generate core configuration
        print("\nPHASE 3: Generating Core Ansible Configuration")
        print("-" * 45)
        
        try:
            self.generate_ansible_cfg()
            print("Generated ansible.cfg with network automation settings")
            
            self.generate_inventory()
            print("Generated inventory with exact IP addresses from network_data.yml")
            
            self.generate_group_department()
            print("Generated group variables for all device types")
            
        except Exception as e:
            print(f"ERROR: Failed to generate core configuration: {e}")
            return False
        
        # PHASE 4: Generate network role
        print("\nPHASE 4: Generating Unified Network Configuration Role")
        print("-" * 45)
        
        try:
            self.generate_network_role()
            print("Generated unified network-config role")
            print(f"Configured {len(self.departments)} department VLANs")
            
            self.generate_end_devices_role()
            print("Generated end devices configuration")
            
        except Exception as e:
            print(f"ERROR: Failed to generate network role: {e}")
            return False
        
        # PHASE 5: Generate playbooks
        print("\nPHASE 5: Generating Deployment Playbooks")
        print("-" * 45)
        
        try:
            self.generate_playbooks()
            print("Generated complete set of deployment playbooks")
            
        except Exception as e:
            print(f"ERROR: Failed to generate playbooks: {e}")
            return False
        
        # PHASE 6: Generate documentation
        print("\nPHASE 6: Generating Project Documentation")
        print("-" * 45)
        
        try:
            self.generate_network_documentation()
            print("Generated comprehensive project documentation")
            
        except Exception as e:
            print(f"ERROR: Failed to generate documentation: {e}")
            return False
        
        # Success summary
        print("\n" + "=" * 60)
        print("NETWORK AUTOMATION GENERATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        print(f"\nNetwork Topology Summary:")
        print(f"Total Departments: {len(self.departments)}")
        print(f"Total Devices: {total_devices}")
        print(f"Core Infrastructure: {len(self.core_infrastructure)} devices")
        
        print(f"\nGenerated Files:")
        print(f"Output Directory: {self.output_dir}/")
        print("  - ansible.cfg (Ansible configuration)")
        print("  - inventories/hosts.yml (Device inventory)")
        print("  - group_vars/ (Device group variables)")
        print("  - roles/network-config/ (Network configuration role)")
        print("  - site.yml (Complete deployment)")
        print("  - README.md (Project documentation)")
        
        print(f"\nDeployment Instructions:")
        print(f"1. Navigate to output directory: cd {self.output_dir}")
        print(f"2. Deploy complete network: ansible-playbook site.yml")
        print(f"3. Deploy network infrastructure only: ansible-playbook playbooks/deploy_network.yml")
        
        return True

    def test_gns3_connection(self):
        """
        Simple GNS3 connection test without importing diagnostic module
        """
        print("Testing GNS3 server connection...")
        
        try:
            import requests
            
            # Test basic connection
            response = requests.get(f"{self.gns3_server_url}/v3/version", timeout=5)
            
            if response.status_code == 200:
                version_info = response.json()
                print(f" GNS3 server connection: OK")
                print(f"  Version: {version_info.get('version', 'Unknown')}")
                return True
            else:
                print(f" GNS3 server responded with status: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(" Cannot connect to GNS3 server")
            print("  Make sure GNS3 is running on http://127.0.0.1:3080")
            return False
        except Exception as e:
            print(f" Connection test failed: {e}")
            return False

    # Initialize GNS3 settings
    gns3_server_url = "http://127.0.0.1:3080"


def main():
    """
    FIXED Main function with proper menu handling
    """
    print("Starting Network Automation Generator - CORRECTED VERSION...")
    print("=" * 60)
    
    # Initialize generator
    generator = NetworkAutomationGenerator()
    generator.load_network_data()
    
    # Check if network data loaded successfully
    if not generator.departments:
        print("ERROR: No departments loaded from network_data.yml")
        print("Please check your network configuration file")
        exit(1)
    
    print(f" Loaded {len(generator.departments)} departments")
    print(f" Loaded {len(generator.core_infrastructure)} core infrastructure devices")
    
    # FIXED MAIN MENU - All choices now handled properly
    print("\nWhat would you like to generate?")
    print("1. Ansible Configuration")
    print("2. GNS3 Connection Test")
    print("3. Both Ansible + GNS3 Test")
    print("4. Exit")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        exit(0)
    
    success = False
    
    if choice == "1":
        # ANSIBLE GENERATION ONLY
        print("\nGenerating Ansible configuration...")
        success = generator.run_generation()
        
        if success:
            print("\n Ansible automation files generated successfully!")
            print(" All YAML files use correct dictionary format")
            print(" All IP addresses taken directly from network_data.yml")
            print(" No external template files needed")
        else:
            print("\n Ansible generation failed!")
    
    elif choice == "2":
        # GNS3 CONNECTION TEST
        print("\nTesting GNS3 connection...")
        success = generator.test_gns3_connection()
        
        if success:
            print("\n GNS3 connection test successful!")
        else:
            print("\n GNS3 connection test failed!")
    
    elif choice == "3":
        # BOTH ANSIBLE AND GNS3 TEST
        print("\nGenerating Ansible configuration and testing GNS3...")
        
        # First generate Ansible config
        print("\nStep 1: Generating Ansible configuration...")
        ansible_success = generator.run_generation()
        
        # Then test GNS3 connection
        print("\nStep 2: Testing GNS3 connection...")
        gns3_success = generator.test_gns3_connection()
        
        success = ansible_success and gns3_success
        
        if success:
            print("\n Complete automation setup successful!")
            print(" Ansible playbooks ready for deployment")
            print(" GNS3 server connection verified")
        else:
            print(f"\n Partial success:")
            print(f"  Ansible: {' Success' if ansible_success else ' Failed'}")
            print(f"  GNS3: {' Success' if gns3_success else ' Failed'}")
    
    elif choice == "4":
        print("Exiting...")
        exit(0)
    
    else:
        print("Invalid choice. Please run again and select 1-4.")
        exit(1)
    
    # Final result
    if success:
        print("\n" + "=" * 60)
        print("GENERATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("GENERATION COMPLETED WITH ISSUES!")
        print("=" * 60)


if __name__ == "__main__":
    main()