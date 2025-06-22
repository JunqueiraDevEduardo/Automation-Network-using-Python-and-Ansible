#!/usr/bin/env python3
"""
Network Automation Generator - CORRECTED VERSION
Reads network_data.yml and generates complete Ansible automation structure
Creates proper inventory, playbooks, roles, and configuration files
FIXED: Ensures all YAML children entries use dictionary format, not list format
"""

import yaml
import json
import os
from pathlib import Path #Ansible file organization
from typing import Dict, List, Any
import time  # For timestamp generation

class NetworkAutomationGenerator:
    """
    Main generator class that converts network_data.yml into complete Ansible automation
    Creates proper directory structure, inventory, playbooks, and configuration files
    All templates embedded in code - no external template files needed
    FIXED: All children entries use correct dictionary format for Ansible compatibility
    """
    
    def __init__(self, network_data_file: str = "/network_data.yml"):
        """
        Initialize generator with network data file path
        Sets up base paths and loads network configuration
        """
        self.network_data_file = network_data_file
        self.output_dir = "automated/scripts/gns3/"
        self.network_data = None
        self.departments = []
        self.core_infrastructure = []
        
        # Device type mappings for Ansible inventory organization
        self.device_type_mapping = {
            'switch': 'switches',
            'router': 'routers', 
            'pc': 'pcs',
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
    Create simplified Ansible directory structure
    Creates only essential folders for basic automation
    """
    directories = [
        self.output_dir,                           # Main output directory
        f"{self.output_dir}/inventories",          # For inventory files
        f"{self.output_dir}/playbooks",            # For playbook files
        f"{self.output_dir}/group_vars",           # For group variables
        f"{self.output_dir}/roles/network-config/tasks",  # Single role for all network tasks
        f"{self.output_dir}/roles/network-config/vars"    # Single role variables
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
    print(f"Created simplified directory structure in {self.output_dir}")
    
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
    Uses only real values from network configuration
    Creates simple, clean inventory structure
    """
    # Initialize basic inventory structure with device type groups
    inventory = {
        'all': {
            'children': {
                'switches': {'hosts': {}},      # All switches as hosts
                'routers': {'hosts': {}},       # All routers as hosts  
                'pcs': {'hosts': {}},           # All PCs as hosts
                'servers': {'hosts': {}},       # All servers as hosts
                'printers': {'hosts': {}},      # All printers as hosts
                'core_infrastructure': {'hosts': {}}  # Core devices as hosts
            }
        }
    }
    
    # Process core infrastructure devices
    for device in self.core_infrastructure:
        device_name = device['name']  # No default - must exist
        device_info = {
            'ansible_host': device['ip'],           # Use exact IP from YAML
            'device_type': device['type'],          # Use exact type from YAML
            'department': 'core'                    # Mark as core infrastructure
        }
        # Add to core_infrastructure group
        inventory['all']['children']['core_infrastructure']['hosts'][device_name] = device_info
    
    # Process each department using only real values
    for dept in self.departments:
        # Extract department information - no defaults, must exist
        dept_name = dept['name']        # Real department name
        vlan_id = dept['vlan']          # Real VLAN ID
        subnet = dept['subnet']         # Real subnet
        gateway = dept['gateway']       # Real gateway
        devices = dept.get('devices', [])  # Device list (can be empty)
        
        # Create department-specific group for organization
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
            device_name = device['name']        # Real device name
            device_type = device['type']        # Real device type
            device_ip = device['ip']            # Real device IP
            
            # Create device information with real values
            device_info = {
                'ansible_host': device_ip,      # Real IP address
                'device_type': device_type,     # Real device type
                'department': dept_name,        # Department assignment
                'vlan_id': vlan_id,            # VLAN assignment
                'subnet': subnet,              # Subnet information
                'gateway': gateway             # Gateway information
            }
            
            # Add connection settings based on device type
            if device_type in ['switch', 'router']:
                # Network devices use network_cli connection
                device_info.update({
                    'ansible_network_os': 'ios',
                    'ansible_connection': 'network_cli',
                    'ansible_user': 'admin',
                    'ansible_password': 'admin',
                    'ansible_become': 'yes',
                    'ansible_become_method': 'enable'
                })
            elif device_type in ['pc', 'server', 'printer']:
                # End devices use SSH connection
                device_info.update({
                    'ansible_connection': 'ssh',
                    'ansible_user': 'admin',
                    'ansible_become': 'yes',
                    'ansible_become_method': 'sudo'
                })
            
            # Place device in correct group using device_type_mapping
            if device_type in self.device_type_mapping:
                group_name = self.device_type_mapping[device_type]
                inventory['all']['children'][group_name]['hosts'][device_name] = device_info
            else:
                print(f"Warning: Unknown device type '{device_type}' for device '{device_name}'")
            
            # Also add device to its department group
            inventory['all']['children'][dept_group_name]['hosts'][device_name] = device_info
    
    # Save inventory file with proper formatting
    with open(f"{self.output_dir}/inventories/hosts.yml", 'w') as f:
        yaml.dump(inventory, f, 
                 default_flow_style=False,     # Readable format
                 indent=2,                     # 2-space indentation
                 sort_keys=False)              # Keep original order
    
    print(f"Generated inventory file: {self.output_dir}/inventories/hosts.yml")
    print(f"Total devices processed: {sum(len(group['hosts']) for group in inventory['all']['children'].values())}")

def generate_group_vars(self):
    """
    Generate group variables for device types and departments
    Uses only real values from network_data.yml
    Creates variables that match the simplified inventory structure
    """
    
    # Variables for switches group
    switches_vars = {
        'ansible_network_os': 'ios',           # Cisco IOS for switches
        'ansible_connection': 'network_cli',   # Network CLI connection type
        'ansible_user': 'admin',               # Switch username
        'ansible_password': 'admin',           # Switch password
        'ansible_become': 'yes',               # Enable privilege escalation
        'ansible_become_method': 'enable',     # Use Cisco enable mode
        'dns_servers': ['8.8.8.8', '8.8.4.4'], # Public DNS servers
        'domain_name': 'company.local'         # Company domain
    }
    
    with open(f"{self.output_dir}/group_vars/switches.yml", 'w') as f:
        yaml.dump(switches_vars, f, default_flow_style=False, indent=2)
    
    # Variables for routers group
    routers_vars = {
        'ansible_network_os': 'ios',           # Cisco IOS for routers
        'ansible_connection': 'network_cli',   # Network CLI connection type
        'ansible_user': 'admin',               # Router username
        'ansible_password': 'admin',           # Router password
        'ansible_become': 'yes',               # Enable privilege escalation
        'ansible_become_method': 'enable',     # Use Cisco enable mode
        'dns_servers': ['8.8.8.8', '8.8.4.4'], # Public DNS servers
        'domain_name': 'company.local'         # Company domain
    }
    
    with open(f"{self.output_dir}/group_vars/routers.yml", 'w') as f:
        yaml.dump(routers_vars, f, default_flow_style=False, indent=2)
    
    # Variables for PCs group
    pcs_vars = {
        'ansible_connection': 'ssh',           # SSH connection for PCs
        'ansible_user': 'admin',               # PC username
        'ansible_become': 'yes',               # Enable sudo
        'ansible_become_method': 'sudo',       # Use sudo for privilege escalation
        'dns_servers': ['8.8.8.8', '8.8.4.4'], # Public DNS servers
        'domain_name': 'company.local'         # Company domain
    }
    
    with open(f"{self.output_dir}/group_vars/pcs.yml", 'w') as f:
        yaml.dump(pcs_vars, f, default_flow_style=False, indent=2)
    
    # Variables for servers group
    servers_vars = {
        'ansible_connection': 'ssh',           # SSH connection for servers
        'ansible_user': 'admin',               # Server username
        'ansible_become': 'yes',               # Enable sudo
        'ansible_become_method': 'sudo',       # Use sudo for privilege escalation
        'dns_servers': ['8.8.8.8', '8.8.4.4'], # Public DNS servers
        'domain_name': 'company.local'         # Company domain
    }
    
    with open(f"{self.output_dir}/group_vars/servers.yml", 'w') as f:
        yaml.dump(servers_vars, f, default_flow_style=False, indent=2)
    
    # Variables for printers group
    printers_vars = {
        'ansible_connection': 'ssh',           # SSH connection for printers
        'ansible_user': 'admin',               # Printer username
        'ansible_become': 'yes',               # Enable sudo
        'ansible_become_method': 'sudo',       # Use sudo for privilege escalation
        'dns_servers': ['8.8.8.8', '8.8.4.4'], # Public DNS servers
        'domain_name': 'company.local'         # Company domain
    }
    
    with open(f"{self.output_dir}/group_vars/printers.yml", 'w') as f:
        yaml.dump(printers_vars, f, default_flow_style=False, indent=2)
    
    # Variables for core infrastructure
    core_vars = {
        'ansible_network_os': 'ios',           # Cisco IOS for core switch
        'ansible_connection': 'network_cli',   # Network CLI connection
        'ansible_user': 'admin',               # Core switch username
        'ansible_password': 'admin',           # Core switch password
        'ansible_become': 'yes',               # Enable privilege escalation
        'ansible_become_method': 'enable',     # Use Cisco enable mode
        'dns_servers': ['8.8.8.8', '8.8.4.4'], # Public DNS servers
        'domain_name': 'company.local'         # Company domain
    }
    
    with open(f"{self.output_dir}/group_vars/core_infrastructure.yml", 'w') as f:
        yaml.dump(core_vars, f, default_flow_style=False, indent=2)
    
    # Generate department-specific group variables using real values only
    for dept in self.departments:
        dept_name = dept['name']        # Real department name - no default
        vlan_id = dept['vlan']          # Real VLAN ID - no default
        subnet = dept['subnet']         # Real subnet - no default
        gateway = dept['gateway']       # Real gateway - no default
        
        # Create department variables with real values
        dept_vars = {
            'department_name': dept_name,
            'vlan_id': vlan_id,
            'subnet': subnet,
            'gateway': gateway,
            # Create clean VLAN name from department name
            'vlan_name': dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
        }
        
        # Save department variables file
        with open(f"{self.output_dir}/group_vars/dept_{vlan_id}.yml", 'w') as f:
            yaml.dump(dept_vars, f, default_flow_style=False, indent=2)
    
    print("Generated group variables for all device types and departments")
    print(f"Created {len(self.departments) + 6} group variable files")
def generate_network_role(self):
    """
    Generate complete network configuration role for switches and routers
    Uses simplified single-role structure with real values only
    Does NOT include PCs/servers/printers (they use different connection methods)
    """
    
    # Complete network configuration tasks for switches and routers
    network_tasks = """---
# Network Configuration Tasks for Switches and Routers Only
# End devices (PCs, servers, printers) use SSH and different configuration methods

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

# Configure router department interface (main LAN interface)
- name: Configure router department LAN interface
  cisco.ios.ios_config:
    lines:
      - "ip address {{ ansible_host }} {{ subnet | ipaddr('netmask') }}"
      - "no shutdown"
      - "description {{ department }} Department LAN Gateway"
    parents: interface GigabitEthernet0/0
  when: device_type == "router"
  tags: [interfaces, routers]

# Configure router uplink interface (connection to core network)
- name: Configure router uplink interface
  cisco.ios.ios_config:
    lines:
      - "ip address {{ ansible_host | regex_replace('\\.[0-9]+$', '.254') }} 255.255.255.0"
      - "no shutdown"
      - "description Uplink to Core Network"
    parents: interface GigabitEthernet0/1
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

# Configure console access
- name: Configure console line
  cisco.ios.ios_config:
    lines:
      - "login local"
      - "exec-timeout 30 0"
    parents: line console 0
  when: device_type in ["switch", "router"]
  tags: [console_access, network_devices]

# Save configuration on all network devices
- name: Save running configuration
  cisco.ios.ios_config:
    save_when: always
  when: device_type in ["switch", "router"]
  tags: [save, network_devices]
"""
    
    # Write the tasks file to the simplified role structure
    with open(f"{self.output_dir}/roles/network-config/tasks/main.yml", 'w') as f:
        f.write(network_tasks)
    
    # Generate role variables using real department data
    network_vars = {
        'domain_name': 'company.local',  # Company domain name
        'department_vlans': []  # Will be populated with real VLAN data
    }
    
    # Generate VLAN configurations using real department data
    for dept in self.departments:
        vlan_id = dept['vlan']      # Real VLAN ID - no defaults
        dept_name = dept['name']    # Real department name - no defaults
        
        # Create clean VLAN name for Cisco (replace problematic characters)
        clean_vlan_name = dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
        
        # Add VLAN configuration with real values
        network_vars['department_vlans'].append({
            'vlan_id': vlan_id,
            'name': clean_vlan_name,
            'state': 'active'
        })
    
    # Write the variables file with real department VLANs
    with open(f"{self.output_dir}/roles/network-config/vars/main.yml", 'w') as f:
        yaml.dump(network_vars, f, default_flow_style=False, indent=2)
    
    print("Generated complete network configuration role for switches and routers")
    print(f"Created VLAN configurations for {len(self.departments)} departments")
    print("Note: PCs, servers, and printers use different configuration methods (SSH)")
def generate_end_devices_role(self):
    """
    Generate end devices configuration role for PCs, servers, and printers
    Uses simplified directory structure with real values
    Handles all end devices that use SSH connection (not network_cli like switches/routers)
    
    Device Types Handled:
    - PCs/Laptops: Basic workstation configuration
    - Servers: Enhanced configuration with additional services
    - Printers: Basic configuration with printing services
    """
    
    # End devices configuration tasks with proper YAML formatting
    # This handles all devices that connect via SSH (PCs, servers, printers)
    # NOT for switches/routers which use network_cli connection
    end_devices_tasks = """---
# End Devices Configuration Tasks
# Handles PCs, laptops, servers, and printers that use SSH connection
# These devices run Linux/Unix OS, not Cisco IOS

# NETWORK CONFIGURATION FOR UBUNTU/DEBIAN SYSTEMS
# This configures static IP addresses for PCs, servers, and printers
# Uses netplan (modern Ubuntu network configuration system)
- name: Configure network interface using netplan
  copy:
    content: |
      network:
        version: 2                    # Netplan version 2 format
        renderer: networkd            # Use systemd-networkd as backend
        ethernets:
          {{ ansible_default_ipv4.interface | default('eth0') }}:
            addresses:
              - {{ ansible_host }}/{{ subnet.split('/')[1] }}  # Static IP from inventory
            gateway4: {{ gateway }}    # Department gateway (router IP)
            nameservers:
              addresses:
                - 8.8.8.8             # Google primary DNS
                - 8.8.4.4             # Google secondary DNS
              search:
                - company.local       # Local domain search
    dest: /etc/netplan/01-network-config.yaml
    backup: yes                       # Backup original configuration
  when: 
    - ansible_os_family == "Debian"  # Only for Ubuntu/Debian systems
    - ansible_distribution_major_version|int >= 18  # Ubuntu 18.04+
  notify: apply netplan              # Trigger handler to apply changes
  tags: [network, ubuntu]

# NETWORK CONFIGURATION FOR CENTOS/RHEL SYSTEMS
# This configures static IP addresses for older Linux distributions
# Uses traditional ifcfg files instead of netplan
- name: Configure network interface for RedHat systems
  copy:
    content: |
      TYPE=Ethernet                   # Interface type
      BOOTPROTO=static               # Static IP configuration
      IPADDR={{ ansible_host }}      # Static IP from inventory
      NETMASK={{ subnet | ipaddr('netmask') }}  # Calculate netmask from subnet
      GATEWAY={{ gateway }}          # Department gateway
      DNS1=8.8.8.8                  # Primary DNS server
      DNS2=8.8.4.4                  # Secondary DNS server
      ONBOOT=yes                    # Enable interface at boot
      DEVICE={{ ansible_default_ipv4.interface | default('eth0') }}
    dest: "/etc/sysconfig/network-scripts/ifcfg-{{ ansible_default_ipv4.interface | default('eth0') }}"
    backup: yes                     # Backup original configuration
  when: ansible_os_family == "RedHat"  # Only for CentOS/RHEL systems
  notify: restart network           # Trigger handler to restart networking
  tags: [network, rhel]

# BASIC PACKAGE INSTALLATION FOR PCs AND SERVERS
# Installs essential software packages for workstations and servers
# Does NOT apply to printers (they have different software needs)
- name: Install basic packages for PCs and servers
  package:
    name: "{{ basic_packages }}"     # List defined in variables
    state: present                   # Ensure packages are installed
  when: device_type in ["pc", "server"]  # Only for PCs and servers, not printers
  tags: [packages]

# SERVER-SPECIFIC PACKAGE INSTALLATION
# Additional packages only installed on servers
# Includes web servers, databases, security tools
- name: Install server additional packages
  package:
    name: "{{ server_packages }}"    # Server-specific package list
    state: present                   # Ensure packages are installed
  when: device_type == "server"     # Only for devices marked as servers
  tags: [packages, servers]

# DNS CONFIGURATION FOR ALL END DEVICES
# Sets up DNS resolution for PCs, servers, and printers
# Ensures all devices can resolve domain names
- name: Configure DNS resolver for all end devices
  copy:
    content: |
      nameserver 8.8.8.8            # Google primary DNS
      nameserver 8.8.4.4            # Google secondary DNS
      search company.local           # Local domain search suffix
    dest: /etc/resolv.conf           # Standard DNS configuration file
    backup: yes                      # Backup original configuration
  tags: [dns]

# HOSTNAME CONFIGURATION FOR ALL END DEVICES
# Sets the system hostname to match Ansible inventory name
# Applies to PCs, servers, and printers
- name: Set hostname for all end devices
  hostname:
    name: "{{ inventory_hostname }}" # Use name from Ansible inventory
  tags: [hostname]

# PRINTER-SPECIFIC CONFIGURATION
# Configures printing services only on devices marked as printers
# Enables CUPS (Common Unix Printing System) service
- name: Configure printer services for printers only
  service:
    name: cups                       # CUPS printing service
    state: started                   # Ensure service is running
    enabled: yes                     # Enable service at boot
  when: device_type == "printer"    # Only for devices marked as printers
  ignore_errors: yes               # Continue if CUPS not available
  tags: [printers]

# OPTIONAL SYSTEM UPDATES
# Updates all system packages (disabled by default)
# Only applies to PCs and servers, not printers
- name: Update system packages (optional)
  package:
    name: "*"                        # All packages
    state: latest                    # Update to latest versions
  when: 
    - update_packages | default(false)  # Only if enabled in variables
    - device_type in ["pc", "server"]   # Not for printers
  tags: [updates]
"""
    
    # Write tasks to the simplified role structure
    # This creates a separate task file for end devices within the network-config role
    with open(f"{self.output_dir}/roles/network-config/tasks/end_devices.yml", 'w') as f:
        f.write(end_devices_tasks)
    
    # Create handlers for end devices
    # Handlers are triggered when configuration changes need to restart services
    end_devices_handlers = """---
# End Devices Configuration Handlers
# These handlers restart network services when configuration changes

# Handler for Ubuntu/Debian systems using netplan
- name: apply netplan
  command: netplan apply            # Apply netplan configuration changes
  become: yes                       # Run with sudo privileges

# Handler for CentOS/RHEL systems using network service
- name: restart network
  service:
    name: network                   # Network service name
    state: restarted               # Restart the service
  become: yes                      # Run with sudo privileges

# Alternative handler for some Debian systems
- name: restart networking
  service:
    name: networking               # Networking service name
    state: restarted              # Restart the service
  become: yes                     # Run with sudo privileges
"""
    
    # Create handlers directory if it doesn't exist
    # Handlers are stored in a separate directory within the role
    handlers_dir = f"{self.output_dir}/roles/network-config/handlers"
    Path(handlers_dir).mkdir(parents=True, exist_ok=True)
    
    # Write handlers file
    with open(f"{handlers_dir}/main.yml", 'w') as f:
        f.write(end_devices_handlers)
    
    # Define variables for end device configuration
    # These variables are used by the tasks above
    end_devices_vars = {
        # Basic packages installed on ALL PCs and servers (not printers)
        'basic_packages': [
            'curl',                # HTTP client for downloading files
            'wget',                # Alternative download utility
            'net-tools',           # Network diagnostic tools (ifconfig, netstat)
            'openssh-server',      # SSH server for remote access
            'htop',                # Interactive process monitor
            'vim',                 # Advanced text editor
            'git'                  # Version control system
        ],
        # Additional packages ONLY installed on servers
        'server_packages': [
            'nginx',               # Web server for hosting websites
            'mysql-server',        # Database server for data storage
            'fail2ban',            # Security tool to prevent brute force attacks
            'ufw',                 # Uncomplicated Firewall for security
            'rsync'                # File synchronization and backup utility
        ],
        'update_packages': False,  # Set to true to enable automatic package updates
        'domain_name': 'company.local'  # Company domain name
    }
    
    # Read existing variables file and merge with end device variables
    # This ensures we don't overwrite existing network device variables
    vars_file = f"{self.output_dir}/roles/network-config/vars/main.yml"
    try:
        with open(vars_file, 'r') as f:
            existing_vars = yaml.safe_load(f) or {}
    except FileNotFoundError:
        existing_vars = {}
    
    # Merge end device variables with existing variables
    # This combines network device vars with end device vars in one file
    existing_vars.update(end_devices_vars)
    
    # Write updated variables file
    with open(vars_file, 'w') as f:
        yaml.dump(existing_vars, f, default_flow_style=False, indent=2)
    
    # Print summary of what was generated
    print("Generated end devices configuration for PCs, servers, and printers")
    print("Device-specific configurations:")
    print("  - PCs: Basic packages + network configuration")
    print("  - Servers: Basic packages + server packages + network configuration")
    print("  - Printers: Network configuration + CUPS printing service")
    print("Added end device tasks to unified network-config role")
    print(f"Configured {len(end_devices_vars['basic_packages'])} basic packages and {len(end_devices_vars['server_packages'])} server packages")
def generate_playbooks(self):
    """
    Generate main playbooks for network deployment
    Creates simplified playbooks that use the unified network-config role
    Generates site-wide deployment and device-specific playbooks
    """
    
    # MAIN SITE DEPLOYMENT PLAYBOOK
    # This is the master playbook that configures the entire network
    # It handles both network infrastructure and end devices
    site_playbook = """---
# Main Site Deployment Playbook
# This playbook configures the complete network infrastructure
# Run this to deploy the entire network from scratch

# CONFIGURE NETWORK INFRASTRUCTURE (Switches and Routers)
# Uses network_cli connection for Cisco devices
- name: Configure Network Infrastructure Devices
  hosts: switches:routers:core_infrastructure  # All network hardware
  gather_facts: no                            # Skip fact gathering for network devices
  connection: network_cli                     # Use network CLI connection
  vars:
    ansible_network_os: ios                   # Cisco IOS operating system
  roles:
    - network-config                          # Unified role for all network config
  tags: [network, infrastructure]

# CONFIGURE END DEVICES (PCs, Servers, Printers)
# Uses SSH connection for Linux/Unix systems
- name: Configure End Devices
  hosts: pcs:servers:printers                 # All end user devices
  gather_facts: yes                          # Gather facts for end devices
  become: yes                                # Use sudo for privilege escalation
  connection: ssh                            # Use SSH connection
  vars:
    ansible_user: admin                      # SSH username
  roles:
    - network-config                         # Same role, different tasks
  tags: [endpoints, end_devices]
"""
    
    # Write the main site playbook
    with open(f"{self.output_dir}/site.yml", 'w') as f:
        f.write(site_playbook)
    
    # NETWORK DEVICES ONLY PLAYBOOK
    # This playbook configures only switches and routers
    # Useful for network-only updates without touching end devices
    network_playbook = """---
# Network Devices Only Configuration Playbook
# Configures switches, routers, and core infrastructure
# Does NOT configure PCs, servers, or printers

- name: Configure Network Infrastructure Only
  hosts: switches:routers:core_infrastructure  # Only network devices
  gather_facts: no                            # Skip fact gathering
  connection: network_cli                     # Network CLI connection
  vars:
    ansible_network_os: ios                   # Cisco IOS
    ansible_user: admin                       # Device username
    ansible_password: admin                   # Device password
  
  tasks:
    # CONFIGURE VLANs ON SWITCHES USING REAL DEPARTMENT DATA
    - name: Configure department VLANs on switches
      cisco.ios.ios_vlans:
        config:"""
    
    # Add real VLAN configurations from departments (no defaults)
    for dept in self.departments:
        vlan_id = dept['vlan']      # Real VLAN ID - no default
        dept_name = dept['name']    # Real department name - no default
        # Clean department name for Cisco VLAN naming requirements
        clean_name = dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
        network_playbook += f"""
          - vlan_id: {vlan_id}
            name: "{clean_name}"
            state: active"""
    
    # Continue with network playbook tasks
    network_playbook += """
        state: merged                         # Merge with existing config
      when: device_type == "switch"          # Only run on switches
      tags: [vlans, switches]

    # CONFIGURE SWITCH MANAGEMENT INTERFACES
    - name: Configure switch management interface
      cisco.ios.ios_config:
        lines:
          - "ip address {{ ansible_host }} {{ subnet | ipaddr('netmask') }}"
          - "no shutdown"
          - "description Management Interface"
        parents: interface vlan1              # Management VLAN interface
      when: device_type == "switch"          # Only run on switches
      tags: [mgmt_interface, switches]

    # CONFIGURE ROUTER INTERFACES  
    - name: Configure router department interface
      cisco.ios.ios_config:
        lines:
          - "ip address {{ ansible_host }} {{ subnet | ipaddr('netmask') }}"
          - "no shutdown"
          - "description {{ department }} Department Gateway"
        parents: interface GigabitEthernet0/0  # Main LAN interface
      when: device_type == "router"          # Only run on routers
      tags: [router_interface, routers]

    # SAVE CONFIGURATION ON ALL NETWORK DEVICES
    - name: Save running configuration
      cisco.ios.ios_config:
        save_when: always                    # Always save changes
      when: device_type in ["switch", "router"]
      tags: [save, network_devices]
"""
    
    # Write the network-only playbook
    with open(f"{self.output_dir}/playbooks/deploy_network.yml", 'w') as f:
        f.write(network_playbook)
    
    # VLAN CONFIGURATION ONLY PLAYBOOK
    # This playbook only configures VLANs on switches
    # Useful for adding new VLANs without full device reconfiguration
    vlan_playbook = """---
# VLAN Configuration Only Playbook
# Configures department VLANs on switches only
# Does NOT configure interfaces or other settings

- name: Configure VLANs on Switches Only
  hosts: switches                            # Only switch devices
  gather_facts: no                          # Skip fact gathering
  connection: network_cli                   # Network CLI connection
  vars:
    ansible_network_os: ios                 # Cisco IOS
    ansible_user: admin                     # Switch username
    ansible_password: admin                 # Switch password
  
  tasks:
    # CONFIGURE ALL DEPARTMENT VLANs USING REAL DATA
    - name: Configure department VLANs with real IDs and names
      cisco.ios.ios_vlans:
        config:"""
    
    # Add real VLAN configurations (no defaults)
    for dept in self.departments:
        vlan_id = dept['vlan']      # Real VLAN ID from network_data.yml
        dept_name = dept['name']    # Real department name
        # Clean name for Cisco compatibility
        clean_name = dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
        vlan_playbook += f"""
          - vlan_id: {vlan_id}                # Real VLAN ID: {vlan_id}
            name: "{clean_name}"              # Clean name: {clean_name}
            state: active                     # VLAN is active"""
    
    # Complete VLAN playbook
    vlan_playbook += """
        state: merged                         # Merge with existing VLANs
      tags: [vlans]

    # SAVE VLAN CONFIGURATION
    - name: Save VLAN configuration to startup-config
      cisco.ios.ios_config:
        save_when: always                    # Always save changes
      tags: [save]
"""
    
    # Write the VLAN-only playbook
    with open(f"{self.output_dir}/playbooks/configure_vlans.yml", 'w') as f:
        f.write(vlan_playbook)
    
    # END DEVICES ONLY PLAYBOOK
    # This playbook configures only PCs, servers, and printers
    # Useful for end device updates without touching network infrastructure
    end_devices_playbook = """---
# End Devices Only Configuration Playbook
# Configures PCs, servers, and printers only
# Does NOT configure switches or routers

- name: Configure End Devices Only
  hosts: pcs:servers:printers                # Only end devices
  gather_facts: yes                          # Need facts for end devices
  become: yes                                # Use sudo privileges
  connection: ssh                            # SSH connection
  vars:
    ansible_user: admin                      # SSH username
  
  tasks:
    # INCLUDE END DEVICE TASKS FROM ROLE
    - name: Include end device configuration tasks
      include_tasks: "{{ role_path }}/tasks/end_devices.yml"
      tags: [end_devices, configuration]

    # INSTALL BASIC PACKAGES ON PCs AND SERVERS
    - name: Install basic packages
      package:
        name: "{{ basic_packages }}"
        state: present
      when: device_type in ["pc", "server"]
      tags: [packages]

    # CONFIGURE HOSTNAME FOR ALL END DEVICES
    - name: Set hostname
      hostname:
        name: "{{ inventory_hostname }}"
      tags: [hostname]
"""
    
    # Write the end devices playbook
    with open(f"{self.output_dir}/playbooks/configure_end_devices.yml", 'w') as f:
        f.write(end_devices_playbook)
    
    # Print summary of generated playbooks
    print("Generated playbooks with real VLAN configurations and comprehensive comments")
    print("Created playbooks:")
    print("  - site.yml: Complete network deployment")
    print("  - deploy_network.yml: Network devices only") 
    print("  - configure_vlans.yml: VLAN configuration only")
    print("  - configure_end_devices.yml: End devices only")
    print(f"Configured VLANs for {len(self.departments)} departments using real data")
def generate_playbooks(self):
    """
    Generate main playbooks for network deployment
    Creates simplified playbooks that use the unified network-config role
    Uses correct inventory groups and real values from network_data.yml
    """
    
    # MAIN SITE DEPLOYMENT PLAYBOOK
    # This is the master playbook that deploys the entire network infrastructure
    # It configures both network devices (switches/routers) and end devices (PCs/servers/printers)
    site_playbook = """---
# Main Site Deployment Playbook
# Complete network deployment for university network automation project
# Configures all devices: switches, routers, PCs, servers, and printers

# PHASE 1: CONFIGURE NETWORK INFRASTRUCTURE
# This phase configures switches, routers, and core infrastructure
# Uses network_cli connection for Cisco IOS devices
- name: Configure Network Infrastructure Devices
  hosts: switches:routers:core_infrastructure    # All network hardware devices
  gather_facts: no                              # Skip fact gathering for network devices
  connection: network_cli                       # Use Cisco network CLI connection
  vars:
    ansible_network_os: ios                     # Specify Cisco IOS operating system
    ansible_user: admin                         # Network device username
    ansible_password: admin                     # Network device password
  roles:
    - network-config                            # Unified role for all network configuration
  tags: [network, infrastructure, switches, routers]

# PHASE 2: CONFIGURE END USER DEVICES  
# This phase configures PCs, servers, and printers
# Uses SSH connection for Linux/Unix systems
- name: Configure End User Devices
  hosts: pcs:servers:printers                   # All end user devices
  gather_facts: yes                             # Gather system facts for end devices
  become: yes                                   # Use sudo for privilege escalation
  connection: ssh                               # Use SSH connection for Linux systems
  vars:
    ansible_user: admin                         # SSH username for end devices
  roles:
    - network-config                            # Same role, different tasks for end devices
  tags: [endpoints, end_devices, pcs, servers, printers]
"""
    
    # Write the main site deployment playbook
    with open(f"{self.output_dir}/site.yml", 'w') as f:
        f.write(site_playbook)
    
    # NETWORK DEVICES ONLY PLAYBOOK
    # This playbook configures only network infrastructure (switches and routers)
    # Useful for network updates without affecting end user devices
    network_playbook = """---
# Network Infrastructure Only Playbook
# Configures switches, routers, and core infrastructure only
# Does NOT configure PCs, servers, or printers

- name: Configure Network Infrastructure Only
  hosts: switches:routers:core_infrastructure    # Only network infrastructure devices
  gather_facts: no                              # Skip fact gathering for network devices
  connection: network_cli                       # Cisco network CLI connection
  vars:
    ansible_network_os: ios                     # Cisco IOS operating system
    ansible_user: admin                         # Network device username  
    ansible_password: admin                     # Network device password
  
  tasks:
    # CONFIGURE DEPARTMENT VLANs ON SWITCHES
    # This task creates VLANs for each department using real data from network_data.yml
    - name: Configure department VLANs on switches using real data
      cisco.ios.ios_vlans:
        config:"""
    
    # Generate VLAN configurations using real department data (no defaults)
    for dept in self.departments:
        vlan_id = dept['vlan']      # Real VLAN ID from network_data.yml
        dept_name = dept['name']    # Real department name from network_data.yml
        # Clean department name for Cisco VLAN naming (remove special characters)
        clean_name = dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
        network_playbook += f"""
          - vlan_id: {vlan_id}                  # VLAN {vlan_id} for {dept_name}
            name: "{clean_name}"                # Clean name: {clean_name}
            state: active                       # VLAN is active and operational"""
    
    # Continue with network infrastructure tasks
    network_playbook += """
        state: merged                           # Merge with existing VLAN configuration
      when: device_type == "switch"            # Only execute on switch devices
      tags: [vlans, switches]

    # CONFIGURE SWITCH MANAGEMENT INTERFACES
    # This configures the management IP address on each switch
    - name: Configure switch management interface with real subnet
      cisco.ios.ios_config:
        lines:
          - "ip address {{ ansible_host }} {{ subnet | ipaddr('netmask') }}"  # Real IP and netmask
          - "no shutdown"                      # Bring interface up
          - "description Management Interface for {{ department }}"  # Interface description
        parents: interface vlan1               # Management VLAN interface
      when: device_type == "switch"           # Only execute on switch devices
      tags: [mgmt_interface, switches]

    # CONFIGURE ROUTER DEPARTMENT INTERFACES
    # This configures the main LAN interface on each department router
    - name: Configure router department interface with real subnet
      cisco.ios.ios_config:
        lines:
          - "ip address {{ ansible_host }} {{ subnet | ipaddr('netmask') }}"  # Real IP and netmask
          - "no shutdown"                      # Bring interface up
          - "description {{ department }} Department Gateway"  # Interface description
        parents: interface GigabitEthernet0/0  # Main LAN interface
      when: device_type == "router"           # Only execute on router devices
      tags: [router_interface, routers]

    # SAVE CONFIGURATION ON ALL NETWORK DEVICES
    # This saves the running configuration to startup configuration
    - name: Save running configuration to startup configuration
      cisco.ios.ios_config:
        save_when: always                     # Always save configuration changes
      when: device_type in ["switch", "router"]  # All network devices
      tags: [save, network_devices]
"""
    
    # Write the network infrastructure only playbook
    with open(f"{self.output_dir}/playbooks/deploy_network.yml", 'w') as f:
        f.write(network_playbook)
    
    # VLAN CONFIGURATION ONLY PLAYBOOK
    # This playbook only configures VLANs on switches
    # Useful for adding new VLANs or modifying existing ones without full reconfiguration
    vlan_playbook = """---
# VLAN Configuration Only Playbook
# Configures department VLANs on switches only
# Useful for VLAN updates without full device reconfiguration

- name: Configure Department VLANs on Switches Only
  hosts: switches                              # Only switch devices
  gather_facts: no                            # Skip fact gathering
  connection: network_cli                     # Cisco network CLI connection
  vars:
    ansible_network_os: ios                   # Cisco IOS operating system
    ansible_user: admin                       # Switch username
    ansible_password: admin                   # Switch password
  
  tasks:
    # CONFIGURE ALL DEPARTMENT VLANs USING REAL DATA
    # Creates VLANs for each department from network_data.yml
    - name: Configure department VLANs with real VLAN IDs and names
      cisco.ios.ios_vlans:
        config:"""
    
    # Generate VLAN configurations using real department data only
    for dept in self.departments:
        vlan_id = dept['vlan']      # Real VLAN ID (no default values)
        dept_name = dept['name']    # Real department name (no default values)
        # Clean department name for Cisco VLAN naming requirements
        clean_name = dept_name.replace('/', '-').replace(' ', '-').replace('&', 'and')
        vlan_playbook += f"""
          - vlan_id: {vlan_id}                  # Department: {dept_name} - VLAN {vlan_id}
            name: "{clean_name}"                # Cisco-compatible name: {clean_name}
            state: active                       # VLAN is active and ready for use"""
    
    # Complete the VLAN configuration playbook
    vlan_playbook += """
        state: merged                           # Merge with existing VLAN database
      tags: [vlans]

    # SAVE VLAN CONFIGURATION
    # Saves the VLAN configuration to persistent storage
    - name: Save VLAN configuration to startup-config
      cisco.ios.ios_config:
        save_when: always                      # Always save VLAN changes
      tags: [save]
"""
    
    # Write the VLAN configuration only playbook
    with open(f"{self.output_dir}/playbooks/configure_vlans.yml", 'w') as f:
        f.write(vlan_playbook)
    
    # END DEVICES ONLY PLAYBOOK
    # This playbook configures only end user devices (PCs, servers, printers)
    # Useful for end device updates without touching network infrastructure
    end_devices_playbook = """---
# End Devices Only Configuration Playbook
# Configures PCs, servers, and printers only
# Does NOT configure network infrastructure (switches/routers)

- name: Configure End User Devices Only
  hosts: pcs:servers:printers                  # All end user devices
  gather_facts: yes                            # Need system facts for end devices
  become: yes                                  # Use sudo for system configuration
  connection: ssh                              # SSH connection for Linux systems
  vars:
    ansible_user: admin                        # SSH username for end devices
  
  tasks:
    # CONFIGURE NETWORK SETTINGS FOR ALL END DEVICES
    # This configures static IP addresses for PCs, servers, and printers
    - name: Configure network interface with static IP
      copy:
        content: |
          network:
            version: 2
            renderer: networkd
            ethernets:
              {{ ansible_default_ipv4.interface | default('eth0') }}:
                addresses:
                  - {{ ansible_host }}/{{ subnet.split('/')[1] }}  # Static IP from inventory
                gateway4: {{ gateway }}         # Department gateway (router IP)
                nameservers:
                  addresses:
                    - 8.8.8.8                  # Google primary DNS
                    - 8.8.4.4                  # Google secondary DNS
                  search:
                    - company.local            # Local domain search
        dest: /etc/netplan/01-network-config.yaml
        backup: yes                            # Backup original configuration
      when: ansible_os_family == "Debian"     # Only for Ubuntu/Debian systems
      notify: apply netplan                    # Trigger network restart
      tags: [network, ubuntu]

    # INSTALL BASIC PACKAGES ON PCs AND SERVERS
    # Installs essential software packages for workstations and servers
    - name: Install basic packages for PCs and servers
      package:
        name: "{{ basic_packages }}"           # Package list from role variables
        state: present                         # Ensure packages are installed
      when: device_type in ["pc", "server"]   # Only for PCs and servers, not printers
      tags: [packages]

    # SET HOSTNAME FOR ALL END DEVICES
    # Configures system hostname to match Ansible inventory name
    - name: Set system hostname
      hostname:
        name: "{{ inventory_hostname }}"       # Use inventory hostname
      tags: [hostname]
"""
    
    # Write the end devices only playbook
    with open(f"{self.output_dir}/playbooks/configure_end_devices.yml", 'w') as f:
        f.write(end_devices_playbook)
    
    # Print comprehensive summary of generated playbooks
    print("Generated complete set of playbooks with real VLAN configurations and detailed comments")
    print("Created playbooks for university network automation project:")
    print("  1. site.yml - Complete network deployment (all devices)")
    print("  2. deploy_network.yml - Network infrastructure only (switches/routers)")
    print("  3. configure_vlans.yml - VLAN configuration only (switches)")
    print("  4. configure_end_devices.yml - End devices only (PCs/servers/printers)")
    print(f"Configured {len(self.departments)} department VLANs using real data from network_data.yml")
    print("All playbooks use simplified network-config role structure")
def generate_network_documentation(self):
    """
    Generate comprehensive network documentation using real values only
    Creates README and topology reference files for university project presentation
    Uses only actual data from network_data.yml without any default values
    """
    
    # Calculate total devices across all departments using real data
    total_dept_devices = sum(len(dept['devices']) for dept in self.departments)
    total_devices = total_dept_devices + len(self.core_infrastructure)
    
    # Generate comprehensive README with project overview
    readme_content = f"""# University Network Automation Project
**Manual vs Automated Network Deployment Comparison**

## Project Overview
This project demonstrates the transformation of a manual Cisco Packet Tracer network design into a fully automated GNS3 deployment using Python and Ansible.

## Network Statistics
- **Total Departments:** {len(self.departments)}
- **Total Network Devices:** {total_devices}
- **Department Devices:** {total_dept_devices}
- **Core Infrastructure:** {len(self.core_infrastructure)} devices
- **VLANs Configured:** {len(self.departments)}

## Network Architecture

### Departments and VLANs
This network implements a departmental VLAN structure with the following configuration:

"""
    
    # Add detailed department information using real values only
    for dept in self.departments:
        dept_name = dept['name']        # Real department name - no defaults
        vlan_id = dept['vlan']          # Real VLAN ID - no defaults  
        subnet = dept['subnet']         # Real subnet - no defaults
        gateway = dept['gateway']       # Real gateway - no defaults
        devices = dept['devices']       # Real device list
        
        # Count device types in this department
        switches = len([d for d in devices if d['type'] == 'switch'])
        routers = len([d for d in devices if d['type'] == 'router'])
        pcs = len([d for d in devices if d['type'] == 'pc'])
        servers = len([d for d in devices if d['type'] == 'server'])
        printers = len([d for d in devices if d['type'] == 'printer'])
        
        readme_content += f"""#### {dept_name} (VLAN {vlan_id})
- **Subnet:** {subnet}
- **Gateway:** {gateway}
- **Total Devices:** {len(devices)}
- **Device Breakdown:**
  - Switches: {switches}
  - Routers: {routers}
  - PCs: {pcs}
  - Servers: {servers}
  - Printers: {printers}

**Device Details:**
"""
        
        # List all devices with their exact IP addresses
        for device in devices:
            device_name = device['name']    # Real device name
            device_type = device['type']    # Real device type
            device_ip = device['ip']        # Real device IP
            readme_content += f"  - `{device_name}` ({device_type}): {device_ip}\n"
        
        readme_content += "\n"
    
    # Add core infrastructure information
    readme_content += f"""### Core Infrastructure
"""
    for device in self.core_infrastructure:
        device_name = device['name']
        device_type = device['type']
        device_ip = device['ip']
        readme_content += f"- `{device_name}` ({device_type}): {device_ip}\n"
    
    # Add project structure and usage information
    readme_content += f"""
## Generated Project Structure

### Configuration Files
- `ansible.cfg` - Ansible behavior configuration
- `inventories/hosts.yml` - Complete device inventory with exact IP addresses
- `group_vars/` - Device group variables (switches, routers, pcs, servers, printers)

### Playbooks
- `site.yml` - Complete network deployment (all devices)
- `playbooks/deploy_network.yml` - Network infrastructure only (switches/routers)
- `playbooks/configure_vlans.yml` - VLAN configuration only (switches)
- `playbooks/configure_end_devices.yml` - End devices only (PCs/servers/printers)

### Roles
- `roles/network-config/` - Unified role for all network configuration
  - `tasks/main.yml` - Network device configuration tasks
  - `tasks/end_devices.yml` - End device configuration tasks
  - `vars/main.yml` - Role variables with real VLAN data
  - `handlers/main.yml` - Network service restart handlers

## Usage Instructions

### Complete Network Deployment
Deploy the entire network infrastructure and all end devices:
```bash
ansible-playbook site.yml
"""
def run_generation(self):
    """
    Main execution method that orchestrates the complete network automation generation process
    Loads network data, creates directory structure, and generates all Ansible configuration files
    Uses simplified unified approach with comprehensive error handling and progress reporting
    """
    
    # Display project header and initialization information
    print("Network Automation Generator for University Project")
    print("Manual to Automated Network Deployment Transformation")
    print("=" * 60)
    print(f"Source Configuration: {self.network_data_file}")
    print(f"Output Directory: {self.output_dir}")
    print("=" * 60)
    
    # PHASE 1: LOAD AND VALIDATE NETWORK CONFIGURATION
    # This phase loads the network_data.yml file and validates its contents
    print("\nPHASE 1: Loading Network Configuration Data")
    print("-" * 45)
    
    if not self.load_network_data():
        print("ERROR: Failed to load network configuration data")
        print("Please check that network_data.yml exists and is properly formatted")
        return False
    
    print("Successfully loaded network configuration")
    print(f"Found {len(self.departments)} departments")
    print(f"Found {len(self.core_infrastructure)} core infrastructure devices")
    
    # Calculate total devices for validation
    total_devices = sum(len(dept['devices']) for dept in self.departments) + len(self.core_infrastructure)
    print(f"Total devices to configure: {total_devices}")
    
    # PHASE 2: CREATE ANSIBLE PROJECT STRUCTURE
    # This phase creates the simplified directory structure for Ansible files
    print("\nPHASE 2: Creating Ansible Project Structure")
    print("-" * 45)
    
    try:
        self.create_directory_structure()
        print("Created simplified Ansible directory structure")
        print("  - inventories/ for device inventory files")
        print("  - playbooks/ for deployment playbooks")
        print("  - group_vars/ for device group variables")
        print("  - roles/network-config/ for unified network configuration role")
    except Exception as e:
        print(f"ERROR: Failed to create directory structure: {e}")
        return False
    
    # PHASE 3: GENERATE CORE ANSIBLE CONFIGURATION
    # This phase creates the fundamental Ansible configuration files
    print("\nPHASE 3: Generating Core Ansible Configuration")
    print("-" * 45)
    
    try:
        # Generate main Ansible configuration file
        self.generate_ansible_cfg()
        print("Generated ansible.cfg with network automation settings")
        
        # Generate device inventory with real IP addresses
        self.generate_inventory()
        print("Generated inventory with exact IP addresses from network_data.yml")
        print("  - Uses simplified device grouping structure")
        print("  - All IP addresses taken directly from network configuration")
        
        # Generate group variables for device types
        self.generate_group_vars()
        print("Generated group variables for all device types")
        print("  - Created variables for switches, routers, pcs, servers, printers")
        
    except Exception as e:
        print(f"ERROR: Failed to generate core configuration: {e}")
        return False
    
    # PHASE 4: GENERATE UNIFIED NETWORK ROLE
    # This phase creates the simplified unified role for all network configuration
    print("\nPHASE 4: Generating Unified Network Configuration Role")
    print("-" * 45)
    
    try:
        # Generate unified network role (replaces separate switch/router/pc roles)
        self.generate_network_role()
        print("Generated unified network-config role")
        print("  - Handles switches, routers, and network infrastructure")
        print(f"  - Configured {len(self.departments)} department VLANs")
        
        # Generate end devices configuration (PCs, servers, printers)
        self.generate_end_devices_role()
        print("Generated end devices configuration")
        print("  - Handles PCs, servers, and printers via SSH")
        print("  - Includes package installation and network configuration")
        
    except Exception as e:
        print(f"ERROR: Failed to generate network role: {e}")
        return False
    
    # PHASE 5: GENERATE DEPLOYMENT PLAYBOOKS
    # This phase creates the playbooks for different deployment scenarios
    print("\nPHASE 5: Generating Deployment Playbooks")
    print("-" * 45)
    
    try:
        self.generate_playbooks()
        print("Generated complete set of deployment playbooks")
        print("  - site.yml for complete network deployment")
        print("  - deploy_network.yml for network infrastructure only")
        print("  - configure_vlans.yml for VLAN configuration only")
        print("  - configure_end_devices.yml for end devices only")
        
    except Exception as e:
        print(f"ERROR: Failed to generate playbooks: {e}")
        return False
    
    # PHASE 6: GENERATE PROJECT DOCUMENTATION
    # This phase creates comprehensive documentation for the university project
    print("\nPHASE 6: Generating Project Documentation")
    print("-" * 45)
    
    try:
        self.generate_network_documentation()
        print("Generated comprehensive project documentation")
        print("  - README.md with complete project overview and usage instructions")
        print("  - network_topology.json with detailed topology reference data")
        
    except Exception as e:
        print(f"ERROR: Failed to generate documentation: {e}")
        return False
    
    # GENERATION COMPLETE - DISPLAY COMPREHENSIVE SUMMARY
    print("\n" + "=" * 60)
    print("NETWORK AUTOMATION GENERATION COMPLETED SUCCESSFULLY")
    print("=" * 60)
    
    # Display network topology summary using real values
    print("\nNetwork Topology Summary:")
    print(f"Total Departments: {len(self.departments)}")
    print(f"Total Devices: {total_devices}")
    print(f"Core Infrastructure: {len(self.core_infrastructure)} devices")
    
    # Display department breakdown with real values (no defaults)
    print(f"\nDepartment Breakdown:")
    for dept in self.departments:
        dept_name = dept['name']        # Real department name - no default
        vlan_id = dept['vlan']          # Real VLAN ID - no default
        subnet = dept['subnet']         # Real subnet - no default
        device_count = len(dept['devices'])  # Real device count
        
        # Count device types in this department
        devices = dept['devices']
        switches = len([d for d in devices if d['type'] == 'switch'])
        routers = len([d for d in devices if d['type'] == 'router'])
        pcs = len([d for d in devices if d['type'] == 'pc'])
        servers = len([d for d in devices if d['type'] == 'server'])
        printers = len([d for d in devices if d['type'] == 'printer'])
        
        print(f"  VLAN {vlan_id}: {dept_name} ({subnet}) - {device_count} devices")
        if switches > 0 or routers > 0 or pcs > 0 or servers > 0 or printers > 0:
            print(f"    Switches: {switches}, Routers: {routers}, PCs: {pcs}, Servers: {servers}, Printers: {printers}")
    
    # Display generated files summary
    print(f"\nGenerated Files:")
    print(f"Output Directory: {self.output_dir}/")
    print("  - ansible.cfg (Ansible configuration)")
    print("  - inventories/hosts.yml (Device inventory with real IPs)")
    print("  - group_vars/ (Device group variables)")
    print("  - roles/network-config/ (Unified configuration role)")
    print("  - playbooks/ (Deployment playbooks)")
    print("  - site.yml (Complete deployment)")
    print("  - README.md (Project documentation)")
    print("  - network_topology.json (Topology reference)")
    
    # Display usage instructions
    print(f"\nDeployment Instructions:")
    print(f"1. Navigate to output directory: cd {self.output_dir}")
    print(f"2. Deploy complete network: ansible-playbook site.yml")
    print(f"3. Deploy network infrastructure only: ansible-playbook playbooks/deploy_network.yml")
    print(f"4. Deploy VLANs only: ansible-playbook playbooks/configure_vlans.yml")
    print(f"5. Deploy end devices only: ansible-playbook playbooks/configure_end_devices.yml")
    
    # Display project success metrics
    print(f"\nProject Generation Summary:")
    print(f"- Configuration Source: network_data.yml")
    print(f"- Structure: Simplified unified role approach")
    print(f"- IP Addresses: Real values from network configuration")
    print(f"- Documentation: Complete project overview")
    print(f"- Format: Ansible-compatible configuration")
    
    print("\n" + "=" * 60)
    print("Ready for university network automation demonstration")
    print("=" * 60)
    
    return True

def create_gns3_nodes(self):
    """
    Create GNS3 nodes using DIRECT API method only (no templates needed)
    FIXED: Import issues resolved with multiple fallback options
    """
    
    print("\nCREATING GNS3 NETWORK NODES (Direct API - No Templates)")
    print("=" * 60)
    print("Using built-in node types that work without templates")
    
    try:
        # STEP 1: IMPORT GNS3NetworkManager WITH FALLBACK OPTIONS
        print("Step 1: Importing GNS3NetworkManager...")
        
        # Try multiple import methods
        gns3_manager_imported = False
        
        try:
            # Option 1: Absolute import
            from automated.scripts.gns3.diagnostic import GNS3NetworkManager
            print(" Imported using absolute path")
            gns3_manager_imported = True
        except ImportError:
            try:
                # Option 2: Direct import (same folder)
                from diagnostic import GNS3NetworkManager
                print(" Imported from same folder")
                gns3_manager_imported = True
            except ImportError:
                try:
                    # Option 3: Add current directory to path
                    import sys
                    import os
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    if current_dir not in sys.path:
                        sys.path.append(current_dir)
                    from diagnostic import GNS3NetworkManager
                    print(" Imported after adding path")
                    gns3_manager_imported = True
                except ImportError:
                    pass
        
        if not gns3_manager_imported:
            print(" ERROR: Cannot import GNS3NetworkManager")
            print("Please check:")
            print("  1. diagnostic.py exists in the same folder")
            print("  2. diagnostic.py contains GNS3NetworkManager class")
            print("  3. No syntax errors in diagnostic.py")
            return False
        
        # STEP 2: CONNECT TO EXISTING PROJECT
        print("\nStep 2: Connecting to existing GNS3 project...")
        
        existing_project_id = "9a8ab49a-6f61-4fa8-9089-99e6c6594e4f"
        
        self.gns3_manager = GNS3NetworkManager(
            server_url=self.gns3_server_url,
            username="admin", 
            password="admin"
        )
        
        self.gns3_manager.current_project_id = existing_project_id
        self.gns3_project_id = existing_project_id
        
        print(f" Connected to project: {existing_project_id}")
        
        # STEP 3: VERIFY PROJECT ACCESS
        print("\nStep 3: Verifying project access...")
        
        project_details = self.gns3_manager.get_project_details(existing_project_id)
        if not project_details:
            print("ERROR: Cannot access project. Check if GNS3 is running.")
            return False
        
        print(f" Project: {project_details.get('name', 'Unknown')}")
        
        # Open project if needed
        if project_details.get('status') != 'opened':
            print("  Opening project...")
            if not self.gns3_manager.open_project(existing_project_id):
                print("ERROR: Failed to open project")
                return False
            print(" Project opened")
        
        # STEP 4: CHECK EXISTING NODES
        print("\nStep 4: Checking existing nodes...")
        
        existing_nodes = self.gns3_manager.list_project_nodes(existing_project_id)
        existing_node_names = {node.get('name') for node in existing_nodes}
        
        print(f" Found {len(existing_nodes)} existing nodes")
        if existing_nodes:
            print("  Existing nodes:")
            for node in existing_nodes[:5]:  # Show first 5
                print(f"    - {node.get('name')} ({node.get('node_type')})")
            if len(existing_nodes) > 5:
                print(f"    ... and {len(existing_nodes) - 5} more")
        
        # STEP 5: CREATE NODES USING DIRECT API
        print("\nStep 5: Creating nodes using direct API...")
        
        # Counters
        created_count = 0
        skipped_count = 0
        failed_count = 0
        
        # Layout settings
        x_start, y_start = 100, 100
        x_spacing, y_spacing = 150, 120
        
        # PHASE A: CREATE CORE INFRASTRUCTURE
        print("\n  Phase A: Creating core infrastructure...")
        
        for i, device in enumerate(self.core_infrastructure):
            device_name = device['name']
            device_type = device['type']
            device_ip = device['ip']
            
            if device_name in existing_node_names:
                print(f"     Skipping {device_name} - already exists")
                skipped_count += 1
                continue
            
            x_pos = x_start + (i * x_spacing)
            y_pos = y_start
            
            # Create node with direct API
            if self._create_node_direct_simple(device_name, device_type, x_pos, y_pos):
                created_count += 1
                print(f"     Created {device_name} ({device_type})")
            else:
                failed_count += 1
                print(f"     Failed to create {device_name}")
        
        # PHASE B: CREATE DEPARTMENT NODES
        print("\n  Phase B: Creating department nodes...")
        
        current_y = y_start + 200  # Start below core infrastructure
        
        for dept_index, dept in enumerate(self.departments):
            dept_name = dept['name']
            vlan_id = dept['vlan']
            devices = dept['devices']
            
            print(f"\n    Creating {dept_name} (VLAN {vlan_id}) devices...")
            
            # Calculate department layout
            dept_x_start = x_start + (dept_index % 3) * 500  # 3 departments per row
            dept_y = current_y + (dept_index // 3) * 300     # New row every 3 departments
            
            for device_index, device in enumerate(devices):
                device_name = device['name']
                device_type = device['type']
                device_ip = device['ip']
                
                if device_name in existing_node_names:
                    print(f"       Skipping {device_name} - already exists")
                    skipped_count += 1
                    continue
                
                # Position within department
                x_pos = dept_x_start + (device_index % 4) * 120
                y_pos = dept_y + (device_index // 4) * 100
                
                # Create node
                if self._create_node_direct_simple(device_name, device_type, x_pos, y_pos):
                    created_count += 1
                    print(f"       Created {device_name} ({device_type})")
                else:
                    failed_count += 1
                    print(f"       Failed to create {device_name}")
        
        # STEP 6: SUMMARY
        print("\n" + "=" * 60)
        print("NODE CREATION SUMMARY")
        print("=" * 60)
        
        total = created_count + skipped_count + failed_count
        print(f"Total nodes processed: {total}")
        print(f" Successfully created: {created_count}")
        print(f" Skipped (already exist): {skipped_count}")
        print(f" Failed to create: {failed_count}")
        
        # Update node tracking for links
        final_nodes = self.gns3_manager.list_project_nodes(existing_project_id)
        self.created_nodes = {node['name']: node for node in final_nodes}
        print(f"\n Ready for link creation with {len(self.created_nodes)} total nodes")
        
        # Success if we created any nodes or if some already existed
        success = (created_count > 0) or (skipped_count > 0)
        return success
        
    except Exception as e:
        print(f"ERROR: Unexpected error in create_gns3_nodes: {e}")
        import traceback
        print("Full error traceback:")
        traceback.print_exc()
        return False
    
def create_gns3_links(self):
    """
    Create network links between nodes based on discovered network topology
    Works with nodes already created by create_gns3_nodes()
    Uses direct GNS3 v3 API calls - everything in one function
    """
    
    print("\nCREATING GNS3 NETWORK LINKS")
    print("=" * 60)
    print("Analyzing created nodes and establishing connections")
    
    # STEP 1: VALIDATE PREREQUISITES
    print("\nStep 1: Validating prerequisites...")
    
    if not hasattr(self, 'gns3_manager') or self.gns3_manager is None:
        print("ERROR: GNS3 manager not initialized. Run create_gns3_nodes first.")
        return False
    
    if not hasattr(self, 'created_nodes') or not self.created_nodes:
        print("ERROR: No nodes available for linking. Run create_gns3_nodes first.")
        return False
    
    if not self.gns3_project_id:
        print("ERROR: No GNS3 project ID available.")
        return False
    
    print(f" GNS3 manager: Ready")
    print(f" Available nodes: {len(self.created_nodes)}")
    print(f" Project ID: {self.gns3_project_id}")
    
    # STEP 2: ANALYZE AVAILABLE NODES
    print("\nStep 2: Analyzing available nodes...")
    
    # Categorize nodes by type from created_nodes
    switches = {}
    routers = {}
    endpoints = {}  # PCs, servers, printers
    core_devices = {}
    
    for node_name, node_info in self.created_nodes.items():
        node_type = node_info.get('node_type', 'unknown')
        
        # Categorize based on name patterns since we have the actual nodes
        if 'SW-' in node_name or 'Switch' in node_name:
            switches[node_name] = node_info
        elif 'R-' in node_name or 'Router' in node_name:
            routers[node_name] = node_info
        elif 'Core' in node_name:
            core_devices[node_name] = node_info
        elif any(prefix in node_name for prefix in ['PC-', 'server-', 'printer-', 'Server-']):
            endpoints[node_name] = node_info
        else:
            # Fallback: try to categorize by node_type from GNS3
            if 'switch' in node_type.lower():
                switches[node_name] = node_info
            elif 'router' in node_type.lower() or 'dynamips' in node_type.lower():
                routers[node_name] = node_info
            else:
                endpoints[node_name] = node_info
    
    print(f"   Switches found: {len(switches)} - {list(switches.keys())}")
    print(f"   Routers found: {len(routers)} - {list(routers.keys())}")
    print(f"   Endpoints found: {len(endpoints)} - {list(endpoints.keys())}")
    print(f"   Core devices found: {len(core_devices)} - {list(core_devices.keys())}")
    
    # Initialize counters
    created_links = 0
    failed_links = 0
    
    # STEP 3: CREATE DEPARTMENT INTERNAL LINKS
    print("\nStep 3: Creating department internal connections...")
    
    for dept in self.departments:
        dept_name = dept['name']
        vlan_id = dept['vlan']
        devices = dept['devices']
        
        print(f"\n  Processing {dept_name} (VLAN {vlan_id})...")
        
        # Find department devices in created nodes
        dept_switches = []
        dept_routers = []
        dept_endpoints = []
        
        for device in devices:
            device_name = device['name']
            if device_name in self.created_nodes:
                if device['type'] == 'switch':
                    if 'Server' not in device_name:  # Main switches only
                        dept_switches.append(device_name)
                elif device['type'] == 'router':
                    dept_routers.append(device_name)
                elif device['type'] in ['pc', 'server', 'printer']:
                    dept_endpoints.append(device_name)
        
        print(f"    Department nodes: {len(dept_switches)} switches, {len(dept_routers)} routers, {len(dept_endpoints)} endpoints")
        
        # PHASE A: CONNECT ENDPOINTS TO DEPARTMENT SWITCH
        if dept_switches and dept_endpoints:
            main_switch = dept_switches[0]  # Use first switch as main
            print(f"    Connecting endpoints to main switch: {main_switch}")
            
            for port_num, endpoint in enumerate(dept_endpoints, start=1):
                # DIRECT LINK CREATION HERE (no helper function)
                try:
                    # Get node IDs
                    endpoint_id = self.created_nodes[endpoint].get('node_id')
                    switch_id = self.created_nodes[main_switch].get('node_id')
                    
                    if endpoint_id and switch_id:
                        # Build v3 API URL
                        api_url = f"{self.gns3_manager.server_url}/v3/projects/{self.gns3_project_id}/links"
                        
                        # Prepare link data
                        link_data = {
                            "nodes": [
                                {
                                    "node_id": endpoint_id,
                                    "adapter_number": 0,
                                    "port_number": 0
                                },
                                {
                                    "node_id": switch_id,
                                    "adapter_number": 0, 
                                    "port_number": port_num
                                }
                            ]
                        }
                        
                        # Create link using gns3_manager session (has auth)
                        response = self.gns3_manager.session.post(
                            api_url,
                            json=link_data,
                            timeout=10
                        )
                        
                        if response.status_code == 201:
                            created_links += 1
                            print(f"      Connected {endpoint} -> {main_switch} port {port_num}")
                        elif response.status_code == 409:
                            created_links += 1  # Count as success if already exists
                            print(f"      Link already exists: {endpoint} -> {main_switch}")
                        else:
                            failed_links += 1
                            print(f"      Failed: {endpoint} -> {main_switch} ({response.status_code})")
                    else:
                        failed_links += 1
                        print(f"      Failed: Node IDs not found for {endpoint} -> {main_switch}")
                        
                except Exception as e:
                    failed_links += 1
                    print(f"      Error connecting {endpoint} -> {main_switch}: {e}")
        
        # PHASE B: CONNECT DEPARTMENT SWITCH TO ROUTER
        if dept_switches and dept_routers:
            main_switch = dept_switches[0]
            dept_router = dept_routers[0]
            
            # DIRECT LINK CREATION HERE
            try:
                switch_id = self.created_nodes[main_switch].get('node_id')
                router_id = self.created_nodes[dept_router].get('node_id')
                
                if switch_id and router_id:
                    api_url = f"{self.gns3_manager.server_url}/v3/projects/{self.gns3_project_id}/links"
                    
                    link_data = {
                        "nodes": [
                            {
                                "node_id": switch_id,
                                "adapter_number": 0,
                                "port_number": 24  # Switch uplink port
                            },
                            {
                                "node_id": router_id,
                                "adapter_number": 0,
                                "port_number": 0   # Router LAN port
                            }
                        ]
                    }
                    
                    response = self.gns3_manager.session.post(api_url, json=link_data, timeout=10)
                    
                    if response.status_code in [201, 409]:
                        created_links += 1
                        print(f"    Connected {main_switch} port 24 -> {dept_router} port 0")
                    else:
                        failed_links += 1
                        print(f"    Failed: {main_switch} -> {dept_router} ({response.status_code})")
                else:
                    failed_links += 1
                    print(f"    Failed: Node IDs not found for {main_switch} -> {dept_router}")
                    
            except Exception as e:
                failed_links += 1
                print(f"    Error connecting {main_switch} -> {dept_router}: {e}")
    
    # STEP 4: CONNECT ROUTERS TO CORE SWITCH
    print("\nStep 4: Connecting routers to core network...")
    
    if core_devices:
        core_switch_name = list(core_devices.keys())[0]  # Use first core device
        print(f"  Using core switch: {core_switch_name}")
        
        core_port = 1  # Start with port 1 on core switch
        
        for dept in self.departments:
            # Find department router
            dept_routers = [device['name'] for device in dept['devices'] 
                           if device['type'] == 'router' and device['name'] in self.created_nodes]
            
            if dept_routers:
                dept_router = dept_routers[0]
                
                # DIRECT LINK CREATION HERE
                try:
                    router_id = self.created_nodes[dept_router].get('node_id')
                    core_id = self.created_nodes[core_switch_name].get('node_id')
                    
                    if router_id and core_id:
                        api_url = f"{self.gns3_manager.server_url}/v3/projects/{self.gns3_project_id}/links"
                        
                        link_data = {
                            "nodes": [
                                {
                                    "node_id": router_id,
                                    "adapter_number": 0,
                                    "port_number": 1  # Router WAN port
                                },
                                {
                                    "node_id": core_id,
                                    "adapter_number": 0,
                                    "port_number": core_port
                                }
                            ]
                        }
                        
                        response = self.gns3_manager.session.post(api_url, json=link_data, timeout=10)
                        
                        if response.status_code in [201, 409]:
                            created_links += 1
                            print(f"    Connected {dept_router} port 1 -> {core_switch_name} port {core_port}")
                            core_port += 1
                        else:
                            failed_links += 1
                            print(f"    Failed: {dept_router} -> {core_switch_name} ({response.status_code})")
                    else:
                        failed_links += 1
                        print(f"    Failed: Node IDs not found for {dept_router} -> {core_switch_name}")
                        
                except Exception as e:
                    failed_links += 1
                    print(f"    Error connecting {dept_router} -> {core_switch_name}: {e}")
    else:
        print("  No core devices found - skipping core connections")
    
    # STEP 5: SUMMARY
    print("\n" + "=" * 60)
    print("LINK CREATION SUMMARY")
    print("=" * 60)
    
    total_attempted = created_links + failed_links
    success_rate = (created_links / total_attempted * 100) if total_attempted > 0 else 0
    
    print(f"Total links attempted: {total_attempted}")
    print(f"Successfully created: {created_links}")
    print(f"Failed to create: {failed_links}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if created_links > 0:
        print(f"\nNetwork topology created successfully!")
        print(f"Ready for device configuration")
        return True
    else:
        print(f"\nNo links were created. Check node availability.")
        return False

def __init__(self, network_data_file: str = "automated/ansible_config/network_data.yml"):
    """
    Initialize the GNS3 Network Manager with server connection parameters.
    Sets up logging, loads configuration, and initializes component paths.
    """
    # Core configuration and path setup
    self.network_data_file = network_data_file
    self.output_dir = "automated/ansible_config"
    self.network_data = None
    self.departments = []
    self.core_infrastructure = []
    
    # Device type mappings for Ansible inventory organization
    self.device_type_mapping = {
        'switch': 'switches',
        'router': 'routers',
        'pc': 'pcs',           # PCs go to pcs group
        'lp': 'pcs',           # Laptops also go to pcs group  
        'server': 'servers',
        'printer': 'printers'
    }
    
    # GNS3 hardware specifications for different device types
    # This mapping defines which GNS3 templates to use for each device type
    self.gns3_hardware_mapping = {
        'switch': {
            'template_name': 'Cisco IOSv Switch',    # Cisco switch template
            'node_type': 'dynamips',                 # Dynamips emulator
            'properties': {'platform': 'c3745'},    # Cisco 3745 platform
            'description': 'Managed Layer 2/3 Switch'
        },
        'router': {
            'template_name': 'Cisco IOSv Router',    # Cisco router template
            'node_type': 'dynamips',                 # Dynamips emulator
            'properties': {'platform': 'c7200'},    # Cisco 7200 platform
            'description': 'Layer 3 Router with routing capabilities'
        },
        'pc': {
            'template_name': 'VPCS',                 # Virtual PC Simulator
            'node_type': 'vpcs',                     # VPCS node type
            'properties': {},                        # No special properties
            'description': 'Virtual PC for end-user simulation'
        },
        'lp': {  # Laptops (from Guest Network department)
            'template_name': 'VPCS',                 # Virtual PC Simulator
            'node_type': 'vpcs',                     # VPCS node type
            'properties': {},                        # No special properties
            'description': 'Virtual Laptop for guest network simulation'
        },
        'server': {
            'template_name': 'Ubuntu Server',        # Ubuntu server template
            'node_type': 'docker',                   # Docker container
            'properties': {'image': 'ubuntu:20.04'}, # Ubuntu 20.04 image
            'description': 'Ubuntu Server container for services'
        },
        'printer': {
            'template_name': 'VPCS',                 # Use VPCS for printer simulation
            'node_type': 'vpcs',                     # VPCS node type
            'properties': {},                        # No special properties
            'description': 'Virtual Printer simulation using VPCS'
        }
    }
    
    # GNS3 server connection settings
    self.gns3_server_url = "http://127.0.0.1:3080"  # Default GNS3 server URL
    self.gns3_project_id = None                      # Will be set when connecting to project
    
    # ADD THESE TWO MISSING ATTRIBUTES FOR GNS3 NODE CREATION:
    # =========================================================
    self.gns3_manager = None                         # GNS3NetworkManager instance (set when connecting)
    self.created_nodes = {}                          # Dictionary to track created nodes for linking
    
    # Load network configuration during initialization
    self.load_network_config()  # Make sure this method exists and sets departments + core_infrastructure

def test_gns3_connection(generator):
    """
    Test function to verify GNS3 connection without creating nodes
    """
    try:
        from automated.scripts.gns3.diagnostic import GNS3NetworkManager
        
        print("Testing GNS3 server connection...")
        
        # Test connection
        gns3_manager = GNS3NetworkManager(
            server_url=generator.gns3_server_url,
            username="admin", 
            password="admin"
        )
        
        # Test project access
        existing_project_id = "9a8ab49a-6f61-4fa8-9089-99e6c6594e4f"
        project_details = gns3_manager.get_project_details(existing_project_id)
        
        if project_details:
            print(f" GNS3 server connection: OK")
            print(f" Project access: OK")
            print(f"  Project name: {project_details.get('name', 'Unknown')}")
            print(f"  Project status: {project_details.get('status', 'Unknown')}")
            
            # Check existing nodes
            nodes = gns3_manager.list_project_nodes(existing_project_id)
            print(f" Existing nodes in project: {len(nodes)}")
            
            return True
        else:
            print("✗ Cannot access GNS3 project")
            return False
            
    except ImportError:
        print("✗ Cannot import GNS3NetworkManager from diagnostic.py")
        print("Make sure diagnostic.py is in automated/scripts/gns3/ folder")
        return False
    except Exception as e:
        print(f"✗ GNS3 connection test failed: {e}")
        return False
def main():
    """
    Main function for standalone script execution
    Enhanced to include GNS3 node creation options
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
    
    # ENHANCED MAIN MENU - Choose what to generate
    print("\nWhat would you like to generate?")
    print("1. Ansible Configuration Only (original)")
    print("2. GNS3 Nodes Only (new)")
    print("3. Both Ansible + GNS3 Nodes (complete)")
    print("4. Test GNS3 Connection")
    
    try:
        choice = input("\nEnter choice (1-4): ").strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        exit(0)
    
    success = False
    
    if choice == "1":
        # ORIGINAL ANSIBLE GENERATION
        print("\nGenerating Ansible configuration only...")
        success = generator.run_generation()
        
        if success:
            print("\n Ansible automation files generated successfully!")
            print("FIXED: All YAML files now use correct dictionary format")
            print("All IP addresses taken directly from network_data.yml")
            print("No template files created - all configurations embedded in tasks")
        else:
            print("\n✗ Ansible generation failed!")
    
    elif choice == "2":
        # NEW GNS3 NODE CREATION
        print("\nGenerating GNS3 nodes only...")
        success = generator.create_gns3_nodes()
        
        if success:
            print("\n GNS3 nodes created successfully!")
            print(f"Total nodes available: {len(generator.created_nodes)}")
            print("Ready for network link creation")
        else:
            print("\n✗ GNS3 node creation failed!")
    
    elif choice == "3":
        # BOTH ANSIBLE AND GNS3
        print("\nGenerating both Ansible configuration AND GNS3 nodes...")
        
        # First generate Ansible config
        print("\nStep 1: Generating Ansible configuration...")
        ansible_success = generator.run_generation()
        
        # Then create GNS3 nodes
        print("\nStep 2: Creating GNS3 nodes...")
        gns3_success = generator.create_gns3_nodes()
        
        success = ansible_success and gns3_success
        
        if success:
            print("\n Complete network automation generated successfully!")
            print(" Ansible playbooks ready for deployment")
            print(f" {len(generator.created_nodes)} GNS3 nodes created")
        else:
            print(f"\n Partial success:")
            print(f"  Ansible: {'Success' if ansible_success else 'Not Success'}")
            print(f"  GNS3: {'Success' if gns3_success else 'Not Success'}")
    
    elif choice == "4":
        # TEST GNS3 CONNECTION
        print("\nTesting GNS3 connection...")
        success = test_gns3_connection(generator)
    
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
        print("GENERATION FAILED!")
        print("=" * 60)
        exit(1)

if __name__ == "__main__":
    main()