# Network Automation Files

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

**Departments:** 0

### Department Summary:

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
