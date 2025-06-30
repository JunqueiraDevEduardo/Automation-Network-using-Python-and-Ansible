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
sys.path.append(str(Path(__file__).parent))
from automated.scripts.gns3.testv1.generatorv1 import NetworkAutomationGenerator
from scripts.gns3.verify_existing_project import EnhancedGNS3Builder
from scripts.gns3.diagnostic import GNS3NetworkManager

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
            devices = dept.get('devices', [])
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
            generator.create_directory_structure() 
            generator.create_gns3_nodes()
            generator.create_gns3_links()
             

            print("Ansible configuration generated successfully")
            
        except Exception as e:
            # Log and display any errors during generation
            self.logger.error(f"Error generating Ansible config: {e}")
            print(f"Error: {e}")

    def deploy_network_config(self):
        """
        Deploy network configuration using Ansible playbooks.
        Provides options for different deployment scopes.
        """
        print("\nDEPLOYING NETWORK CONFIGURATION")
        print("-" * 40)
        
        # Check if generated files exist
        network_automation_dir = self.base_path / "scripts" / "gns3" / "network_automation"
        if not network_automation_dir.exists():
            print("No generated configuration found. Please run 'Generate Ansible Configuration' first.")
            return
        
        print("Available deployment options:")
        print("1. Show generated inventory")
        print("2. Show generated playbooks")
        print("3. Show PC configuration script")
        
        choice = input("Choice (1-3): ").strip()
        
        if choice == "1":
            self.show_generated_inventory()
        elif choice == "2":
            self.show_generated_playbooks()
        elif choice == "3":
            self.show_pc_script()
        else:
            print("Invalid choice")

    def show_generated_inventory(self):
        """Show the generated Ansible inventory."""
        inventory_file = self.base_path / "scripts" / "gns3" / "network_automation" / "inventory.yml"
        if inventory_file.exists():
            print("\nGenerated Inventory:")
            print("-" * 20)
            with open(inventory_file, 'r') as f:
                print(f.read())
        else:
            print("Inventory file not found")

    def show_generated_playbooks(self):
        """Show the generated Ansible playbooks."""
        playbooks_dir = self.base_path / "scripts" / "gns3" / "network_automation"
        
        for playbook in ["configure_vlans.yml", "configure_interfaces.yml"]:
            playbook_file = playbooks_dir / playbook
            if playbook_file.exists():
                print(f"\n{playbook}:")
                print("-" * 30)
                with open(playbook_file, 'r') as f:
                    content = f.read()
                    print(content[:500] + "..." if len(content) > 500 else content)

    def show_pc_script(self):
        """Show the generated PC configuration script."""
        script_file = self.base_path / "scripts" / "gns3" / "network_automation" / "configure_pcs.sh"
        if script_file.exists():
            print("\nPC Configuration Script:")
            print("-" * 30)
            with open(script_file, 'r') as f:
                lines = f.readlines()
                # Show first 50 lines
                for line in lines[:50]:
                    print(line.rstrip())
                if len(lines) > 50:
                    print(f"\n... and {len(lines) - 50} more lines")
        else:
            print("PC script not found")

    def gns3_operations(self):
        """
        Handle GNS3 server operations and project management.
        """
        print("\nGNS3 OPERATIONS")
        print("-" * 30)
        print("1. Test GNS3 Connection")
        print("2. Connect to Existing Project")
        print("3. Back to Main Menu")
        
        choice = input("Choice (1-3): ").strip()
        
        if choice == "1":
            self.test_gns3_connection()
        elif choice == "2":
            self.connect_to_gns3_project()

    def test_gns3_connection(self):
        """Test connection to GNS3 server."""
        print("\nTesting GNS3 Connection...")
        print("-" * 30)
        
        try:
            # Use diagnostic manager to test connection
            diagnostic = GNS3NetworkManager(self.gns3_server, "admin", "admin")
            projects = diagnostic.list_projects()
            
            if projects:
                print(f"Successfully connected to GNS3 server")
                print(f"Found {len(projects)} projects")
            else:
                print("Connected to server but no projects found")
                
        except Exception as e:
            print(f"Connection failed: {e}")

    def connect_to_gns3_project(self):
        """Connect to an existing GNS3 project."""
        project_id = input("Enter project ID: ").strip()
        if not project_id:
            print("Project ID required")
            return
        
        try:
            builder = EnhancedGNS3Builder(
                config_file=str(self.config_path),
                gns3_server=self.gns3_server,
                project_id=project_id
            )
            
            builder.print_project_summary()
            self.project_id = project_id
            print("Connected successfully")
            
        except Exception as e:
            print(f"Connection failed: {e}")

    def verify_connectivity(self):
        """Verify network connectivity placeholder."""
        print("\nNETWORK CONNECTIVITY VERIFICATION")
        print("-" * 45)

    def backup_configurations(self):
        """Configuration backup placeholder."""
        print("\nBACKUP CONFIGURATIONS")
        print("-" * 30)

    def network_monitoring(self):
        """Network monitoring placeholder."""
        print("\nNETWORK MONITORING")
        print("-" * 25)

    def troubleshooting_tools(self):
        """Network troubleshooting tools."""
        print("\nTROUBLESHOOTING TOOLS")
        print("-" * 30)
        print("1. Ping Test")
        print("2. View Logs")
        print("3. Back to Main Menu")
        
        choice = input("Choice (1-3): ").strip()
        
        if choice == "1":
            self.ping_test()
        elif choice == "2":
            self.view_logs()

    def ping_test(self):
        """Execute simple ping test."""
        target = input("Enter target IP: ").strip()
        if target:
            try:
                result = subprocess.run(['ping', '-c', '4', target], 
                                      capture_output=True, text=True)
                print(f"\nPing results:")
                print(result.stdout)
            except Exception as e:
                print(f"Ping failed: {e}")

    def view_logs(self):
        """Display recent log entries."""
        log_path = self.base_path / "logs" / "automation.log"
        if log_path.exists():
            print("\nRecent log entries:")
            print("-" * 30)
            with open(log_path, 'r') as f:
                lines = f.readlines()
                # Display last 10 lines
                for line in lines[-10:]:
                    print(line.strip())
        else:
            print("No log file found")

    def settings_menu(self):
        """Settings and configuration management."""
        print("\nSETTINGS & CONFIGURATION")
        print("-" * 35)
        print("1. View Current Configuration")
        print("2. Edit GNS3 Server URL")
        print("3. Back to Main Menu")
        
        choice = input("Choice (1-3): ").strip()
        
        if choice == "1":
            self.view_configuration()
        elif choice == "2":
            self.edit_gns3_server()

    def view_configuration(self):
        """Display current configuration."""
        print("\nCurrent Configuration:")
        print("-" * 30)
        print(yaml.dump(self.config, default_flow_style=False, indent=2))

    def edit_gns3_server(self):
        """Allow user to modify GNS3 server URL."""
        current = self.gns3_server
        print(f"Current GNS3 server: {current}")
        new_server = input("Enter new server URL (or press Enter to keep current): ").strip()
        if new_server:
            self.gns3_server = new_server
            print(f"Server updated to: {new_server}")
        else:
            print("Server URL unchanged")

    def run(self):
        """
        Main application loop that handles user interaction.
        """
        print("Starting Network Automation Controller...")
        print(f"Config file: {self.config_file}")
        print(f"Base path: {self.base_path}")
        
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
                print("\n\nGoodbye!")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                print(f"Unexpected error: {e}")

def main():
    """Entry point for the application."""
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