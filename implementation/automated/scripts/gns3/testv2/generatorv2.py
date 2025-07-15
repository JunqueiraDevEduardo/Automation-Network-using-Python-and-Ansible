"""
Project 2 Eduardo Junqueira IPVC-ESTG ERSC
Network Automation Generator V2
simplified network topology generator without limitations generate thr network_data_v2_new.yml
Features:
- Create, edit, delete departments and devices without restrictions
- 100% automatic operation with minimal user input
- No technical validations or limitations
- Simple and fast workflow
"""

import yaml #librarie to read files yml that need the python3 -m pip install pyyaml command
import os #provides functions for interacting with the operating system.
from pathlib import Path #call path() directly without having the prefix pathlib.


class SimpleNetworkGenerator:
    """
    Simplified network generator with complete freedom and automation
    No limitations, no complex validations, just pure functionality
    """
    
    def __init__(self):
        """Initialize the simple network generator"""
        self.network_data_v2 = {
            'departments': [],
            'core_infrastructure': []
        }
        
        self.device_types = {
            '1': 'switch',
            '2': 'router', 
            '3': 'pc',
            '4': 'server',
            '5': 'printer'
        }

    def get_input(self, prompt, default=None):
        """Simple input without validation"""
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default
        return input(f"{prompt}: ").strip()

    def get_number(self, prompt, default=None):
        """Get number input without restrictions"""
        try:
            value = self.get_input(prompt, default)
            return int(value)
        except:
            return int(default) if default else 0

    def print_header(self, text):
        """Print simple header"""
        print("\n" + "=" * 50)
        print(text)
        print("=" * 50)

    def auto_generate_ips(self, base_ip, device_count):
        """Automatically generate IP addresses without restrictions"""
        ips = []
        for i in range(1, device_count + 1):
            ips.append(f"{base_ip}.{i}")
        return ips

    def create_department_auto(self, dept_number):
        """Automatically create department with minimal input"""
        print(f"\n--- Creating Department {dept_number} ---")
        
        # Get basic info - completely free
        name = self.get_input("Department name", f"Dept_{dept_number}")
        vlan = self.get_number("VLAN ID", str(dept_number * 10))
        
        # Auto-generate subnet without restrictions
        subnet_base = f"192.168.{vlan}"
        subnet = f"{subnet_base}.0/24"
        gateway = f"{subnet_base}.1"
        
        print(f"Auto-assigned: VLAN {vlan}, Subnet {subnet}")
        
        # Auto-create devices with simple counts
        switch_count = self.get_number("Switches", "1")
        router_count = self.get_number("Routers", "1") 
        pc_count = self.get_number("PCs", "3")
        server_count = self.get_number("Servers", "1")
        printer_count = self.get_number("Printers", "1")
        
        devices = []
        ip_counter = 10  # Start IPs from .10
        
        # Create switches
        for i in range(switch_count):
            devices.append({
                'name': f"SW-{vlan}-{i+1}",
                'type': 'switch',
                'ip': f"{subnet_base}.{ip_counter}"
            })
            ip_counter += 1
            
        # Create routers
        for i in range(router_count):
            devices.append({
                'name': f"R-{vlan}-{i+1}",
                'type': 'router',
                'ip': f"{subnet_base}.{ip_counter}"
            })
            ip_counter += 1
            
        # Create PCs
        for i in range(pc_count):
            devices.append({
                'name': f"PC-{vlan}-{i+1}",
                'type': 'pc',
                'ip': f"{subnet_base}.{ip_counter}"
            })
            ip_counter += 1
            
        # Create servers
        for i in range(server_count):
            devices.append({
                'name': f"SRV-{vlan}-{i+1}",
                'type': 'server',
                'ip': f"{subnet_base}.{ip_counter}"
            })
            ip_counter += 1
            
        # Create printers
        for i in range(printer_count):
            devices.append({
                'name': f"PRT-{vlan}-{i+1}",
                'type': 'printer',
                'ip': f"{subnet_base}.{ip_counter}"
            })
            ip_counter += 1
        
        department = {
            'name': name,
            'vlan': vlan,
            'subnet': subnet,
            'gateway': gateway,
            'devices': devices
        }
        
        print(f"Department '{name}' created with {len(devices)} devices")
        return department

    def list_departments(self):
        """List all departments"""
        if not self.network_data_v2['departments']:
            print("No departments found")
            return False
            
        print("\nDepartments:")
        for i, dept in enumerate(self.network_data_v2['departments'], 1):
            print(f"{i}. {dept['name']} (VLAN {dept['vlan']}, {len(dept['devices'])} devices)")
        return True

    def edit_department(self):
        """Edit department - simple and direct"""
        if not self.list_departments():
            return
            
        try:
            choice = int(self.get_input("Select department number")) - 1
            dept = self.network_data_v2['departments'][choice]
        except:
            print("Invalid selection")
            return
            
        print(f"\nEditing: {dept['name']}")
        
        # Edit basic info
        dept['name'] = self.get_input("New name", dept['name'])
        dept['vlan'] = self.get_number("New VLAN", str(dept['vlan']))
        
        # Auto-update subnet based on VLAN
        subnet_base = f"192.168.{dept['vlan']}"
        dept['subnet'] = f"{subnet_base}.0/24"
        dept['gateway'] = f"{subnet_base}.1"
        
        # Update device IPs automatically
        for i, device in enumerate(dept['devices']):
            device['ip'] = f"{subnet_base}.{10 + i}"
            
        print("Department updated successfully")

    def delete_department(self):
        """Delete department - simple confirmation"""
        if not self.list_departments():
            return
            
        try:
            choice = int(self.get_input("Select department number to delete")) - 1
            dept = self.network_data_v2['departments'][choice]
            
            confirm = self.get_input(f"Delete '{dept['name']}'? (y/n)", "n")
            if confirm.lower() == 'y':
                removed = self.network_data_v2['departments'].pop(choice)
                print(f"Department '{removed['name']}' deleted")
            else:
                print("Deletion cancelled")
        except:
            print("Invalid selection")

    def create_auto_network(self):
        """Create complete network automatically"""
        self.print_header("AUTO NETWORK CREATION")
        
        # Get number of departments
        num_depts = self.get_number("How many departments", "3")
        
        # Auto-create departments
        for i in range(num_depts):
            dept = self.create_department_auto(i + 1)
            self.network_data_v2['departments'].append(dept)
            
        # Auto-create core infrastructure
        core_devices = [
            {'name': 'CoreSwitch', 'type': 'switch', 'ip': '192.168.1.1'},
            {'name': 'CoreRouter', 'type': 'router', 'ip': '192.168.1.2'}
        ]
        self.network_data_v2['core_infrastructure'] = core_devices
        
        print(f"\nNetwork created: {num_depts} departments + core infrastructure")

    def show_network(self):
        """Display network summary"""
        self.print_header("NETWORK SUMMARY")
        
        if not self.network_data_v2['departments']:
            print("No network data")
            return
            
        for dept in self.network_data_v2['departments']:
            print(f"\n{dept['name']} (VLAN {dept['vlan']})")
            print(f"  Subnet: {dept['subnet']}")
            print(f"  Gateway: {dept['gateway']}")
            print(f"  Devices: {len(dept['devices'])}")
            
            for device in dept['devices']:
                print(f"    {device['name']} ({device['type']}) - {device['ip']}")
                
        if self.network_data_v2['core_infrastructure']:
            print(f"\nCore Infrastructure:")
            for device in self.network_data_v2['core_infrastructure']:
                print(f"  {device['name']} ({device['type']}) - {device['ip']}")

    def save_network(self):
        """Save network to file"""
        filename = self.get_input("Filename", "network_data_v2.yml")
        
        try:
            with open(filename, 'w') as f:
                yaml.dump(self.network_data_v2, f, default_flow_style=False, indent=2)
            print(f"Network saved to {filename}")
        except Exception as e:
            print(f"Save error: {e}")

    def load_network(self):
        """Load network from file"""
        filename = self.get_input("Filename to load", "network_data_v2.yml")
        
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    self.network_data_v2 = yaml.safe_load(f)
                print(f"Network loaded from {filename}")
            else:
                print("File not found")
        except Exception as e:
            print(f"Load error: {e}")

    def quick_template(self):
        """Ultra-fast template creation"""
        self.print_header("QUICK TEMPLATE")
        
        # Auto-create 3 departments with standard setup
        templates = [
            {'name': 'Sales', 'vlan': 10, 'devices': {'switch': 1, 'router': 1, 'pc': 5, 'server': 1, 'printer': 1}},
            {'name': 'IT', 'vlan': 20, 'devices': {'switch': 2, 'router': 1, 'pc': 3, 'server': 2, 'printer': 1}},
            {'name': 'Finance', 'vlan': 30, 'devices': {'switch': 1, 'router': 1, 'pc': 4, 'server': 1, 'printer': 2}}
        ]
        
        self.network_data_v2['departments'] = []
        
        for template in templates:
            devices = []
            ip_counter = 10
            subnet_base = f"192.168.{template['vlan']}"
            
            for device_type, count in template['devices'].items():
                for i in range(count):
                    devices.append({
                        'name': f"{device_type.upper()}-{template['vlan']}-{i+1}",
                        'type': device_type,
                        'ip': f"{subnet_base}.{ip_counter}"
                    })
                    ip_counter += 1
            
            dept = {
                'name': template['name'],
                'vlan': template['vlan'],
                'subnet': f"{subnet_base}.0/24",
                'gateway': f"{subnet_base}.1",
                'devices': devices
            }
            self.network_data_v2['departments'].append(dept)
        
        # Add core
        self.network_data_v2['core_infrastructure'] = [
            {'name': 'CoreSwitch', 'type': 'switch', 'ip': '192.168.1.1'},
            {'name': 'CoreRouter', 'type': 'router', 'ip': '192.168.1.2'}
        ]
        
        print("Quick template created: 3 departments ready!")

    def run_ansible(self):
        """Run Ansible generator if available"""
        generators = ['generatorv3.py', 'generatorv2.py', 'generator.py']
        
        for gen in generators:
            if os.path.exists(gen):
                print(f"Running {gen}...")
                os.system(f"python3 {gen}")
                return
                
        print("No Ansible generator found")

    def main_menu(self):
        """Simple main menu"""
        self.print_header("SIMPLE NETWORK GENERATOR V2")
        print("100% Automatic - No Limitations")
        
        while True:
            print("\n1. Create Auto Network")
            print("2. Quick Template")
            print("3. Edit Department") 
            print("4. Delete Department")
            print("5. Show Network")
            print("6. Save Network")
            print("7. Load Network")
            print("8. Run Ansible")
            print("9. Exit")
            
            choice = self.get_input("Option")
            
            if choice == '1':
                self.create_auto_network()
            elif choice == '2':
                self.quick_template()
            elif choice == '3':
                self.edit_department()
            elif choice == '4':
                self.delete_department()
            elif choice == '5':
                self.show_network()
            elif choice == '6':
                self.save_network()
            elif choice == '7':
                self.load_network()
            elif choice == '8':
                self.run_ansible()
            elif choice == '9':
                print("Goodbye!")
                break
            else:
                print("Invalid option")

def main():
    """Main function"""
    try:
        generator = SimpleNetworkGenerator()
        generator.main_menu()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()