#!/usr/bin/env python3
"""
Network Automation Main Controller
Central orchestrator for automated network deployment and management

This script provides a unified interface to manage:
- Network configuration generation
- Ansible playbook execution
- GNS3 project management
- Configuration deployment

Usage: python3 main.py [command] [options]
"""

# Standard library imports for system operations, file handling, and process management
import os
import sys
import yaml
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Import custom modules for network automation functionality
# These modules handle GNS3 topology building, project verification, and authentication
sys.path.append(str(Path(__file__).parent))
from scripts.gns3.build_gns3_topology import NetworkAutomationGenerator
from scripts.gns3.verify_existing_project import EnhancedGNS3Builder
#add here the other scripts of gns3!

class NetworkAutomationController:
    """
    Main controller class that orchestrates all network automation operations.
    Handles configuration management, deployment, monitoring, and troubleshooting.
    """
    
    def __init__(self, config_file: str = "config/network_data.yml"):
        """
        Initialize the network automation controller with configuration paths and settings.
        Sets up logging, loads configuration, and initializes component paths.
        """
        # Core configuration and path setup
        self.config_file = config_file
        self.base_path = Path(__file__).parent  # Get the directory where this script is located
        self.config_path = self.base_path / config_file
        self.ansible_path = self.base_path / "ansible"  # Path to Ansible configurations
        self.scripts_path = self.base_path / "scripts"  # Path to automation scripts
        
        # Initialize logging system for debugging and monitoring
        self.setup_logging()
        
        # Load network configuration from YAML file
        self.load_config()
        
        # Set default GNS3 server connection and project settings
        self.gns3_server = "http://127.0.0.1:3080"  # Default local GNS3 server
        self.project_id = None  # Will be set when connecting to a specific project

    def setup_logging(self):
        """
        Configure logging system to write to both file and console.
        Creates log directory if it doesn't exist and sets up dual output handlers.
        """
        # Create logs directory if it doesn't exist
        log_dir = self.base_path / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Configure logging with timestamp, level, and message format
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                # Write logs to file for persistent storage
                logging.FileHandler(log_dir / "automation.log"),
                # Also display logs on console for real-time feedback
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        """
        Load network configuration from YAML file.
        Handles file not found and parsing errors gracefully.
        """
        try:
            if self.config_path.exists():
                # Load existing configuration file
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                self.logger.info(f"Configuration loaded from {self.config_file}")
            else:
                # Create default empty configuration if file doesn't exist
                self.logger.warning(f"Configuration file {self.config_file} not found")
                self.config = {"departments": []}
        except Exception as e:
            # Handle any errors during configuration loading
            self.logger.error(f"Error loading configuration: {e}")
            self.config = {"departments": []}

    def show_menu(self):
        """
        Display the main interactive menu with all available operations.
        This is the primary user interface for the automation system.
        """
        print("\n" + "="*60)
        print("NETWORK AUTOMATION CONTROLLER")
        print("="*60)
        print("1.  Show Network Overview")
        print("2.  Generate Ansible Configuration")
        print("3.  Deploy Network Configuration")
        print("4.  GNS3 Operations")
        print("5.  Verify Connectivity")
        print("6.  Backup Configurations")
        print("7.  Network Monitoring")
        print("8.  Troubleshooting Tools")
        print("9.  Settings & Configuration")
        print("0.  Exit")
        print("="*60)

    def show_network_overview(self):
        """
        Display comprehensive overview of the network topology and configuration.
        Shows department breakdown, device counts, VLAN assignments, and network summaries.
        """
        print("\nNETWORK OVERVIEW")
        print("-" * 40)
        
        # Get departments from configuration
        departments = self.config.get('departments', [])
        if not departments:
            print("No departments configured")
            return
        
        # Calculate total devices across all departments
        total_devices = 0
        print(f"Departments: {len(departments)}")
        print()
        
        # Iterate through each department and display its configuration
        for dept in departments:
            name = dept.get('name', 'Unknown')
            vlan = dept.get('vlan', 'N/A')
            subnet = dept.get('subnet', 'N/A')
            gateway = dept.get('gateway', 'N/A')
            
            # Calculate device count (handle different data structures)
            devices = dept.get('devices', {})
            if isinstance(devices, dict):
                dept_total = sum(devices.values())  # Sum up device counts by type
            else:
                dept_total = len(devices) if isinstance(devices, list) else 0
            
            total_devices += dept_total
            
            # Display department information
            print(f"  {name}")
            print(f"   VLAN: {vlan} | Subnet: {subnet}")
            print(f"   Gateway: {gateway} | Devices: {dept_total}")
            print()
        
        # Display network summary statistics
        print(f"Total Devices: {total_devices}")
        print(f"Total VLANs: {len(departments)}")

    def generate_ansible_config(self):
        """
        Generate Ansible configuration files from the network data.
        Creates inventories, playbooks, and role configurations for network deployment.
        """
        print("\nGENERATING ANSIBLE CONFIGURATION")
        print("-" * 40)
        
        try:
            # Use NetworkAutomationGenerator to create all Ansible configurations
            generator = NetworkAutomationGenerator(str(self.config_path))
            generator.save_all_files()  # Generate inventory, playbooks, and roles
            
            # Organize generated files into proper Ansible directory structure
            self.organize_ansible_files()
            
            print("Ansible configuration generated successfully")
            
        except Exception as e:
            # Log and display any errors during generation
            self.logger.error(f"Error generating Ansible config: {e}")
            print(f"Error: {e}")

    def organize_ansible_files(self):
        """
        Move generated files from temporary location to proper Ansible directory structure.
        Ensures files are placed in correct locations for Ansible to find them.
        """
        source_dir = self.base_path / "network_automation"
        
        if source_dir.exists():
            # Move inventory file to production inventory location
            if (source_dir / "inventory.yml").exists():
                (source_dir / "inventory.yml").rename(
                    self.ansible_path / "inventories" / "production" / "hosts.yml"
                )
            
            # Move playbooks to playbooks directory
            for playbook in ["configure_vlans.yml", "configure_interfaces.yml"]:
                if (source_dir / playbook).exists():
                    (source_dir / playbook).rename(
                        self.ansible_path / "playbooks" / playbook
                    )

    def deploy_network_config(self):
        """
        Deploy network configuration using Ansible playbooks.
        Provides options for different deployment scopes (full, network devices, end devices, department).
        """
        print("\nDEPLOYING NETWORK CONFIGURATION")
        print("-" * 40)
        
        # Verify Ansible is installed and configured before deployment
        if not self.check_ansible_prerequisites():
            return
        
        # Present deployment options to user
        print("Select deployment type:")
        print("1. Full deployment (all devices)")
        print("2. Network devices only (switches/routers)")
        print("3. End devices only (PCs/servers)")
        print("4. Specific department")
        
        choice = input("Choice (1-4): ").strip()
        
        try:
            # Execute appropriate deployment based on user choice
            if choice == "1":
                self.run_full_deployment()
            elif choice == "2":
                self.run_network_devices_deployment()
            elif choice == "3":
                self.run_end_devices_deployment()
            elif choice == "4":
                self.run_department_deployment()
            else:
                print("Invalid choice")
                
        except Exception as e:
            # Log deployment errors for troubleshooting
            self.logger.error(f"Deployment error: {e}")
            print(f"Deployment failed: {e}")

    def check_ansible_prerequisites(self) -> bool:
        """
        Verify that Ansible and required collections are installed.
        Checks for Ansible binary and cisco.ios collection specifically.
        Returns True if all prerequisites are met, False otherwise.
        """
        try:
            # Check if Ansible is installed and accessible
            result = subprocess.run(['ansible', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("Ansible not installed")
                print("Install with: pip install ansible")
                return False
            
            # Check if Cisco IOS collection is installed (required for network device management)
            result = subprocess.run(['ansible-galaxy', 'collection', 'list'], 
                                  capture_output=True, text=True)
            if 'cisco.ios' not in result.stdout:
                print("Cisco IOS collection not found")
                install = input("Install now? (y/n): ").lower().strip()
                if install == 'y':
                    # Install the required collection automatically
                    subprocess.run(['ansible-galaxy', 'collection', 'install', 'cisco.ios'])
                else:
                    return False
            
            return True
            
        except FileNotFoundError:
            # Ansible not found in system PATH
            print("Ansible not found in PATH")
            return False

    def run_full_deployment(self):
        """
        Execute complete network deployment using the main site playbook.
        Deploys configuration to all devices in the network topology.
        """
        # Define paths to inventory and main playbook
        inventory_path = self.ansible_path / "inventories" / "production" / "hosts.yml"
        site_playbook = self.ansible_path / "site.yml"
        
        # Verify inventory file exists before attempting deployment
        if not inventory_path.exists():
            print("Inventory file not found. Generate configuration first.")
            return
        
        # Construct and execute Ansible playbook command
        cmd = [
            'ansible-playbook', 
            '-i', str(inventory_path),  # Specify inventory file
            str(site_playbook)          # Specify playbook to run
        ]
        
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, cwd=str(self.ansible_path))

    def run_network_devices_deployment(self):
        """
        Deploy configuration only to network infrastructure devices (switches and routers).
        Uses specialized playbook for network device configuration.
        """
        inventory_path = self.ansible_path / "inventories" / "production" / "hosts.yml"
        playbook_path = self.ansible_path / "playbooks" / "network-devices.yml"
        
        cmd = [
            'ansible-playbook',
            '-i', str(inventory_path),
            str(playbook_path)
        ]
        
        subprocess.run(cmd, cwd=str(self.ansible_path))

    def run_end_devices_deployment(self):
        """
        Deploy configuration only to end devices (PCs and servers).
        Uses playbook specifically designed for end device configuration.
        """
        inventory_path = self.ansible_path / "inventories" / "production" / "hosts.yml"
        playbook_path = self.ansible_path / "playbooks" / "configure-pcs.yml"
        
        cmd = [
            'ansible-playbook',
            '-i', str(inventory_path),
            str(playbook_path)
        ]
        
        subprocess.run(cmd, cwd=str(self.ansible_path))

    def run_department_deployment(self):
        """
        Deploy configuration to devices in a specific department only.
        Allows targeted deployment using Ansible's limit functionality.
        """
        departments = self.config.get('departments', [])
        if not departments:
            print("No departments configured")
            return
        
        # Display available departments for selection
        print("Available departments:")
        for i, dept in enumerate(departments, 1):
            print(f"{i}. {dept.get('name', 'Unknown')}")
        
        try:
            # Get user selection and execute limited deployment
            choice = int(input("Select department: ")) - 1
            dept = departments[choice]
            dept_name = dept.get('name', 'Unknown')
            
            # Use --limit flag to restrict deployment to specific department
            cmd = [
                'ansible-playbook',
                '-i', str(self.ansible_path / "inventories" / "production" / "hosts.yml"),
                '--limit', dept_name,  # Limit execution to specific department
                str(self.ansible_path / "site.yml")
            ]
            
            subprocess.run(cmd, cwd=str(self.ansible_path))
            
        except (ValueError, IndexError):
            print("Invalid department selection")

    def gns3_operations(self):
        """
        Handle GNS3 server operations and project management.
        Provides submenu for GNS3-related functionality.
        """
        print("\nGNS3 OPERATIONS")
        print("-" * 30)
        print("1. Diagnose GNS3 Connection")
        print("2. Connect to Existing Project")
        print("3. List Available Projects")
        print("4. Project Health Check")
        print("5. Back to Main Menu")
        
        choice = input("Choice (1-5): ").strip()
        
        # Execute selected GNS3 operation
        if choice == "1":
            self.diagnose_gns3()
        elif choice == "2":
            self.connect_to_gns3_project()
        elif choice == "3":
            self.list_gns3_projects()
        elif choice == "4":
            self.gns3_health_check()

    def diagnose_gns3(self):
        """
        Run comprehensive GNS3 connection diagnostics.
        Tests authentication, connectivity, and API accessibility.
        """
        print("\nGNS3 CONNECTION DIAGNOSTICS")
        print("-" * 35)
        
        try:
            # Use GNS3AuthDiagnostic to test connection and authentication
            diagnostic = GNS3AuthDiagnostic(self.gns3_server)
            diagnostic.comprehensive_test("admin", "admin")  # Test with default credentials
        except Exception as e:
            print(f"Diagnostic error: {e}")

    def connect_to_gns3_project(self):
        """
        Connect to an existing GNS3 project using project ID.
        Establishes connection and stores project reference for future operations.
        """
        project_id = input("Enter project ID: ").strip()
        if not project_id:
            print("Project ID required")
            return
        
        try:
            # Create GNS3 builder instance and connect to specified project
            builder = EnhancedGNS3Builder(
                config_file=str(self.config_path),
                gns3_server=self.gns3_server,
                project_id=project_id
            )
            
            # Display project information and store connection
            builder.print_project_summary()
            self.project_id = project_id
            print("Connected successfully")
            
        except Exception as e:
            print(f"Connection failed: {e}")

    def list_gns3_projects(self):
        """
        List all available projects on the GNS3 server.
        Helps users identify correct project IDs for connection.
        """
        print("\nAvailable GNS3 Projects")
        print("-" * 30)
        try:
            # Create temporary builder instance to access project listing functionality
            builder = EnhancedGNS3Builder(
                config_file=str(self.config_path),
                gns3_server=self.gns3_server,
                project_id="dummy"  # Placeholder ID for listing operation
            )
            builder.list_available_projects()
        except:
            print("Could not retrieve project list")

    def gns3_health_check(self):
        """
        Perform comprehensive health check of GNS3 server.
        Tests server status, compute nodes, and overall system health.
        """
        print("\nGNS3 HEALTH CHECK")
        print("-" * 25)
        try:
            builder = EnhancedGNS3Builder(
                config_file=str(self.config_path),
                gns3_server=self.gns3_server,
                project_id="dummy"
            )
            builder.check_server_health()
        except Exception as e:
            print(f"Health check failed: {e}")

    def verify_connectivity(self):
        """
        Verify network connectivity to all configured devices using Ansible ping.
        Tests reachability of network devices, end devices, and all devices.
        """
        print("\nNETWORK CONNECTIVITY VERIFICATION")
        print("-" * 45)
        
        # Path to Ansible inventory file
        inventory_path = self.ansible_path / "inventories" / "production" / "hosts.yml"
        
        if not inventory_path.exists():
            print("Inventory not found. Generate configuration first.")
            return
        
        # Test different device groups for comprehensive connectivity verification
        device_groups = ["network_devices", "end_devices", "all"]
        
        for group in device_groups:
            print(f"\nTesting {group}...")
            # Use Ansible ping module to test connectivity
            cmd = [
                'ansible', group,
                '-i', str(inventory_path),
                '-m', 'ping'  # Ansible ping module
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, 
                                      cwd=str(self.ansible_path))
                if result.returncode == 0:
                    print(f"{group}: All devices reachable")
                else:
                    print(f"{group}: Some devices unreachable")
                    print(result.stderr)
            except Exception as e:
                print(f"Error testing {group}: {e}")

    def backup_configurations(self):
        """
        Execute backup script to save current device configurations.
        Calls external backup script if available.
        """
        print("\nBACKUP CONFIGURATIONS")
        print("-" * 30)
        
        # Path to backup script
        backup_script = self.scripts_path / "deployment" / "deploy.sh"
        
        if backup_script.exists():
            # Execute backup script with backup parameter
            cmd = [str(backup_script), "backup"]
            subprocess.run(cmd)
        else:
            print("Backup script not found")
            print("Run deployment setup first")

    def network_monitoring(self):
        """
        Network monitoring dashboard placeholder.
        This function is prepared for future monitoring capabilities.
        """
        print("\nNETWORK MONITORING")
        print("-" * 25)
        print("Feature under development")
        print("Future capabilities:")
        print("- Real-time device status")
        print("- Performance metrics")
        print("- Alert management")

    def troubleshooting_tools(self):
        """
        Network troubleshooting tools menu.
        Provides access to various diagnostic and troubleshooting utilities.
        """
        print("\nTROUBLESHOOTING TOOLS")
        print("-" * 30)
        print("1. Ping Test")
        print("2. Traceroute")
        print("3. Port Scan")
        print("4. Configuration Diff")
        print("5. Log Analysis")
        print("6. Back to Main Menu")
        
        choice = input("Choice (1-6): ").strip()
        
        # Execute selected troubleshooting tool
        if choice == "1":
            self.ping_test()
        elif choice == "2":
            self.traceroute_test()
        elif choice == "3":
            self.port_scan()
        elif choice == "4":
            self.config_diff()
        elif choice == "5":
            self.log_analysis()

    def ping_test(self):
        """Execute simple ping test to specified target IP address."""
        target = input("Enter target IP: ").strip()
        if target:
            # Run system ping command with 4 packets
            subprocess.run(['ping', '-c', '4', target])

    def traceroute_test(self):
        """Execute traceroute to specified target to trace network path."""
        target = input("Enter target IP: ").strip()
        if target:
            # Run system traceroute command
            subprocess.run(['traceroute', target])

    def port_scan(self):
        """Port scanning functionality placeholder."""
        print("Port scan feature under development")

    def config_diff(self):
        """Configuration difference analysis placeholder."""
        print("Config diff feature under development")

    def log_analysis(self):
        """
        Display recent log entries from the automation log file.
        Shows last 20 log entries for quick troubleshooting.
        """
        log_path = self.base_path / "logs" / "automation.log"
        if log_path.exists():
            print("\nRecent log entries:")
            with open(log_path, 'r') as f:
                lines = f.readlines()
                # Display last 20 lines of the log file
                for line in lines[-20:]:
                    print(line.strip())
        else:
            print("No log file found")

    def settings_menu(self):
        """
        Settings and configuration management menu.
        Allows viewing, editing, and managing system configuration.
        """
        print("\nSETTINGS & CONFIGURATION")
        print("-" * 35)
        print("1. View Current Configuration")
        print("2. Edit GNS3 Server URL")
        print("3. Reset Configuration")
        print("4. Export Configuration")
        print("5. Import Configuration")
        print("6. Back to Main Menu")
        
        choice = input("Choice (1-6): ").strip()
        
        # Execute selected settings operation
        if choice == "1":
            self.view_configuration()
        elif choice == "2":
            self.edit_gns3_server()
        elif choice == "3":
            self.reset_configuration()
        elif choice == "4":
            self.export_configuration()
        elif choice == "5":
            self.import_configuration()

    def view_configuration(self):
        """Display current configuration in YAML format."""
        print("\nCurrent Configuration:")
        print(yaml.dump(self.config, default_flow_style=False, indent=2))

    def edit_gns3_server(self):
        """Allow user to modify GNS3 server URL."""
        current = self.gns3_server
        print(f"Current GNS3 server: {current}")
        new_server = input("Enter new server URL: ").strip()
        if new_server:
            self.gns3_server = new_server
            print(f"Server updated to: {new_server}")

    def reset_configuration(self):
        """Reset configuration to default empty state with user confirmation."""
        confirm = input("Are you sure? This will reset all settings (y/n): ").lower()
        if confirm == 'y':
            self.config = {"departments": []}
            print("Configuration reset")

    def export_configuration(self):
        """Export current configuration to specified file."""
        filename = input("Export filename: ").strip()
        if filename:
            try:
                with open(filename, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False)
                print(f"Configuration exported to {filename}")
            except Exception as e:
                print(f"Export failed: {e}")

    def import_configuration(self):
        """Import configuration from specified file."""
        filename = input("Import filename: ").strip()
        if filename and Path(filename).exists():
            try:
                with open(filename, 'r') as f:
                    self.config = yaml.safe_load(f)
                print(f"Configuration imported from {filename}")
            except Exception as e:
                print(f"Import failed: {e}")
        else:
            print("File not found")

    def run(self):
        """
        Main application loop that handles user interaction.
        Displays menu, processes user input, and executes corresponding functions.
        Includes error handling and graceful shutdown capabilities.
        """
        print("Starting Network Automation Controller...")
        
        while True:
            try:
                # Display menu and get user choice
                self.show_menu()
                choice = input("\nSelect option: ").strip()
                
                # Execute function based on user selection
                if choice == "1":
                    self.show_network_overview()
                elif choice == "2":
                    self.generate_ansible_config()
                elif choice == "3":
                    self.deploy_network_config()
                elif choice == "4":
                    self.gns3_operations()
                elif choice == "5":
                    self.verify_connectivity()
                elif choice == "6":
                    self.backup_configurations()
                elif choice == "7":
                    self.network_monitoring()
                elif choice == "8":
                    self.troubleshooting_tools()
                elif choice == "9":
                    self.settings_menu()
                elif choice == "0":
                    print("Goodbye!")
                    break
                else:
                    print("Invalid option. Please try again.")
                
                # Wait for user acknowledgment before continuing
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print("\n\nGoodbye!")
                break
            except Exception as e:
                # Log and display unexpected errors
                self.logger.error(f"Unexpected error: {e}")
                print(f"Unexpected error: {e}")

def main():
    """
    Entry point for the application.
    Handles command line arguments and initializes the controller.
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Network Automation Controller")
    parser.add_argument('--config', '-c', default='config/network_data.yml',
                       help='Configuration file path')
    parser.add_argument('--server', '-s', default='http://127.0.0.1:3080',
                       help='GNS3 server URL')
    parser.add_argument('--non-interactive', action='store_true',
                       help='Run in non-interactive mode')
    
    args = parser.parse_args()
    
    try:
        # Initialize controller with parsed arguments
        controller = NetworkAutomationController(config_file=args.config)
        controller.gns3_server = args.server
        
        if args.non_interactive:
            # Run automated tasks without user interaction
            controller.show_network_overview()
        else:
            # Run interactive menu system
            controller.run()
            
    except Exception as e:
        print(f"Failed to start controller: {e}")
        sys.exit(1)

# Execute main function when script is run directly
if __name__ == "__main__":
    main()