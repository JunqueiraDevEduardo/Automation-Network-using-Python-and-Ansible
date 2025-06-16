#!/bin/bash
# PC Network Configuration Script
# Configures IP addresses and gateways for all department PCs and servers

echo "Configuring PC Network Settings..."


# Development/Engineering Department (VLAN 10)
echo "Configuring Development/Engineering devices..."

# Configure PC-2-10
echo "  Setting up PC-2-10: 192.168.10.3"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.10.3/24 dev eth0
# sudo ip route add default via 192.168.10.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.10.3 255.255.255.0 192.168.10.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-3-10
echo "  Setting up PC-3-10: 192.168.10.4"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.10.4/24 dev eth0
# sudo ip route add default via 192.168.10.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.10.4 255.255.255.0 192.168.10.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-4-10
echo "  Setting up PC-4-10: 192.168.10.5"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.10.5/24 dev eth0
# sudo ip route add default via 192.168.10.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.10.5 255.255.255.0 192.168.10.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-5-10
echo "  Setting up PC-5-10: 192.168.10.6"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.10.6/24 dev eth0
# sudo ip route add default via 192.168.10.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.10.6 255.255.255.0 192.168.10.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-6-10
echo "  Setting up PC-6-10: 192.168.10.7"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.10.7/24 dev eth0
# sudo ip route add default via 192.168.10.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.10.7 255.255.255.0 192.168.10.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure Server-1-10
echo "  Setting up Server-1-10: 192.168.10.8"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.10.8/24 dev eth0
# sudo ip route add default via 192.168.10.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.10.8 255.255.255.0 192.168.10.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Guest Network Department (VLAN 20)
echo "Configuring Guest Network devices..."

# Configure PC-2-20
echo "  Setting up PC-2-20: 192.168.20.3"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.20.3/24 dev eth0
# sudo ip route add default via 192.168.20.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.20.3 255.255.255.0 192.168.20.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-3-20
echo "  Setting up PC-3-20: 192.168.20.4"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.20.4/24 dev eth0
# sudo ip route add default via 192.168.20.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.20.4 255.255.255.0 192.168.20.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-4-20
echo "  Setting up PC-4-20: 192.168.20.5"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.20.5/24 dev eth0
# sudo ip route add default via 192.168.20.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.20.5 255.255.255.0 192.168.20.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-5-20
echo "  Setting up PC-5-20: 192.168.20.6"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.20.6/24 dev eth0
# sudo ip route add default via 192.168.20.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.20.6 255.255.255.0 192.168.20.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# IT Network Department (VLAN 30)
echo "Configuring IT Network devices..."

# Configure PC-2-30
echo "  Setting up PC-2-30: 192.168.30.3"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.30.3/24 dev eth0
# sudo ip route add default via 192.168.30.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.30.3 255.255.255.0 192.168.30.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-3-30
echo "  Setting up PC-3-30: 192.168.30.4"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.30.4/24 dev eth0
# sudo ip route add default via 192.168.30.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.30.4 255.255.255.0 192.168.30.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-4-30
echo "  Setting up PC-4-30: 192.168.30.5"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.30.5/24 dev eth0
# sudo ip route add default via 192.168.30.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.30.5 255.255.255.0 192.168.30.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-4-30
echo "  Setting up PC-4-30: 192.168.30.5"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.30.5/24 dev eth0
# sudo ip route add default via 192.168.30.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.30.5 255.255.255.0 192.168.30.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-5-30
echo "  Setting up PC-5-30: 192.168.30.6"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.30.6/24 dev eth0
# sudo ip route add default via 192.168.30.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.30.6 255.255.255.0 192.168.30.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-6-30
echo "  Setting up PC-6-30: 192.168.30.7"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.30.7/24 dev eth0
# sudo ip route add default via 192.168.30.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.30.7 255.255.255.0 192.168.30.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-6-30
echo "  Setting up PC-6-30: 192.168.30.7"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.30.7/24 dev eth0
# sudo ip route add default via 192.168.30.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.30.7 255.255.255.0 192.168.30.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure Server-1-30
echo "  Setting up Server-1-30: 192.168.30.8"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.30.8/24 dev eth0
# sudo ip route add default via 192.168.30.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.30.8 255.255.255.0 192.168.30.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Sales and Marketing Department (VLAN 40)
echo "Configuring Sales and Marketing devices..."

