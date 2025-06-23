"""
Interactive Network Data Generator V2
Eduardo Junqueira IPVC-ESTG ERSC

This script allows users to interactively create network_data.yml
Users can customize:
- Number of departments
- Department names and VLANs
- Device types and quantities
- IP addressing schemes
- Network topology

After generation, it can automatically run the Ansible generator
"""

import yaml
import ipaddress
import os
import re
from pathlib import Path

class InteractiveNetworkGenerator:
    """
    Interactive generator that creates network_data.yml based on user input
    Provides a user-friendly interface for designing network topologies
    """
    
    def __init__(self):
        """Initialize the interactive network generator"""
        self.network_data = {
            'departments': [],
            'core_infrastructure': []
        }
        self.used_vlans = set()
        self.used_subnets = set()
        
        # Common device types
        self.device_types = {
            '1': 'switch',
            '2': 'router', 
            '3': 'pc',
            '4': 'server',
            '5': 'printer'
        }
        
        # Color codes for output
        self.colors = {
            'header': '\033[95m',
            'blue': '\033[94m',
            'cyan': '\033[96m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'end': '\033[0m',
            'bold': '\033[1m'
        }

    def print_colored(self, text, color='end'):
        """Print colored text for better user experience"""
        print(f"{self.colors.get(color, '')}{text}{self.colors['end']}")

    def print_header(self, text):
        """Print a formatted header"""
        self.print_colored("=" * 60, 'cyan')
        self.print_colored(text.center(60), 'header')
        self.print_colored("=" * 60, 'cyan')

    def print_section(self, text):
        """Print a formatted section header"""
        self.print_colored(f"\n{text}", 'blue')
        self.print_colored("-" * len(text), 'blue')

    def get_user_input(self, prompt, input_type='str', validation=None, default=None):
        """
        Get validated user input with proper error handling
        """
        while True:
            try:
                if default:
                    user_input = input(f"{prompt} [{default}]: ").strip()
                    if not user_input:
                        user_input = default
                else:
                    user_input = input(f"{prompt}: ").strip()
                
                if not user_input:
                    self.print_colored("Input cannot be empty. Please try again.", 'red')
                    continue
                
                # Type conversion
                if input_type == 'int':
                    user_input = int(user_input)
                elif input_type == 'float':
                    user_input = float(user_input)
                
                # Validation
                if validation and not validation(user_input):
                    self.print_colored("Invalid input. Please try again.", 'red')
                    continue
                
                return user_input
                
            except ValueError:
                self.print_colored(f"Please enter a valid {input_type}.", 'red')
            except KeyboardInterrupt:
                self.print_colored("\nOperation cancelled by user.", 'yellow')
                exit(0)

    def validate_vlan_id(self, vlan_id):
        """Validate VLAN ID"""
        if vlan_id < 1 or vlan_id > 4094:
            self.print_colored("VLAN ID must be between 1 and 4094.", 'red')
            return False
        if vlan_id in self.used_vlans:
            self.print_colored(f"VLAN {vlan_id} is already used. Please choose another.", 'red')
            return False
        return True

    def validate_subnet(self, subnet_str):
        """Validate subnet format and uniqueness"""
        try:
            subnet = ipaddress.IPv4Network(subnet_str, strict=False)
            if str(subnet) in self.used_subnets:
                self.print_colored(f"Subnet {subnet} is already used. Please choose another.", 'red')
                return False
            return True
        except ipaddress.AddressValueError:
            self.print_colored("Invalid subnet format. Use format like 192.168.10.0/24", 'red')
            return False

    def generate_ip_addresses(self, subnet_str, device_names, device_types):
        """
        Generate IP addresses for devices in a subnet
        Uses intelligent IP assignment based on device types
        """
        subnet = ipaddress.IPv4Network(subnet_str, strict=False)
        gateway_ip = str(subnet.network_address + 1)
        
        ip_assignments = {}
        ip_counter = 1
        
        # Assign IPs based on device type priority
        # Gateways: .1, Switches: .250+, Routers: gateway, PCs: .10+, Servers: .100+, Printers: .200+
        
        for i, (device_name, device_type) in enumerate(zip(device_names, device_types)):
            if device_type == 'router':
                # Routers typically get the gateway IP
                ip_assignments[device_name] = gateway_ip
            elif device_type == 'switch':
                # Switches get high IPs (.250, .251, etc.)
                ip_assignments[device_name] = str(subnet.network_address + 250 + i)
            elif device_type == 'server':
                # Servers get .100+ range
                ip_assignments[device_name] = str(subnet.network_address + 100 + i)
            elif device_type == 'printer':
                # Printers get .200+ range  
                ip_assignments[device_name] = str(subnet.network_address + 200 + i)
            else:  # PCs and other devices
                # PCs get .10+ range
                ip_assignments[device_name] = str(subnet.network_address + 10 + i)
        
        return ip_assignments, gateway_ip

    def display_device_types(self):
        """Display available device types"""
        self.print_colored("\nAvailable Device Types:", 'cyan')
        for key, device_type in self.device_types.items():
            self.print_colored(f"  {key}. {device_type.capitalize()}", 'yellow')

    def create_department(self, dept_number):
        """Create a single department interactively"""
        self.print_section(f"Department {dept_number} Configuration")
        
        # Department name
        dept_name = self.get_user_input(
            "Enter department name (e.g., Development, Sales, IT)",
            validation=lambda x: len(x) >= 2
        )
        
        # VLAN ID
        vlan_id = self.get_user_input(
            f"Enter VLAN ID for {dept_name} (1-4094)",
            input_type='int',
            validation=self.validate_vlan_id
        )
        self.used_vlans.add(vlan_id)
        
        # Subnet
        default_subnet = f"192.168.{vlan_id}.0/24"
        subnet = self.get_user_input(
            f"Enter subnet for {dept_name}",
            validation=self.validate_subnet,
            default=default_subnet
        )
        self.used_subnets.add(subnet)
        
        # Calculate gateway
        subnet_obj = ipaddress.IPv4Network(subnet, strict=False)
        gateway = str(subnet_obj.network_address + 1)
        
        # Device configuration
        self.print_colored(f"\nConfiguring devices for {dept_name}:", 'green')
        devices = []
        device_names = []
        device_types = []
        
        # Ask for each device type
        for device_type in ['switch', 'router', 'pc', 'server', 'printer']:
            count = self.get_user_input(
                f"How many {device_type}s in {dept_name}",
                input_type='int',
                validation=lambda x: x >= 0,
                default='0' if device_type in ['server', 'printer'] else '1'
            )
            
            # Create devices of this type
            for i in range(count):
                if device_type == 'switch':
                    device_name = f"SW-{vlan_id}-{chr(65 + i)}"  # SW-10-A, SW-10-B, etc.
                elif device_type == 'router':
                    device_name = f"R-{vlan_id}-{chr(65 + i)}"   # R-10-A, R-10-B, etc.
                elif device_type == 'pc':
                    device_name = f"PC-{i+1}-{vlan_id}"         # PC-1-10, PC-2-10, etc.
                elif device_type == 'server':
                    device_name = f"server-{i+1}-{vlan_id}"     # server-1-10, etc.
                elif device_type == 'printer':
                    device_name = f"printer-{i+1}-{vlan_id}"   # printer-1-10, etc.
                
                device_names.append(device_name)
                device_types.append(device_type)
        
        # Generate IP addresses
        if device_names:
            ip_assignments, gateway_ip = self.generate_ip_addresses(subnet, device_names, device_types)
            
            # Create device entries
            for device_name, device_type in zip(device_names, device_types):
                devices.append({
                    'name': device_name,
                    'type': device_type,
                    'ip': ip_assignments[device_name]
                })
            
            # Update gateway if router exists
            for device in devices:
                if device['type'] == 'router':
                    gateway = device['ip']
                    break
        
        # Create department entry
        department = {
            'name': dept_name,
            'vlan': vlan_id,
            'subnet': subnet,
            'gateway': gateway,
            'devices': devices
        }
        
        # Display summary
        self.print_colored(f"\n✓ Department {dept_name} created:", 'green')
        self.print_colored(f"  VLAN: {vlan_id}", 'yellow')
        self.print_colored(f"  Subnet: {subnet}", 'yellow')
        self.print_colored(f"  Gateway: {gateway}", 'yellow')
        self.print_colored(f"  Devices: {len(devices)}", 'yellow')
        
        return department

    def create_core_infrastructure(self):
        """Create core infrastructure interactively"""
        self.print_section("Core Infrastructure Configuration")
        
        create_core = self.get_user_input(
            "Create core infrastructure? (y/n)",
            default='y'
        ).lower() == 'y'
        
        if not create_core:
            return []
        
        core_devices = []
        
        # Core switch
        core_switch_name = self.get_user_input(
            "Enter core switch name",
            default="CoreSwitch"
        )
        
        core_switch_ip = self.get_user_input(
            "Enter core switch IP address",
            default="192.168.1.1"
        )
        
        core_devices.append({
            'name': core_switch_name,
            'type': 'switch',
            'ip': core_switch_ip
        })
        
        # Additional core devices
        while True:
            add_more = self.get_user_input(
                "Add another core device? (y/n)",
                default='n'
            ).lower() == 'y'
            
            if not add_more:
                break
            
            self.display_device_types()
            device_type_choice = self.get_user_input(
                "Select device type (1-5)",
                validation=lambda x: x in self.device_types.keys()
            )
            
            device_type = self.device_types[device_type_choice]
            device_name = self.get_user_input(f"Enter {device_type} name")
            device_ip = self.get_user_input(f"Enter {device_type} IP address")
            
            core_devices.append({
                'name': device_name,
                'type': device_type,
                'ip': device_ip
            })
        
        self.print_colored(f"\n✓ Created {len(core_devices)} core infrastructure devices", 'green')
        return core_devices

    def display_network_summary(self):
        """Display a summary of the created network"""
        self.print_header("NETWORK TOPOLOGY SUMMARY")
        
        total_devices = sum(len(dept['devices']) for dept in self.network_data['departments'])
        total_devices += len(self.network_data['core_infrastructure'])
        
        self.print_colored(f"Total Departments: {len(self.network_data['departments'])}", 'cyan')
        self.print_colored(f"Total Devices: {total_devices}", 'cyan')
        self.print_colored(f"Core Infrastructure: {len(self.network_data['core_infrastructure'])}", 'cyan')
        
        # Department details
        for dept in self.network_data['departments']:
            self.print_colored(f"\n{dept['name']} (VLAN {dept['vlan']}):", 'green')
            self.print_colored(f"  Subnet: {dept['subnet']}", 'yellow')
            self.print_colored(f"  Gateway: {dept['gateway']}", 'yellow')
            self.print_colored(f"  Devices: {len(dept['devices'])}", 'yellow')
            
            # Device breakdown
            device_counts = {}
            for device in dept['devices']:
                device_type = device['type']
                device_counts[device_type] = device_counts.get(device_type, 0) + 1
            
            for device_type, count in device_counts.items():
                self.print_colored(f"    {device_type.capitalize()}s: {count}", 'cyan')

    def save_network_data(self, filename='network_data.yml'):
        """Save the network data to YAML file"""
        try:
            with open(filename, 'w') as f:
                yaml.dump(self.network_data, f, default_flow_style=False, indent=2, sort_keys=False)
            
            self.print_colored(f"\n✓ Network data saved to {filename}", 'green')
            return True
        except Exception as e:
            self.print_colored(f"✗ Error saving network data: {e}", 'red')
            return False

    def load_template_network(self):
        """Create a template network for quick start"""
        self.print_colored("Creating template network with 3 departments...", 'yellow')
        
        # Template departments
        template_departments = [
            {
                'name': 'Development',
                'vlan': 10,
                'base_ip': '192.168.10.0/24',
                'devices': {'switch': 1, 'router': 1, 'pc': 3, 'server': 1, 'printer': 1}
            },
            {
                'name': 'Sales', 
                'vlan': 20,
                'base_ip': '192.168.20.0/24',
                'devices': {'switch': 1, 'router': 1, 'pc': 5, 'server': 0, 'printer': 1}
            },
            {
                'name': 'IT',
                'vlan': 30,
                'base_ip': '192.168.30.0/24', 
                'devices': {'switch': 1, 'router': 1, 'pc': 2, 'server': 2, 'printer': 1}
            }
        ]
        
        for template in template_departments:
            devices = []
            device_names = []
            device_types = []
            
            # Create devices based on template
            for device_type, count in template['devices'].items():
                for i in range(count):
                    if device_type == 'switch':
                        device_name = f"SW-{template['vlan']}-{chr(65 + i)}"
                    elif device_type == 'router':
                        device_name = f"R-{template['vlan']}-{chr(65 + i)}"
                    elif device_type == 'pc':
                        device_name = f"PC-{i+1}-{template['vlan']}"
                    elif device_type == 'server':
                        device_name = f"server-{i+1}-{template['vlan']}"
                    elif device_type == 'printer':
                        device_name = f"printer-{i+1}-{template['vlan']}"
                    
                    device_names.append(device_name)
                    device_types.append(device_type)
            
            # Generate IPs
            ip_assignments, gateway_ip = self.generate_ip_addresses(
                template['base_ip'], device_names, device_types
            )
            
            # Create device entries
            for device_name, device_type in zip(device_names, device_types):
                devices.append({
                    'name': device_name,
                    'type': device_type,
                    'ip': ip_assignments[device_name]
                })
            
            # Update gateway for router
            gateway = gateway_ip
            for device in devices:
                if device['type'] == 'router':
                    gateway = device['ip']
                    break
            
            # Add department
            self.network_data['departments'].append({
                'name': template['name'],
                'vlan': template['vlan'],
                'subnet': template['base_ip'],
                'gateway': gateway,
                'devices': devices
            })
            
            self.used_vlans.add(template['vlan'])
            self.used_subnets.add(template['base_ip'])
        
        # Add core infrastructure
        self.network_data['core_infrastructure'] = [{
            'name': 'CoreSwitch',
            'type': 'switch', 
            'ip': '192.168.1.1'
        }]
        
        self.print_colored("✓ Template network created successfully!", 'green')

    def run_ansible_generator(self):
        """Run the existing Ansible generator after creating network_data.yml"""
        self.print_section("Ansible Configuration Generation")
        
        run_ansible = self.get_user_input(
            "Generate Ansible configuration now? (y/n)",
            default='y'
        ).lower() == 'y'
        
        if not run_ansible:
            self.print_colored("Skipping Ansible generation. You can run it later.", 'yellow')
            return
        
        # Check if generator exists
        generators = ['generatorv3.py', 'generatorv2.py', 'generatorv1.py']
        generator_found = None
        
        for gen in generators:
            if os.path.exists(gen):
                generator_found = gen
                break
        
        if generator_found:
            self.print_colored(f"Found {generator_found}. Running Ansible generator...", 'green')
            try:
                os.system(f"python3 {generator_found}")
                self.print_colored("✓ Ansible configuration generated!", 'green')
            except Exception as e:
                self.print_colored(f"✗ Error running generator: {e}", 'red')
        else:
            self.print_colored("No generator found. Please run manually later.", 'yellow')
            self.print_colored("Available generators: generatorv1.py, generatorv2.py, generatorv3.py", 'cyan')

    def main_menu(self):
        """Main interactive menu"""
        self.print_header("INTERACTIVE NETWORK DATA GENERATOR V2")
        self.print_colored("Create custom network topologies interactively!", 'cyan')
        
        while True:
            self.print_section("Main Menu")
            self.print_colored("1. Create Custom Network (Interactive)", 'yellow')
            self.print_colored("2. Load Template Network (Quick Start)", 'yellow')
            self.print_colored("3. View Current Network Summary", 'yellow')
            self.print_colored("4. Save Network Data", 'yellow')
            self.print_colored("5. Generate Ansible Configuration", 'yellow')
            self.print_colored("6. Exit", 'yellow')
            
            choice = self.get_user_input("Select option (1-6)")
            
            if choice == '1':
                self.create_interactive_network()
            elif choice == '2':
                self.load_template_network()
            elif choice == '3':
                if self.network_data['departments'] or self.network_data['core_infrastructure']:
                    self.display_network_summary()
                else:
                    self.print_colored("No network data available. Create a network first.", 'red')
            elif choice == '4':
                if self.network_data['departments'] or self.network_data['core_infrastructure']:
                    filename = self.get_user_input("Enter filename", default="network_data.yml")
                    self.save_network_data(filename)
                else:
                    self.print_colored("No network data to save. Create a network first.", 'red')
            elif choice == '5':
                if self.network_data['departments'] or self.network_data['core_infrastructure']:
                    # Save first, then run generator
                    self.save_network_data()
                    self.run_ansible_generator()
                else:
                    self.print_colored("No network data available. Create a network first.", 'red')
            elif choice == '6':
                self.print_colored("Thank you for using Interactive Network Generator V2!", 'green')
                break
            else:
                self.print_colored("Invalid choice. Please select 1-6.", 'red')

    def create_interactive_network(self):
        """Create network interactively"""
        self.print_header("INTERACTIVE NETWORK CREATION")
        
        # Clear existing data if user wants
        if self.network_data['departments'] or self.network_data['core_infrastructure']:
            clear_data = self.get_user_input(
                "Clear existing network data? (y/n)",
                default='n'
            ).lower() == 'y'
            
            if clear_data:
                self.network_data = {'departments': [], 'core_infrastructure': []}
                self.used_vlans.clear()
                self.used_subnets.clear()
                self.print_colored("✓ Existing data cleared.", 'green')
        
        # Number of departments
        num_departments = self.get_user_input(
            "How many departments do you want to create",
            input_type='int',
            validation=lambda x: x > 0 and x <= 20
        )
        
        # Create departments
        for i in range(num_departments):
            department = self.create_department(i + 1)
            self.network_data['departments'].append(department)
        
        # Core infrastructure
        core_infrastructure = self.create_core_infrastructure()
        self.network_data['core_infrastructure'] = core_infrastructure
        
        # Display summary
        self.display_network_summary()
        
        # Auto-save
        auto_save = self.get_user_input(
            "Save network data automatically? (y/n)",
            default='y'
        ).lower() == 'y'
        
        if auto_save:
            self.save_network_data()

def main():
    """Main function"""
    try:
        generator = InteractiveNetworkGenerator()
        generator.main_menu()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user. Goodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please report this issue.")

if __name__ == "__main__":
    main()