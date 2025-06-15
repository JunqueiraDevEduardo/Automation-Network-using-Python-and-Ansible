#!/bin/bash
# PC Network Configuration Script
# Configures IP addresses and gateways for all department PCs

echo "🖥️ Configuring PC Network Settings..."


# Development_Engineering Department (VLAN 10)
echo "Configuring Development_Engineering PCs..."

# Configure PC-A-01
echo "  Setting up PC-A-01: 192.168.10.2"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.10.2/28 dev eth0
# sudo ip route add default via 192.168.10.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.10.2 255.255.255.240 192.168.10.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-A-02
echo "  Setting up PC-A-02: 192.168.10.3"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.10.3/28 dev eth0
# sudo ip route add default via 192.168.10.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.10.3 255.255.255.240 192.168.10.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-A-03
echo "  Setting up PC-A-03: 192.168.10.4"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.10.4/28 dev eth0
# sudo ip route add default via 192.168.10.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.10.4 255.255.255.240 192.168.10.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-A-04
echo "  Setting up PC-A-04: 192.168.10.5"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.10.5/28 dev eth0
# sudo ip route add default via 192.168.10.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.10.5 255.255.255.240 192.168.10.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-A-05
echo "  Setting up PC-A-05: 192.168.10.6"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.10.6/28 dev eth0
# sudo ip route add default via 192.168.10.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.10.6 255.255.255.240 192.168.10.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-A-06
echo "  Setting up PC-A-06: 192.168.10.7"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.10.7/28 dev eth0
# sudo ip route add default via 192.168.10.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.10.7 255.255.255.240 192.168.10.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# IT_Network Department (VLAN 30)
echo "Configuring IT_Network PCs..."

# Configure PC-B-01
echo "  Setting up PC-B-01: 192.168.30.2"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.30.2/28 dev eth0
# sudo ip route add default via 192.168.30.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.30.2 255.255.255.240 192.168.30.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-B-02
echo "  Setting up PC-B-02: 192.168.30.3"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.30.3/28 dev eth0
# sudo ip route add default via 192.168.30.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.30.3 255.255.255.240 192.168.30.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-B-03
echo "  Setting up PC-B-03: 192.168.30.4"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.30.4/28 dev eth0
# sudo ip route add default via 192.168.30.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.30.4 255.255.255.240 192.168.30.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-B-04
echo "  Setting up PC-B-04: 192.168.30.5"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.30.5/28 dev eth0
# sudo ip route add default via 192.168.30.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.30.5 255.255.255.240 192.168.30.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-B-05
echo "  Setting up PC-B-05: 192.168.30.6"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.30.6/28 dev eth0
# sudo ip route add default via 192.168.30.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.30.6 255.255.255.240 192.168.30.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-B-06
echo "  Setting up PC-B-06: 192.168.30.7"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.30.7/28 dev eth0
# sudo ip route add default via 192.168.30.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.30.7 255.255.255.240 192.168.30.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Sales_Marketing Department (VLAN 40)
echo "Configuring Sales_Marketing PCs..."

# Configure PC-C-01
echo "  Setting up PC-C-01: 192.168.40.2"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.40.2/28 dev eth0
# sudo ip route add default via 192.168.40.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.40.2 255.255.255.240 192.168.40.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-C-02
echo "  Setting up PC-C-02: 192.168.40.3"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.40.3/28 dev eth0
# sudo ip route add default via 192.168.40.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.40.3 255.255.255.240 192.168.40.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-C-03
echo "  Setting up PC-C-03: 192.168.40.4"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.40.4/28 dev eth0
# sudo ip route add default via 192.168.40.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.40.4 255.255.255.240 192.168.40.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Guest_Network Department (VLAN 20)
echo "Configuring Guest_Network PCs..."

# Configure PC-D-01
echo "  Setting up PC-D-01: 192.168.20.2"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.20.2/28 dev eth0
# sudo ip route add default via 192.168.20.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.20.2 255.255.255.240 192.168.20.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-D-02
echo "  Setting up PC-D-02: 192.168.20.3"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.20.3/28 dev eth0
# sudo ip route add default via 192.168.20.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.20.3 255.255.255.240 192.168.20.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-D-03
echo "  Setting up PC-D-03: 192.168.20.4"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.20.4/28 dev eth0
# sudo ip route add default via 192.168.20.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.20.4 255.255.255.240 192.168.20.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-D-04
echo "  Setting up PC-D-04: 192.168.20.5"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.20.5/28 dev eth0
# sudo ip route add default via 192.168.20.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.20.5 255.255.255.240 192.168.20.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-D-05
echo "  Setting up PC-D-05: 192.168.20.6"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.20.6/28 dev eth0
# sudo ip route add default via 192.168.20.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.20.6 255.255.255.240 192.168.20.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Accounts_Finance Department (VLAN 70)
echo "Configuring Accounts_Finance PCs..."

