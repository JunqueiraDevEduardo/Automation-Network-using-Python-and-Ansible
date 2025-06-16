# Network Automation Files

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

**Departments:** 10
**VLANs configured:** 10

### Department Summary:

- **Development/Engineering**
  - VLAN: 10
  - Subnet: 192.168.10.0/28
  - Devices: 8

- **Guest Network**
  - VLAN: 20
  - Subnet: 192.168.20.0/28
  - Devices: 6

- **IT Network**
  - VLAN: 30
  - Subnet: 192.168.30.0/28
  - Devices: 10

- **Sales and Marketing**
  - VLAN: 40
  - Subnet: 192.168.40.0/29
  - Devices: 5

- **Admin Department**
  - VLAN: 50
  - Subnet: 192.168.50.0/29
  - Devices: 3

- **Human Resource Management**
  - VLAN: 60
  - Subnet: 192.168.60.0/29
  - Devices: 4

- **Accounts and Finance**
  - VLAN: 70
  - Subnet: 192.168.70.0/29
  - Devices: 4

- **Design**
  - VLAN: 80
  - Subnet: 192.168.80.0/29
  - Devices: 3

- **Marketing**
  - VLAN: 90
  - Subnet: 192.168.90.0/29
  - Devices: 3

- **Infrastructure & Security**
  - VLAN: 100
  - Subnet: 192.168.0.0/23
  - Devices: 12

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

## File Generated From

This automation was generated from: `automated/config/network_data.yml`

## Next Steps

1. Review and customize the generated configurations
2. Update device credentials in the playbooks if needed
3. Test on a lab environment before production deployment
4. Document any manual changes made to the configurations

For more information, see the main project documentation.