# Configure PC-2-40
echo "  Setting up PC-2-40: 192.168.40.3"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.40.3/24 dev eth0
# sudo ip route add default via 192.168.40.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.40.3 255.255.255.0 192.168.40.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-3-40
echo "  Setting up PC-3-40: 192.168.40.4"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.40.4/24 dev eth0
# sudo ip route add default via 192.168.40.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.40.4 255.255.255.0 192.168.40.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure printer-1-40
echo "  Setting up printer-1-40: 192.168.40.5"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.40.5/24 dev eth0
# sudo ip route add default via 192.168.40.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.40.5 255.255.255.0 192.168.40.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Admin Department Department (VLAN 50)
echo "Configuring Admin Department devices..."

# Configure PC-2-50
echo "  Setting up PC-2-50: 192.168.50.3"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.50.3/24 dev eth0
# sudo ip route add default via 192.168.50.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.50.3 255.255.255.0 192.168.50.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Human Resource Management Department (VLAN 60)
echo "Configuring Human Resource Management devices..."

# Configure PC-2-60
echo "  Setting up PC-2-60: 192.168.60.3"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.60.3/24 dev eth0
# sudo ip route add default via 192.168.60.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.60.3 255.255.255.0 192.168.60.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure printer-1-60
echo "  Setting up printer-1-60: 192.168.60.4"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.60.4/24 dev eth0
# sudo ip route add default via 192.168.60.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.60.4 255.255.255.0 192.168.60.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Accounts and Finance Department (VLAN 70)
echo "Configuring Accounts and Finance devices..."

# Configure PC-2-70
echo "  Setting up PC-2-70: 192.168.70.3"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.70.3/24 dev eth0
# sudo ip route add default via 192.168.70.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.70.3 255.255.255.0 192.168.70.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure server-1-70
echo "  Setting up server-1-70: 192.168.70.4"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.70.4/24 dev eth0
# sudo ip route add default via 192.168.70.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.70.4 255.255.255.0 192.168.70.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Design Department (VLAN 80)
echo "Configuring Design devices..."

# Configure PC-2-80
echo "  Setting up PC-2-80: 192.168.80.3"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.80.3/24 dev eth0
# sudo ip route add default via 192.168.80.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.80.3 255.255.255.0 192.168.80.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Marketing Department (VLAN 90)
echo "Configuring Marketing devices..."

# Configure PC-2-90
echo "  Setting up PC-2-90: 192.168.90.3"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.90.3/24 dev eth0
# sudo ip route add default via 192.168.90.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.90.3 255.255.255.0 192.168.90.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Infrastructure & Security Department (VLAN 100)
echo "Configuring Infrastructure & Security devices..."

# Configure PC-2-100
echo "  Setting up PC-2-100: 192.168.0.9"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.0.9/24 dev eth0
# sudo ip route add default via 192.168.0.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.0.9 255.255.255.0 192.168.0.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-3-100
echo "  Setting up PC-3-100: 192.168.0.10"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.0.10/24 dev eth0
# sudo ip route add default via 192.168.0.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.0.10 255.255.255.0 192.168.0.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-4-100
echo "  Setting up PC-4-100: 192.168.0.11"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.0.11/24 dev eth0
# sudo ip route add default via 192.168.0.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.0.11 255.255.255.0 192.168.0.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure Server-1-100
echo "  Setting up Server-1-100: 192.168.0.2"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.0.2/24 dev eth0
# sudo ip route add default via 192.168.0.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.0.2 255.255.255.0 192.168.0.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure Server-2-100
echo "  Setting up Server-2-100: 192.168.0.3"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.0.3/24 dev eth0
# sudo ip route add default via 192.168.0.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.0.3 255.255.255.0 192.168.0.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure Server-3-100
echo "  Setting up Server-3-100: 192.168.0.4"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.0.4/24 dev eth0
# sudo ip route add default via 192.168.0.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.0.4 255.255.255.0 192.168.0.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure Server-4-100
echo "  Setting up Server-4-100: 192.168.0.5"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.0.5/24 dev eth0
# sudo ip route add default via 192.168.0.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.0.5 255.255.255.0 192.168.0.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure Server-5-100
echo "  Setting up Server-5-100: 192.168.0.6"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.0.6/24 dev eth0
# sudo ip route add default via 192.168.0.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.0.6 255.255.255.0 192.168.0.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure Server-6-100
echo "  Setting up Server-6-100: 192.168.0.7"
# For Ubuntu/Linux systems:
# sudo ip addr add 192.168.0.7/24 dev eth0
# sudo ip route add default via 192.168.0.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows systems (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.0.7 255.255.255.0 192.168.0.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

echo "PC configuration completed!"
echo "Note: Uncomment and modify the appropriate commands for your operating system"
