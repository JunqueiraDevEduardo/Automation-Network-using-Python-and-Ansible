#!/usr/bin/env python3
"""
Network Automation Generator
Reads network_data.yml and generates complete Ansible automation structure
Creates proper inventory, playbooks, roles, and configuration files
No external template files - all configurations embedded in code
"""

import yaml
import json
import os
from pathlib import Path
from typing import Dict, List, Any

class NetworkAutomationGenerator:
    """
    Main generator class that converts network_data.yml into complete Ansible automation
    Creates proper directory structure, inventory, playbooks, and configuration files
    All templates embedded in code - no external template files needed
    """
    
    def __init__(self, network_data_file: str = "network_data.yml"):
        """
        Initialize generator with network data file path
        Sets up base paths and loads network configuration
        """
        self.network_data_file = network_data_file
        self.output_dir = "ansible_config"
        self.network_data = None
        self.departments = []
        self.core_infrastructure = []
        
        # Device type mappings for Ansible inventory organization
        self.device_type_mapping = {
            'switch': 'switches',
            'router': 'routers', 
            'pc': 'workstations',
            'server': 'servers',
            'printer': 'printers'
        }
        
    def load_network_data(self):
        """
        Load network configuration from YAML file
        Handles file reading and error management
        """
        try:
            if os.path.exists(self.network_data_file):
                with open(self.network_data_file, 'r') as f:
                    self.network_data = yaml.safe_load(f)
                print(f"Loaded network data from {self.network_data_file}")
            else:
                print(f"Error: Network data file {self.network_data_file} not found")
                return False
                
            # Extract departments and core infrastructure
            self.departments = self.network_data.get('departments', [])
            self.core_infrastructure = self.network_data.get('core_infrastructure', [])
            
            print(f"Found {len(self.departments)} departments")
            print(f"Found {len(self.core_infrastructure)} core infrastructure devices")
            return True
            
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            return False
        except Exception as e:
            print(f"Error loading network data: {e}")
            return False
    
    def create_directory_structure(self):
        """
        Create complete Ansible directory structure
        Establishes all necessary folders for proper Ansible organization
        """
        directories = [
            self.output_dir,
            f"{self.output_dir}/inventories",
            f"{self.output_dir}/playbooks", 
            f"{self.output_dir}/roles",
            f"{self.output_dir}/group_vars",
            f"{self.output_dir}/host_vars",
            f"{self.output_dir}/roles/switch-config/tasks",
            f"{self.output_dir}/roles/switch-config/vars",
            f"{self.output_dir}/roles/router-config/tasks",
            f"{self.output_dir}/roles/router-config/vars",
            f"{self.output_dir}/roles/pc-config/tasks",
            f"{self.output_dir}/roles/pc-config/vars",
            f"{self.output_dir}/roles/pc-config/handlers",
            f"{self.output_dir}/scripts"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
        print(f"Created directory structure in {self.output_dir}")
    
    def generate_ansible_cfg(self):
        """
        Generate main ansible.cfg configuration file
        Sets up Ansible behavior and connection parameters
        """
        config_content = """[defaults]
inventory = inventories/hosts.yml
remote_user = admin
host_key_checking = False
timeout = 30
retry_files_enabled = False
gathering = explicit
stdout_callback = yaml
forks = 10

[persistent_connection]
connect_timeout = 30
command_timeout = 30

[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
pipelining = True

[privilege_escalation]
become = True
become_method = enable
become_user = admin
become_ask_pass = False
"""
        
        with open(f"{self.output_dir}/ansible.cfg", 'w') as f:
            f.write(config_content)
        print("Generated ansible.cfg")
    
    def generate_inventory(self):
        """
        Generate Ansible inventory from network_data.yml
        Uses exact IP addresses from network_data.yml for each device
        Creates organized inventory with proper device grouping
        """
        inventory = {
            'all': {
                'children': {
                    'switches': {'hosts': {}},
                    'routers': {'hosts': {}},
                    'workstations': {'hosts': {}},
                    'servers': {'hosts': {}},
                    'printers': {'hosts': {}},
                    'core_infrastructure': {'hosts': {}}
                }
            }
        }
        
        # Add core infrastructure devices with exact IPs
        for device in self.core_infrastructure:
            device_name = device.get('name', 'unknown')
            device_info = {
                'ansible_host': device.get('ip', '192.168.1.1'),
                'device_type': device.get('type', 'unknown'),
                'department': 'core'
            }
            inventory['all']['children']['core_infrastructure']['hosts'][device_name] = device_info
        
        # Process each department with exact device IPs
        for dept in self.departments:
            dept_name = dept.get('name', 'Unknown')
            vlan_id = dept.get('vlan', 1)
            subnet = dept.get('subnet', '192.168.1.0/24')
            gateway = dept.get('gateway', '192.168.1.1')
            devices = dept.get('devices', [])
            
            # Create department group
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
            
            # Process devices in department with their exact IP addresses
            for device in devices:
                device_name = device.get('name', 'unknown')
                device_type = device.get('type', 'unknown')
                device_ip = device.get('ip', '192.168.1.2')  # Use exact IP from network_data.yml
                
                # Create device info with exact IP address
                device_info = {
                    'ansible_host': device_ip,
                    'device_type': device_type,
                    'department': dept_name,
                    'vlan_id': vlan_id,
                    'subnet': subnet,
                    'gateway': gateway
                }
                
                # Add network-specific variables for network devices
                if device_type in ['switch', 'router']:
                    device_info.update({
                        'ansible_network_os': 'ios',
                        'ansible_connection': 'network_cli',
                        'ansible_user': 'admin',
                        'ansible_password': 'admin',
                        'ansible_become': 'yes',
                        'ansible_become_method': 'enable'
                    })
                elif device_type in ['pc', 'server']:
                    device_info.update({
                        'ansible_connection': 'ssh',
                        'ansible_user': 'admin',
                        'ansible_become': 'yes',
                        'ansible_become_method': 'sudo'
                    })
                
                # Add to appropriate device type group based on actual type and name
                if device_type == 'switch':
                    inventory['all']['children']['switches']['hosts'][device_name] = device_info
                elif device_type == 'router':
                    inventory['all']['children']['routers']['hosts'][device_name] = device_info
                elif device_type == 'pc':
                    # Check if it's actually a server or printer based on name
                    if 'server' in device_name.lower():
                        inventory['all']['children']['servers']['hosts'][device_name] = device_info
                    elif 'printer' in device_name.lower():
                        inventory['all']['children']['printers']['hosts'][device_name] = device_info
                    else:
                        inventory['all']['children']['workstations']['hosts'][device_name] = device_info
                
                # Add to department group
                inventory['all']['children'][dept_group_name]['hosts'][device_name] = device_info
        
        # Add network devices group
        inventory['all']['children']['network_devices'] = {
            'children': ['switches', 'routers', 'core_infrastructure'],
            'vars': {
                'ansible_network_os': 'ios',
                'ansible_connection': 'network_cli',
                'ansible_user': 'admin',
                'ansible_password': 'admin',
                'ansible_become': 'yes',
                'ansible_become_method': 'enable'
            }
        }
        
        # Add end devices group
        inventory['all']['children']['end_devices'] = {
            'children': ['workstations', 'servers', 'printers'],
            'vars': {
                'ansible_connection': 'ssh',
                'ansible_user': 'admin',
                'ansible_become': 'yes',
                'ansible_become_method': 'sudo'
            }
        }
        
        with open(f"{self.output_dir}/inventories/hosts.yml", 'w') as f:
            yaml.dump(inventory, f, default_flow_style=False, indent=2)
        print("Generated inventory file with exact IP addresses")
    
    def generate_group_vars(self):
        """
        Generate group variables for different device types and departments
        Creates variables for network devices, end devices, and each department
        """
        # Network devices group vars
        network_vars = {
            'ansible_network_os': 'ios',
            'ansible_connection': 'network_cli',
            'ansible_user': 'admin',
            'ansible_password': 'admin',
            'ansible_become': 'yes',
            'ansible_become_method': 'enable',
            'ntp_servers': ['192.168.1.1', '192.168.1.2'],
            'dns_servers': ['8.8.8.8', '8.8.4.4'],
            'domain_name': 'company.local'
        }
        
        with open(f"{self.output_dir}/group_vars/network_devices.yml", 'w') as f:
            yaml.dump(network_vars, f, default_flow_style=False, indent=2)
        
        # End devices group vars
        end_device_vars = {
            'ansible_connection': 'ssh',
            'ansible_user': 'admin',
            'ansible_become': 'yes',
            'ansible_become_method': 'sudo',
            'dns_servers': ['8.8.8.8', '8.8.4.4'],
            'domain_name': 'company.local'
        }
        
        with open(f"{self.output_dir}/group_vars/end_devices.yml", 'w') as f:
            yaml.dump(end_device_vars, f, default_flow_style=False, indent=2)
        
        # Generate department-specific group vars
        for dept in self.departments:
            dept_name = dept.get('name', 'Unknown')
            vlan_id = dept.get('vlan', 1)
            subnet = dept.get('subnet', '192.168.1.0/24')
            gateway = dept.get('gateway', '192.168.1.1')
            
            dept_vars = {
                'department_name': dept_name,
                'vlan_id': vlan_id,
                'subnet': subnet,
                'gateway': gateway,
                'vlan_name': dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
            }
            
            with open(f"{self.output_dir}/group_vars/dept_{vlan_id}.yml", 'w') as f:
                yaml.dump(dept_vars, f, default_flow_style=False, indent=2)
        
        print("Generated group variables")
    
    def generate_switch_role(self):
        """
        Generate switch configuration role with tasks and variables
        All configuration embedded directly in tasks - no template files
        """
        # Switch tasks with embedded configuration
        switch_tasks = f"""---
# Switch Configuration Tasks
- name: Configure VLANs
  cisco.ios.ios_vlans:
    config: "{{{{ vlans_config }}}}"
    state: merged
  tags: [vlans]

- name: Configure L2 interfaces
  cisco.ios.ios_l2_interfaces:
    config: "{{{{ switch_interfaces }}}}"
    state: merged
  tags: [interfaces]

- name: Configure switch base settings
  cisco.ios.ios_config:
    lines:
      - "hostname {{{{ inventory_hostname }}}}"
      - "service password-encryption"
      - "ip domain-name {{{{ domain_name | default('company.local') }}}}"
      - "enable secret admin"
      - "username admin privilege 15 secret admin"
      - "ip default-gateway {{{{ gateway | default('192.168.1.254') }}}}"
      - "crypto key generate rsa modulus 1024"
      - "ip ssh version 2"
    parents: []
  tags: [base_config]

- name: Configure management interface
  cisco.ios.ios_config:
    lines:
      - "ip address {{{{ ansible_host }}}} 255.255.255.0"
      - "no shutdown"
    parents: interface vlan1
  tags: [mgmt_interface]

- name: Configure VTY lines for SSH access
  cisco.ios.ios_config:
    lines:
      - "login local"
      - "transport input ssh"
    parents: line vty 0 15
  tags: [ssh_access]

- name: Save configuration
  cisco.ios.ios_config:
    save_when: always
  tags: [save]
"""
        
        with open(f"{self.output_dir}/roles/switch-config/tasks/main.yml", 'w') as f:
            f.write(switch_tasks)
        
        # Switch variables with VLAN configurations from network_data.yml
        switch_vars = {
            'vlans_config': [],
            'switch_interfaces': []
        }
        
        # Generate VLAN configurations from departments
        for dept in self.departments:
            vlan_id = dept.get('vlan', 1)
            dept_name = dept.get('name', 'Unknown')
            clean_name = dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
            
            switch_vars['vlans_config'].append({
                'vlan_id': vlan_id,
                'name': clean_name,
                'state': 'active'
            })
        
        # Generate interface configurations
        for i in range(1, 25):
            switch_vars['switch_interfaces'].append({
                'name': f'FastEthernet0/{i}',
                'access': {'vlan': 1}
            })
        
        with open(f"{self.output_dir}/roles/switch-config/vars/main.yml", 'w') as f:
            yaml.dump(switch_vars, f, default_flow_style=False, indent=2)
        
        print("Generated switch configuration role (no template files)")
    
    def generate_router_role(self):
        """
        Generate router configuration role with tasks and variables
        All configuration embedded directly in tasks - no template files
        """
        # Router tasks with embedded configuration
        router_tasks = f"""---
# Router Configuration Tasks
- name: Configure router base settings
  cisco.ios.ios_config:
    lines:
      - "hostname {{{{ inventory_hostname }}}}"
      - "ip routing"
      - "ip cef"
      - "service password-encryption"
      - "ip domain-name {{{{ domain_name | default('company.local') }}}}"
      - "enable secret admin"
      - "username admin privilege 15 secret admin"
      - "crypto key generate rsa modulus 1024"
      - "ip ssh version 2"
    parents: []
  tags: [base_config]

- name: Configure router interface
  cisco.ios.ios_config:
    lines:
      - "ip address {{{{ ansible_host }}}} 255.255.255.0"
      - "no shutdown"
    parents: interface FastEthernet0/0
  tags: [interface]

- name: Configure VTY lines for SSH access
  cisco.ios.ios_config:
    lines:
      - "login local"
      - "transport input ssh"
    parents: line vty 0 15
  tags: [ssh_access]

- name: Save configuration
  cisco.ios.ios_config:
    save_when: always
  tags: [save]
"""
        
        with open(f"{self.output_dir}/roles/router-config/tasks/main.yml", 'w') as f:
            f.write(router_tasks)
        
        # Router variables
        router_vars = {
            'domain_name': 'company.local'
        }
        
        with open(f"{self.output_dir}/roles/router-config/vars/main.yml", 'w') as f:
            yaml.dump(router_vars, f, default_flow_style=False, indent=2)
        
        print("Generated router configuration role (no template files)")
    
    def generate_pc_role(self):
        """
        Generate PC configuration role for workstations and servers
        All configuration embedded directly in tasks - no template files
        """
        # PC tasks with embedded network configuration
        pc_tasks = f"""---
# PC Configuration Tasks
- name: Configure network interface using netplan (Ubuntu 18.04+)
  copy:
    content: |
      network:
        version: 2
        renderer: networkd
        ethernets:
          {{{{ ansible_default_ipv4.interface | default('eth0') }}}}:
            addresses:
              - {{{{ ansible_host }}}}/{{{{ subnet.split('/')[1] }}}}
            gateway4: {{{{ gateway }}}}
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
  tags: [network]

- name: Configure network interface (CentOS/RHEL)
  copy:
    content: |
      TYPE=Ethernet
      BOOTPROTO=static
      IPADDR={{{{ ansible_host }}}}
      NETMASK=255.255.255.0
      GATEWAY={{{{ gateway }}}}
      DNS1=8.8.8.8
      DNS2=8.8.4.4
      ONBOOT=yes
    dest: "/etc/sysconfig/network-scripts/ifcfg-{{{{ ansible_default_ipv4.interface | default('eth0') }}}}"
    backup: yes
  when: ansible_os_family == "RedHat"
  notify: restart network
  tags: [network]

- name: Install basic packages
  package:
    name: "{{{{ basic_packages }}}}"
    state: present
  tags: [packages]

- name: Configure DNS resolver
  copy:
    content: |
      nameserver 8.8.8.8
      nameserver 8.8.4.4
      search company.local
    dest: /etc/resolv.conf
    backup: yes
  tags: [dns]
"""
        
        with open(f"{self.output_dir}/roles/pc-config/tasks/main.yml", 'w') as f:
            f.write(pc_tasks)
        
        # Create handlers for PC role
        pc_handlers = """---
# PC Configuration Handlers
- name: apply netplan
  command: netplan apply

- name: restart network
  service:
    name: network
    state: restarted
"""
        
        with open(f"{self.output_dir}/roles/pc-config/handlers/main.yml", 'w') as f:
            f.write(pc_handlers)
        
        # PC variables
        pc_vars = {
            'basic_packages': [
                'curl',
                'wget', 
                'net-tools',
                'openssh-server',
                'htop',
                'vim',
                'git'
            ]
        }
        
        with open(f"{self.output_dir}/roles/pc-config/vars/main.yml", 'w') as f:
            yaml.dump(pc_vars, f, default_flow_style=False, indent=2)
        
        print("Generated PC configuration role (no template files)")
    
    def generate_playbooks(self):
        """
        Generate main playbooks for network deployment
        Creates site-wide, network-only, and device-specific playbooks
        """
        # Main site playbook
        site_playbook = """---
# Main Site Deployment Playbook
- name: Configure Network Infrastructure
  hosts: network_devices
  gather_facts: no
  roles:
    - switch-config
    - router-config
  tags: [network]

- name: Configure End Devices
  hosts: end_devices
  gather_facts: yes
  become: yes
  roles:
    - pc-config
  tags: [endpoints]
"""
        
        with open(f"{self.output_dir}/site.yml", 'w') as f:
            f.write(site_playbook)
        
        # Network devices only playbook with exact VLAN configurations
        network_playbook = """---
# Network Devices Configuration Playbook
- name: Configure All Network Devices
  hosts: network_devices
  gather_facts: no
  vars:
    ansible_network_os: ios
    ansible_connection: network_cli
    
  tasks:
    - name: Configure VLANs on switches
      cisco.ios.ios_vlans:
        config:"""
        
        # Add VLAN configurations from network_data.yml
        for dept in self.departments:
            vlan_id = dept.get('vlan', 1)
            dept_name = dept.get('name', 'Unknown')
            clean_name = dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
            network_playbook += f"""
          - vlan_id: {vlan_id}
            name: "{clean_name}"
            state: active"""
        
        network_playbook += """
        state: merged
      when: '"switch" in inventory_hostname.lower()'
      tags: [vlans]

    - name: Configure switch management interface
      cisco.ios.ios_config:
        lines:
          - "ip address {{ ansible_host }} 255.255.255.0"
          - "no shutdown"
        parents: interface vlan1
      when: '"switch" in inventory_hostname.lower()'
      tags: [mgmt_interface]

    - name: Configure router interface
      cisco.ios.ios_config:
        lines:
          - "ip address {{ ansible_host }} 255.255.255.0"
          - "no shutdown"
        parents: interface FastEthernet0/0
      when: '"router" in inventory_hostname.lower() or inventory_hostname.startswith("R-")'
      tags: [router_interface]

    - name: Save configuration
      cisco.ios.ios_config:
        save_when: always
      tags: [save]
"""
        
        with open(f"{self.output_dir}/playbooks/deploy_network.yml", 'w') as f:
            f.write(network_playbook)
        
        # VLAN configuration playbook with exact department VLANs
        vlan_playbook = """---
# VLAN Configuration Playbook
- name: Configure VLANs on Switches
  hosts: switches
  gather_facts: no
  
  tasks:
    - name: Configure department VLANs
      cisco.ios.ios_vlans:
        config:"""
        
        for dept in self.departments:
            vlan_id = dept.get('vlan', 1)
            dept_name = dept.get('name', 'Unknown')
            clean_name = dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
            vlan_playbook += f"""
          - vlan_id: {vlan_id}
            name: "{clean_name}"
            state: active"""
        
        vlan_playbook += """
        state: merged
      tags: [vlans]
      
    - name: Save configuration
      cisco.ios.ios_config:
        save_when: always
"""
        
        with open(f"{self.output_dir}/playbooks/configure_vlans.yml", 'w') as f:
            f.write(vlan_playbook)
        
        print("Generated playbooks with exact VLAN configurations")
    
    def generate_deployment_script(self):
        """
        Generate bash deployment script for easy execution
        Creates script to run all playbooks in correct order
        """
        script_content = """#!/bin/bash
# Network Deployment Script
# Deploys complete network configuration from network_data.yml

set -e

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command -v ansible &> /dev/null; then
        error "Ansible is not installed"
        exit 1
    fi
    
    if ! ansible-galaxy collection list | grep -q cisco.ios; then
        warn "Installing Cisco IOS collection..."
        ansible-galaxy collection install cisco.ios
    fi
    
    log "Prerequisites OK"
}

# Test connectivity
test_connectivity() {
    log "Testing device connectivity..."
    
    ansible network_devices -i inventories/hosts.yml -m ping --one-line || {
        warn "Some network devices not reachable"
    }
    
    log "Connectivity test completed"
}

# Deploy network
deploy_network() {
    log "Deploying network configuration..."
    
    info "Configuring VLANs..."
    ansible-playbook -i inventories/hosts.yml playbooks/configure_vlans.yml
    
    info "Deploying complete network..."
    ansible-playbook -i inventories/hosts.yml playbooks/deploy_network.yml
    
    log "Network deployment completed"
}

# Main execution
main() {
    log "Starting network deployment automation..."
    
    case "${1:-deploy}" in
        "check")
            check_prerequisites
            test_connectivity
            ;;
        "deploy")
            check_prerequisites
            deploy_network
            ;;
        "full")
            check_prerequisites
            test_connectivity
            deploy_network
            ;;
        *)
            echo "Usage: $0 {check|deploy|full}"
            echo "  check  - Check prerequisites and connectivity"
            echo "  deploy - Deploy network configuration"
            echo "  full   - Full deployment with checks"
            exit 1
            ;;
    esac
    
    log "Deployment automation completed"
}

main "$@"
"""
        
        script_path = f"{self.output_dir}/deploy_network.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        print("Generated deployment script")
    
    def generate_network_documentation(self):
        """
        Generate network documentation and reference files
        Creates README and network topology data with exact IP addresses
        """
        # Generate README with device details
        readme_content = f"""# Network Automation Configuration

Generated from network_data.yml with exact IP addresses

## Network Overview

**Departments:** {len(self.departments)}
**Core Infrastructure:** {len(self.core_infrastructure)} devices

### Department Summary with IP Addresses:
"""
        
        for dept in self.departments:
            dept_name = dept.get('name', 'Unknown')
            vlan_id = dept.get('vlan', 1)
            subnet = dept.get('subnet', 'N/A')
            gateway = dept.get('gateway', 'N/A')
            devices = dept.get('devices', [])
            
            readme_content += f"""
- **{dept_name}** (VLAN {vlan_id})
  - Subnet: {subnet}
  - Gateway: {gateway}
  - Devices: {len(devices)}
"""
            
            # List devices with their exact IP addresses
            for device in devices:
                device_name = device.get('name', 'unknown')
                device_type = device.get('type', 'unknown')
                device_ip = device.get('ip', 'N/A')
                readme_content += f"    - {device_name} ({device_type}): {device_ip}\n"
        
        readme_content += """
## Usage

### Deploy Complete Network
```bash
./deploy_network.sh full
```

### Deploy Network Only
```bash
./deploy_network.sh deploy
```

### Check Prerequisites
```bash
./deploy_network.sh check
```

### Manual Deployment
```bash
# Configure VLANs
ansible-playbook -i inventories/hosts.yml playbooks/configure_vlans.yml

# Deploy network devices
ansible-playbook -i inventories/hosts.yml playbooks/deploy_network.yml

# Deploy complete site
ansible-playbook -i inventories/hosts.yml site.yml
```

## Files Generated

- `ansible.cfg` - Ansible configuration
- `inventories/hosts.yml` - Device inventory with exact IP addresses
- `playbooks/` - Deployment playbooks
- `roles/` - Configuration roles (no template files)
- `group_vars/` - Group variables
- `deploy_network.sh` - Deployment script

## IP Address Assignment

All IP addresses are taken directly from network_data.yml:
- No automatic IP generation
- Exact addresses as specified in configuration
- VLAN assignments match department structure

## Requirements

- Ansible 2.9+
- cisco.ios collection
- Network devices accessible via SSH/Telnet
"""
        
        with open(f"{self.output_dir}/README.md", 'w') as f:
            f.write(readme_content)
        
        # Generate network topology data with exact IPs
        topology_data = {
            'departments': self.departments,
            'core_infrastructure': self.core_infrastructure,
            'total_devices': sum(len(dept.get('devices', [])) for dept in self.departments) + len(self.core_infrastructure),
            'ip_assignments': {}
        }
        
        # Add IP assignment details
        for dept in self.departments:
            dept_name = dept.get('name', 'Unknown')
            topology_data['ip_assignments'][dept_name] = {
                'vlan': dept.get('vlan'),
                'subnet': dept.get('subnet'),
                'gateway': dept.get('gateway'),
                'devices': [
                    {
                        'name': device.get('name'),
                        'type': device.get('type'),
                        'ip': device.get('ip')
                    }
                    for device in dept.get('devices', [])
                ]
            }
        
        with open(f"{self.output_dir}/network_topology.json", 'w') as f:
            json.dump(topology_data, f, indent=2)
        
        print("Generated documentation with exact IP addresses")
    
    def run_generation(self):
        """
        Main execution method that orchestrates the complete generation process
        Loads data, creates structure, and generates all configuration files
        """
        print("Network Automation Generator")
        print("=" * 50)
        
        # Load network data
        if not self.load_network_data():
            print("Failed to load network data")
            return False
        
        # Create directory structure
        self.create_directory_structure()
        
        # Generate all configuration files
        self.generate_ansible_cfg()
        self.generate_inventory()
        self.generate_group_vars()
        self.generate_switch_role()
        self.generate_router_role()
        self.generate_pc_role()
        self.generate_playbooks()
        self.generate_deployment_script()
        self.generate_network_documentation()
        
        print("\nGeneration Summary:")
        print(f"- Processed {len(self.departments)} departments")
        print(f"- Generated inventory with exact IP addresses")
        print(f"- Created roles without template files")
        print(f"- Generated deployment playbooks")
        print(f"- Created deployment automation script")
        
        # Show IP address summary
        print("\nIP Address Summary by Department:")
        for dept in self.departments:
            dept_name = dept.get('name', 'Unknown')
            vlan_id = dept.get('vlan', 1)
            subnet = dept.get('subnet', 'N/A')
            device_count = len(dept.get('devices', []))
            print(f"  VLAN {vlan_id} ({dept_name}): {subnet} - {device_count} devices")
        
        print(f"\nFiles created in '{self.output_dir}' directory")
        print("To deploy: cd ansible_config && ./deploy_network.sh full")
        
        return True

def main():
    """
    Main function for standalone script execution
    Creates generator instance and runs complete generation process
    """
    print("Starting Network Automation Generator...")
    
    generator = NetworkAutomationGenerator()
    
    if generator.run_generation():
        print("\nNetwork automation files generated successfully!")
        print("All IP addresses taken directly from network_data.yml")
        print("No template files created - all configurations embedded in tasks")
    else:
        print("\nGeneration failed!")
        exit(1)

if __name__ == "__main__":
    main()