# Configure PC-E-01
echo "  Setting up PC-E-01: 192.168.70.2"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.70.2/28 dev eth0
# sudo ip route add default via 192.168.70.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.70.2 255.255.255.240 192.168.70.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-E-02
echo "  Setting up PC-E-02: 192.168.70.3"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.70.3/28 dev eth0
# sudo ip route add default via 192.168.70.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.70.3 255.255.255.240 192.168.70.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Human_Resources Department (VLAN 60)
echo "Configuring Human_Resources PCs..."

# Configure PC-F-01
echo "  Setting up PC-F-01: 192.168.60.2"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.60.2/29 dev eth0
# sudo ip route add default via 192.168.60.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.60.2 255.255.255.248 192.168.60.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-F-02
echo "  Setting up PC-F-02: 192.168.60.3"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.60.3/29 dev eth0
# sudo ip route add default via 192.168.60.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.60.3 255.255.255.248 192.168.60.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Infrastructure_Security Department (VLAN 0)
echo "Configuring Infrastructure_Security PCs..."

# Configure PC-G-01
echo "  Setting up PC-G-01: 192.168.0.2"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.0.2/28 dev eth0
# sudo ip route add default via 192.168.0.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.0.2 255.255.255.240 192.168.0.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-G-02
echo "  Setting up PC-G-02: 192.168.0.3"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.0.3/28 dev eth0
# sudo ip route add default via 192.168.0.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.0.3 255.255.255.240 192.168.0.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-G-03
echo "  Setting up PC-G-03: 192.168.0.4"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.0.4/28 dev eth0
# sudo ip route add default via 192.168.0.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.0.4 255.255.255.240 192.168.0.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-G-04
echo "  Setting up PC-G-04: 192.168.0.5"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.0.5/28 dev eth0
# sudo ip route add default via 192.168.0.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.0.5 255.255.255.240 192.168.0.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Admin_Department Department (VLAN 50)
echo "Configuring Admin_Department PCs..."

# Configure PC-H-01
echo "  Setting up PC-H-01: 192.168.50.2"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.50.2/29 dev eth0
# sudo ip route add default via 192.168.50.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.50.2 255.255.255.248 192.168.50.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-H-02
echo "  Setting up PC-H-02: 192.168.50.3"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.50.3/29 dev eth0
# sudo ip route add default via 192.168.50.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.50.3 255.255.255.248 192.168.50.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Marketing_Department Department (VLAN 90)
echo "Configuring Marketing_Department PCs..."

# Configure PC-I-01
echo "  Setting up PC-I-01: 192.168.90.2"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.90.2/28 dev eth0
# sudo ip route add default via 192.168.90.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.90.2 255.255.255.240 192.168.90.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-I-02
echo "  Setting up PC-I-02: 192.168.90.3"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.90.3/28 dev eth0
# sudo ip route add default via 192.168.90.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.90.3 255.255.255.240 192.168.90.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Design_Department Department (VLAN 80)
echo "Configuring Design_Department PCs..."

# Configure PC-J-01
echo "  Setting up PC-J-01: 192.168.80.2"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.80.2/29 dev eth0
# sudo ip route add default via 192.168.80.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.80.2 255.255.255.248 192.168.80.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

# Configure PC-J-02
echo "  Setting up PC-J-02: 192.168.80.3"
# For Ubuntu/Linux PCs:
# sudo ip addr add 192.168.80.3/29 dev eth0
# sudo ip route add default via 192.168.80.1
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For Windows PCs (run as administrator):
# netsh interface ip set address "Ethernet" static 192.168.80.3 255.255.255.248 192.168.80.1
# netsh interface ip set dns "Ethernet" static 8.8.8.8

echo "✅ PC configuration completed!"
echo "Note: Uncomment and modify the appropriate commands for your OS"
