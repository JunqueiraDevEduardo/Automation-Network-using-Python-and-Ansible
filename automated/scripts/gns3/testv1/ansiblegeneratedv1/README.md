#Network Automation Project

## Project Overview
This project demonstrates automated network deployment using Python and Ansible.

## Network Statistics
- **Total Departments:** 10
- **Total Network Devices:** 66
- **Department Devices:** 65
- **Core Infrastructure:** 1 devices
- **VLANs Configured:** 10

## Network Architecture

### Departments and VLANs

#### Development/Engineering (VLAN 10)
- **Subnet:** 192.168.10.0/28
- **Gateway:** 192.168.10.1
- **Total Devices:** 9

**Device Details:**
  - `SW-10-A` (switch): 192.168.10.250
  - `PC-1-10` (pc): 192.168.10.2
  - `PC-2-10` (pc): 192.168.10.3
  - `PC-3-10` (pc): 192.168.10.4
  - `PC-4-10` (pc): 192.168.10.5
  - `PC-5-10` (pc): 192.168.10.6
  - `PC-6-10` (pc): 192.168.10.7
  - `R-10-A` (router): 192.168.10.1
  - `Server-1-10` (server): 192.168.10.8

#### Guest Network (VLAN 20)
- **Subnet:** 192.168.20.0/28
- **Gateway:** 192.168.20.1
- **Total Devices:** 7

**Device Details:**
  - `SW-20-D` (switch): 192.168.20.250
  - `LP-1-20` (pc): 192.168.20.2
  - `LP-2-20` (pc): 192.168.20.3
  - `LP-3-20` (pc): 192.168.20.4
  - `LP-4-20` (pc): 192.168.20.5
  - `LP-5-20` (pc): 192.168.20.6
  - `R-20-D` (router): 192.168.20.1

#### IT (VLAN 30)
- **Subnet:** 192.168.30.0/28
- **Gateway:** 192.168.30.1
- **Total Devices:** 9

**Device Details:**
  - `SW-30-B` (switch): 192.168.30.250
  - `PC-1-30` (pc): 192.168.30.2
  - `PC-2-30` (pc): 192.168.30.3
  - `PC-3-30` (pc): 192.168.30.4
  - `PC-4-30` (pc): 192.168.30.5
  - `PC-5-30` (pc): 192.168.30.6
  - `PC-6-30` (pc): 192.168.30.7
  - `R-30-B` (router): 192.168.30.1
  - `Server-1-30` (server): 192.168.30.8

#### Sales and Marketing (VLAN 40)
- **Subnet:** 192.168.40.0/29
- **Gateway:** 192.168.40.1
- **Total Devices:** 6

**Device Details:**
  - `SW-40-C` (switch): 192.168.40.250
  - `PC-1-40` (pc): 192.168.40.2
  - `PC-2-40` (pc): 192.168.40.3
  - `PC-3-40` (pc): 192.168.40.4
  - `printer-1-40` (printer): 192.168.40.5
  - `R-40-C` (router): 192.168.40.1

#### Admin Department (VLAN 50)
- **Subnet:** 192.168.50.0/29
- **Gateway:** 192.168.50.1
- **Total Devices:** 4

**Device Details:**
  - `SW-50-H` (switch): 192.168.50.250
  - `PC-1-50` (pc): 192.168.50.2
  - `PC-2-50` (pc): 192.168.50.3
  - `R-50-H` (router): 192.168.50.1

#### Human Resource Management (VLAN 60)
- **Subnet:** 192.168.60.0/29
- **Gateway:** 192.168.60.1
- **Total Devices:** 5

**Device Details:**
  - `SW-60-E` (switch): 192.168.60.250
  - `PC-1-60` (pc): 192.168.60.2
  - `PC-2-60` (pc): 192.168.60.3
  - `printer-1-60` (printer): 192.168.60.4
  - `R-60-E` (router): 192.168.60.1

#### Accounts and Finance (VLAN 70)
- **Subnet:** 192.168.70.0/29
- **Gateway:** 192.168.70.1
- **Total Devices:** 5

**Device Details:**
  - `SW-70-E` (switch): 192.168.70.250
  - `PC-1-70` (pc): 192.168.70.2
  - `PC-2-70` (pc): 192.168.70.3
  - `server-1-70` (server): 192.168.70.4
  - `R-70-E` (router): 192.168.70.1

#### Design (VLAN 80)
- **Subnet:** 192.168.80.0/29
- **Gateway:** 192.168.80.1
- **Total Devices:** 4

**Device Details:**
  - `SW-80-J` (switch): 192.168.80.250
  - `PC-1-80` (pc): 192.168.80.2
  - `PC-2-80` (pc): 192.168.80.3
  - `R-80-J` (router): 192.168.80.1

#### Marketing (VLAN 90)
- **Subnet:** 192.168.90.0/29
- **Gateway:** 192.168.90.1
- **Total Devices:** 4

**Device Details:**
  - `SW-90-I` (switch): 192.168.90.250
  - `PC-1-90` (pc): 192.168.90.2
  - `PC-2-90` (pc): 192.168.90.3
  - `R-90-I` (router): 192.168.90.1

#### Infrastructure & Security (VLAN 100)
- **Subnet:** 192.168.0.0/23
- **Gateway:** 192.168.0.1
- **Total Devices:** 12

**Device Details:**
  - `SW-100-G` (switch): 192.168.2.250
  - `PC-1-100` (pc): 192.168.0.8
  - `PC-2-100` (pc): 192.168.0.9
  - `PC-3-100` (pc): 192.168.0.10
  - `PC-4-100` (pc): 192.168.0.11
  - `R-100-G` (router): 192.168.0.1
  - `Server-1-100` (switch): 192.168.0.12
  - `Server-2-100` (switch): 192.168.0.13
  - `Server-3-100` (switch): 192.168.0.14
  - `Server-4-100` (switch): 192.168.0.15
  - `Server-5-100` (switch): 192.168.0.16
  - `Server-6-100` (switch): 192.168.0.17

### Core Infrastructure
- `CoreSwitch` (switch): 192.168.1.1

## Usage Instructions future!

### Complete Network Deployment
```bash
ansible-playbook api.yml
```

### Network Infrastructure Only
```bash
ansible-playbook playbooks/deploy_network.yml
```

## Generated Files
- `ansible.cfg` - Ansible configuration
- `inventories/hosts.yml` - Device inventory
- `departments/` - Device group departments
- `roles/network-config/` - Network configuration role
- `api.yml` - Complete deployment playbook
- `playbooks/deploy_network.yml` - Network infrastructure only
