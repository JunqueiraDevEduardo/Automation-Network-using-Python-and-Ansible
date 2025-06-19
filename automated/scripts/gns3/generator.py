#!/usr/bin/env python3
"""
FIXED Network Automation Generator
Corrected version that properly handles network_data.yml and generates working Ansible configurations
"""

import yaml
import json
import os
from pathlib import Path
from typing import Dict, List, Any

class NetworkAutomationGenerator:
    def __init__(self, network_data_file: str = "config/network_data.yml"):
        """Initialize generator with network data file path"""
        self.network_data_file = network_data_file
        self.output_dir = "scripts/gns3/ansible_config"
        self.network_data = None
        self.departments = []
        self.core_infrastructure = []
        
    def load_network_data(self):
        """Load network configuration from YAML file"""
        try:
            # Try multiple possible locations for the config file
            possible_paths = [
                self.network_data_file,
                "config/network_data.yml",
                "scripts/gns3/network_data.yml",
                "network_data.yml"
            ]
            
            config_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            
            if not config_path:
                print(f"Error: Network data file not found in any of these locations:")
                for path in possible_paths:
                    print(f"  - {path}")
                return False
                
            with open(config_path, 'r') as f:
                self.network_data = yaml.safe_load(f)
            
            print(f"✓ Loaded network data from {config_path}")
            
            # Extract departments and core infrastructure
            self.departments = self.network_data.get('departments', [])
            self.core_infrastructure = self.network_data.get('core_infrastructure', [])
            
            print(f"✓ Found {len(self.departments)} departments")
            print(f"✓ Found {len(self.core_infrastructure)} core infrastructure devices")
            
            return True
            
        except yaml.YAMLError as e:
            print(f"Error parsing YAML: {e}")
            return False
        except Exception as e:
            print(f"Error loading network data: {e}")
            return False
    
    def create_directory_structure(self):
        """Create complete Ansible directory structure"""
        directories = [
            self.output_dir,
            f"{self.output_dir}/inventories",
            f"{self.output_dir}/playbooks", 
            f"{self.output_dir}/roles",
            f"{self.output_dir}/group_vars",
            f"{self.output_dir}/roles/switch-config/tasks",
            f"{self.output_dir}/roles/switch-config/vars",
            f"{self.output_dir}/roles/router-config/tasks",
            f"{self.output_dir}/roles/router-config/vars",
            f"{self.output_dir}/roles/pc-config/tasks",
            f"{self.output_dir}/roles/pc-config/vars",
            f"{self.output_dir}/roles/pc-config/handlers"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
        print(f"✓ Created directory structure in {self.output_dir}")
    
    def generate_ansible_cfg(self):
        """Generate main ansible.cfg configuration file"""
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
        print("✓ Generated ansible.cfg")
    
    def generate_inventory(self):
        """Generate Ansible inventory with correct YAML format"""
        # Initialize inventory structure
        inventory = {
            'all': {
                'children': {
                    'network_devices': {
                        'children': {
                            'switches': {'hosts': {}},
                            'routers': {'hosts': {}},
                            'core_infrastructure': {'hosts': {}}
                        },
                        'vars': {
                            'ansible_network_os': 'ios',
                            'ansible_connection': 'network_cli',
                            'ansible_user': 'admin',
                            'ansible_password': 'admin',
                            'ansible_become': 'yes',
                            'ansible_become_method': 'enable'
                        }
                    },
                    'end_devices': {
                        'children': {
                            'workstations': {'hosts': {}},
                            'servers': {'hosts': {}},
                            'printers': {'hosts': {}}
                        },
                        'vars': {
                            'ansible_connection': 'ssh',
                            'ansible_user': 'admin',
                            'ansible_become': 'yes',
                            'ansible_become_method': 'sudo'
                        }
                    }
                }
            }
        }
        
        # Add core infrastructure
        for device in self.core_infrastructure:
            device_name = device.get('name', 'unknown')
            device_info = {
                'ansible_host': device.get('ip', '192.168.1.1'),
                'device_type': device.get('type', 'unknown'),
                'department': 'core'
            }
            inventory['all']['children']['network_devices']['children']['core_infrastructure']['hosts'][device_name] = device_info
        
        # Process departments
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
            
            # Process devices
            for device in devices:
                device_name = device.get('name', 'unknown')
                device_type = device.get('type', 'unknown')
                device_ip = device.get('ip', '192.168.1.2')
                
                device_info = {
                    'ansible_host': device_ip,
                    'device_type': device_type,
                    'department': dept_name,
                    'vlan_id': vlan_id,
                    'subnet': subnet,
                    'gateway': gateway
                }
                
                # Add network-specific variables
                if device_type in ['switch', 'router']:
                    device_info.update({
                        'ansible_network_os': 'ios',
                        'ansible_connection': 'network_cli',
                        'ansible_user': 'admin',
                        'ansible_password': 'admin',
                        'ansible_become': 'yes',
                        'ansible_become_method': 'enable'
                    })
                else:
                    device_info.update({
                        'ansible_connection': 'ssh',
                        'ansible_user': 'admin',
                        'ansible_become': 'yes',
                        'ansible_become_method': 'sudo'
                    })
                
                # Categorize devices
                if device_type == 'switch':
                    inventory['all']['children']['network_devices']['children']['switches']['hosts'][device_name] = device_info
                elif device_type == 'router':
                    inventory['all']['children']['network_devices']['children']['routers']['hosts'][device_name] = device_info
                elif device_type == 'pc':
                    if 'server' in device_name.lower():
                        inventory['all']['children']['end_devices']['children']['servers']['hosts'][device_name] = device_info
                    elif 'printer' in device_name.lower():
                        inventory['all']['children']['end_devices']['children']['printers']['hosts'][device_name] = device_info
                    else:
                        inventory['all']['children']['end_devices']['children']['workstations']['hosts'][device_name] = device_info
                
                # Add to department group
                inventory['all']['children'][dept_group_name]['hosts'][device_name] = device_info
        
        # Save inventory
        with open(f"{self.output_dir}/inventories/hosts.yml", 'w') as f:
            yaml.dump(inventory, f, default_flow_style=False, indent=2, sort_keys=False)
        
        print("✓ Generated inventory with correct YAML format")
    
    def generate_group_vars(self):
        """Generate group variables for departments"""
        # Network devices group vars
        network_vars = {
            'ansible_network_os': 'ios',
            'ansible_connection': 'network_cli',
            'ansible_user': 'admin',
            'ansible_password': 'admin',
            'ansible_become': 'yes',
            'ansible_become_method': 'enable',
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
        
        # Department-specific group vars
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
        
        print("✓ Generated group variables")
    
    def generate_playbooks(self):
        """Generate deployment playbooks"""
        # VLAN configuration playbook
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
        
        # Main deployment playbook
        deploy_playbook = """---
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
        
        for dept in self.departments:
            vlan_id = dept.get('vlan', 1)
            dept_name = dept.get('name', 'Unknown')
            clean_name = dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
            deploy_playbook += f"""
          - vlan_id: {vlan_id}
            name: "{clean_name}"
            state: active"""
        
        deploy_playbook += """
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
            f.write(deploy_playbook)
        
        print("✓ Generated playbooks")
    
    def generate_deployment_script(self):
        """Generate deployment script"""
        script_content = """#!/bin/bash
# Fixed Network Deployment Script

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
        print("✓ Generated deployment script")
    
    def save_all_files(self):
        """Generate all configuration files"""
        print("🚀 Starting Network Automation Generation...")
        
        # Load network data
        if not self.load_network_data():
            print("❌ Failed to load network data")
            return False
        
        # Create directory structure
        self.create_directory_structure()
        
        # Generate all files
        self.generate_ansible_cfg()
        self.generate_inventory()
        self.generate_group_vars()
        self.generate_playbooks()
        self.generate_deployment_script()
        
        print("\n✅ Generation Summary:")
        print(f"   📁 Output directory: {self.output_dir}")
        print(f"   🏢 Departments processed: {len(self.departments)}")
        print(f"   🖥️  Core infrastructure: {len(self.core_infrastructure)}")
        print(f"   📄 Files created: ansible.cfg, inventory, playbooks, scripts")
        
        print(f"\n🎯 Next steps:")
        print(f"   1. cd {self.output_dir}")
        print(f"   2. ./deploy_network.sh check")
        print(f"   3. ./deploy_network.sh deploy")
        
        return True

if __name__ == "__main__":
    generator = NetworkAutomationGenerator()
    if generator.save_all_files():
        print("\n🎉 SUCCESS: All files generated successfully!")
    else:
        print("\n💥 FAILED: Generation failed!")
        exit(1)