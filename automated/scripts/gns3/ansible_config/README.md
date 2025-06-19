# Network Automation Configuration

Generated from network_data.yml with exact IP addresses

## Network Overview

**Departments:** 10
**Core Infrastructure:** 1 devices

### Department Summary with IP Addresses:

- **Development/Engineering** (VLAN 10)
  - Subnet: 192.168.10.0/28
  - Gateway: 192.168.10.1
  - Devices: 8
    - SW-10-DEV (switch): 192.168.10.2
    - PC-2-10 (pc): 192.168.10.3
    - PC-3-10 (pc): 192.168.10.4
    - PC-4-10 (pc): 192.168.10.5
    - PC-5-10 (pc): 192.168.10.6
    - PC-6-10 (pc): 192.168.10.7
    - R-10-A (router): 192.168.10.1
    - Server-1-10 (switch): 192.168.10.8

- **Guest Network** (VLAN 20)
  - Subnet: 192.168.20.0/28
  - Gateway: 192.168.20.1
  - Devices: 6
    - SW-20-GUEST (switch): 192.168.20.2
    - PC-2-20 (pc): 192.168.20.3
    - PC-3-20 (pc): 192.168.20.4
    - PC-4-20 (pc): 192.168.20.5
    - PC-5-20 (pc): 192.168.20.6
    - R-20-D (router): 192.168.20.1

- **IT Network** (VLAN 30)
  - Subnet: 192.168.30.0/28
  - Gateway: 192.168.30.1
  - Devices: 8
    - SW-30-IT (switch): 192.168.30.2
    - PC-2-30 (pc): 192.168.30.3
    - PC-3-30 (pc): 192.168.30.4
    - PC-4-30 (pc): 192.168.30.5
    - PC-5-30 (pc): 192.168.30.6
    - PC-6-30 (pc): 192.168.30.7
    - R-30-B (router): 192.168.30.1
    - Server-1-30 (switch): 192.168.30.8

- **Sales and Marketing** (VLAN 40)
  - Subnet: 192.168.40.0/29
  - Gateway: 192.168.40.1
  - Devices: 5
    - SW-40-SALES (switch): 192.168.40.2
    - PC-2-40 (pc): 192.168.40.3
    - PC-3-40 (pc): 192.168.40.4
    - printer-1-40 (pc): 192.168.40.5
    - R-40-C (router): 192.168.40.1

- **Admin Department** (VLAN 50)
  - Subnet: 192.168.50.0/29
  - Gateway: 192.168.50.1
  - Devices: 3
    - SW-50-ADMIN (switch): 192.168.50.2
    - PC-2-50 (pc): 192.168.50.3
    - R-50-H (router): 192.168.50.1

- **Human Resource Management** (VLAN 60)
  - Subnet: 192.168.60.0/29
  - Gateway: 192.168.60.1
  - Devices: 4
    - SW-60-HR (switch): 192.168.60.2
    - PC-2-60 (pc): 192.168.60.3
    - printer-1-60 (pc): 192.168.60.4
    - R-60-E (router): 192.168.60.1

- **Accounts and Finance** (VLAN 70)
  - Subnet: 192.168.70.0/29
  - Gateway: 192.168.70.1
  - Devices: 4
    - SW-70-FINANCE (switch): 192.168.70.2
    - PC-2-70 (pc): 192.168.70.3
    - server-1-70 (pc): 192.168.70.4
    - R-70-E (router): 192.168.70.1

- **Design** (VLAN 80)
  - Subnet: 192.168.80.0/29
  - Gateway: 192.168.80.1
  - Devices: 3
    - SW-80-DESIGN (switch): 192.168.80.2
    - PC-2-80 (pc): 192.168.80.3
    - R-80-J (router): 192.168.80.1

- **Marketing** (VLAN 90)
  - Subnet: 192.168.90.0/29
  - Gateway: 192.168.90.1
  - Devices: 3
    - SW-90-MARKETING (switch): 192.168.90.2
    - PC-2-90 (pc): 192.168.90.3
    - R-90-I (router): 192.168.90.1

- **Infrastructure & Security** (VLAN 100)
  - Subnet: 192.168.0.0/23
  - Gateway: 192.168.0.1
  - Devices: 11
    - SW-100-INFRA (switch): 192.168.0.8
    - PC-2-100 (pc): 192.168.0.9
    - PC-3-100 (pc): 192.168.0.10
    - PC-4-100 (pc): 192.168.0.11
    - R-100-G (router): 192.168.0.1
    - Server-1-100 (switch): 192.168.0.2
    - Server-2-100 (switch): 192.168.0.3
    - Server-3-100 (switch): 192.168.0.4
    - Server-4-100 (switch): 192.168.0.5
    - Server-5-100 (switch): 192.168.0.6
    - Server-6-100 (switch): 192.168.0.7

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
