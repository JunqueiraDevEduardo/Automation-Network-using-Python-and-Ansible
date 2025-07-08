#!/usr/bin/env python3
"""
Network Device Management Automation Script
Implements the flowchart workflow for device discovery, SSH access, and credential management.
"""

import asyncio
import subprocess
import paramiko
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import ipaddress
import logging
import json
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('network_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DeviceInfo:
    """Data class to store device information"""
    ip_address: str
    hostname: str = ""
    device_type: str = ""
    ssh_status: str = ""
    credential_status: str = ""
    error_message: str = ""
    timestamp: str = ""
    old_username: str = ""
    new_username: str = ""
    ping_status: str = ""

class NetworkDeviceManager:
    """
    Main class implementing the flowchart workflow:
    1. Test IP connectivity (ping)
    2. SSH to reachable devices
    3. Get hostnames
    4. Update credentials
    5. Log to Excel
    6. Send email report
    """
    
    def __init__(self, config_file: str = "network_config.json"):
        """Initialize the network device manager with configuration"""
        self.config = self.load_config(config_file)
        self.results: List[DeviceInfo] = []
        self.failed_ips: List[str] = []
        self.successful_devices: List[DeviceInfo] = []
        
        # SSH configuration
        self.ssh_timeout = self.config.get('ssh_timeout', 10)
        self.max_concurrent = self.config.get('max_concurrent_connections', 5)
        
        # Email configuration
        self.smtp_server = self.config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = self.config.get('smtp_port', 587)
        self.email_user = self.config.get('email_user', '')
        self.email_password = self.config.get('email_password', '')
        self.email_recipients = self.config.get('email_recipients', [])
        
        # Credential configuration
        self.old_credentials = self.config.get('old_credentials', {})
        self.new_credentials = self.config.get('new_credentials', {})
        
        logger.info("Network Device Manager initialized")

    def load_config(self, config_file: str) -> dict:
        """Load configuration from JSON file"""
        default_config = {
            "ip_ranges": ["192.168.1.0/24"],
            "ssh_timeout": 10,
            "max_concurrent_connections": 5,
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email_user": "",
            "email_password": "",
            "email_recipients": [],
            "old_credentials": {
                "username": "admin",
                "password": "admin"
            },
            "new_credentials": {
                "username": "netadmin",
                "password": "NewSecureP@ss123"
            },
            "device_types": {
                "cisco": {
                    "enable_command": "enable",
                    "config_mode": "configure terminal",
                    "save_command": "write memory"
                },
                "linux": {
                    "shell_prompt": "$",
                    "sudo_command": "sudo"
                }
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                    logger.info(f"Configuration loaded from {config_file}")
            else:
                # Create default config file
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created default configuration file: {config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            
        return default_config

    def generate_ip_list(self) -> List[str]:
        """Generate list of IP addresses from configured ranges"""
        ip_list = []
        
        for ip_range in self.config.get('ip_ranges', []):
            try:
                network = ipaddress.ip_network(ip_range, strict=False)
                ip_list.extend([str(ip) for ip in network.hosts()])
                logger.info(f"Generated {len(list(network.hosts()))} IPs from range {ip_range}")
            except Exception as e:
                logger.error(f"Error processing IP range {ip_range}: {e}")
                
        return ip_list

    def ping_ip(self, ip: str) -> bool:
        """Test if IP address is pingable"""
        try:
            # Use ping command based on OS
            if os.name == 'nt':  # Windows
                result = subprocess.run(['ping', '-n', '1', ip], 
                                      capture_output=True, text=True, timeout=5)
            else:  # Unix/Linux
                result = subprocess.run(['ping', '-c', '1', ip], 
                                      capture_output=True, text=True, timeout=5)
            
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error pinging {ip}: {e}")
            return False

    def get_device_info_ssh(self, ip: str) -> DeviceInfo:
        """SSH to device and gather information"""
        device_info = DeviceInfo(
            ip_address=ip,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ping_status="Success"
        )
        
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            # Try SSH connection with old credentials
            ssh_client.connect(
                ip,
                username=self.old_credentials['username'],
                password=self.old_credentials['password'],
                timeout=self.ssh_timeout
            )
            
            device_info.ssh_status = "Connected"
            logger.info(f"SSH connected to {ip}")
            
            # Get hostname
            hostname = self.get_hostname(ssh_client)
            device_info.hostname = hostname
            
            # Detect device type
            device_type = self.detect_device_type(ssh_client)
            device_info.device_type = device_type
            
            # Update credentials
            credential_result = self.update_credentials(ssh_client, device_type)
            device_info.credential_status = credential_result
            device_info.old_username = self.old_credentials['username']
            device_info.new_username = self.new_credentials['username']
            
            logger.info(f"Device {ip} ({hostname}) processed successfully")
            
        except paramiko.AuthenticationException:
            device_info.ssh_status = "Authentication Failed"
            device_info.error_message = "Invalid credentials"
            logger.warning(f"Authentication failed for {ip}")
            
        except paramiko.SSHException as e:
            device_info.ssh_status = "SSH Error"
            device_info.error_message = str(e)
            logger.error(f"SSH error for {ip}: {e}")
            
        except Exception as e:
            device_info.ssh_status = "Connection Failed"
            device_info.error_message = str(e)
            logger.error(f"Connection failed for {ip}: {e}")
            
        finally:
            ssh_client.close()
            
        return device_info

    def get_hostname(self, ssh_client: paramiko.SSHClient) -> str:
        """Get hostname from connected device"""
        try:
            # Try common hostname commands
            hostname_commands = [
                'hostname',
                'show version | include hostname',
                'cat /etc/hostname',
                'uname -n'
            ]
            
            for cmd in hostname_commands:
                try:
                    stdin, stdout, stderr = ssh_client.exec_command(cmd)
                    output = stdout.read().decode().strip()
                    if output and not output.startswith('bash:'):
                        # Extract hostname from output
                        if 'hostname' in output.lower():
                            # For Cisco devices
                            lines = output.split('\n')
                            for line in lines:
                                if 'hostname' in line.lower():
                                    return line.split()[-1]
                        else:
                            # For Linux/Unix devices
                            return output.split('\n')[0].strip()
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting hostname: {e}")
            
        return "Unknown"

    def detect_device_type(self, ssh_client: paramiko.SSHClient) -> str:
        """Detect device type (Cisco, Linux, etc.)"""
        try:
            # Try to execute 'show version' for Cisco devices
            stdin, stdout, stderr = ssh_client.exec_command('show version')
            output = stdout.read().decode().strip()
            
            if 'cisco' in output.lower() or 'ios' in output.lower():
                return "Cisco"
            elif 'linux' in output.lower():
                return "Linux"
            else:
                # Try uname for Unix/Linux systems
                stdin, stdout, stderr = ssh_client.exec_command('uname -a')
                output = stdout.read().decode().strip()
                if 'linux' in output.lower():
                    return "Linux"
                elif 'unix' in output.lower():
                    return "Unix"
                    
        except Exception as e:
            logger.error(f"Error detecting device type: {e}")
            
        return "Unknown"

    def update_credentials(self, ssh_client: paramiko.SSHClient, device_type: str) -> str:
        """Update device credentials based on device type"""
        try:
            if device_type.lower() == "cisco":
                return self.update_cisco_credentials(ssh_client)
            elif device_type.lower() in ["linux", "unix"]:
                return self.update_linux_credentials(ssh_client)
            else:
                return "Unsupported device type"
                
        except Exception as e:
            logger.error(f"Error updating credentials: {e}")
            return f"Failed: {str(e)}"

    def update_cisco_credentials(self, ssh_client: paramiko.SSHClient) -> str:
        """Update credentials on Cisco devices"""
        try:
            # Enter privileged mode
            stdin, stdout, stderr = ssh_client.exec_command('enable')
            stdin.write(self.old_credentials['password'] + '\n')
            stdin.flush()
            
            # Enter configuration mode
            stdin, stdout, stderr = ssh_client.exec_command('configure terminal')
            
            # Add new user
            new_user_cmd = f"username {self.new_credentials['username']} privilege 15 secret {self.new_credentials['password']}"
            stdin, stdout, stderr = ssh_client.exec_command(new_user_cmd)
            
            # Remove old user (if different)
            if self.old_credentials['username'] != self.new_credentials['username']:
                old_user_cmd = f"no username {self.old_credentials['username']}"
                stdin, stdout, stderr = ssh_client.exec_command(old_user_cmd)
            
            # Save configuration
            stdin, stdout, stderr = ssh_client.exec_command('end')
            stdin, stdout, stderr = ssh_client.exec_command('write memory')
            
            return "Success"
            
        except Exception as e:
            return f"Failed: {str(e)}"

    def update_linux_credentials(self, ssh_client: paramiko.SSHClient) -> str:
        """Update credentials on Linux/Unix devices"""
        try:
            # Add new user
            add_user_cmd = f"sudo useradd -m -s /bin/bash {self.new_credentials['username']}"
            stdin, stdout, stderr = ssh_client.exec_command(add_user_cmd)
            
            # Set password
            set_pass_cmd = f"echo '{self.new_credentials['username']}:{self.new_credentials['password']}' | sudo chpasswd"
            stdin, stdout, stderr = ssh_client.exec_command(set_pass_cmd)
            
            # Add to sudo group
            sudo_cmd = f"sudo usermod -aG sudo {self.new_credentials['username']}"
            stdin, stdout, stderr = ssh_client.exec_command(sudo_cmd)
            
            # Remove old user (if different)
            if self.old_credentials['username'] != self.new_credentials['username']:
                del_user_cmd = f"sudo userdel -r {self.old_credentials['username']}"
                stdin, stdout, stderr = ssh_client.exec_command(del_user_cmd)
            
            return "Success"
            
        except Exception as e:
            return f"Failed: {str(e)}"

    def process_devices(self, ip_list: List[str]) -> None:
        """Process devices following the flowchart workflow"""
        logger.info(f"Starting to process {len(ip_list)} IP addresses")
        
        # Step 1: Test IP connectivity
        logger.info("Step 1: Testing IP connectivity...")
        pingable_ips = []
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # Submit ping tasks
            ping_futures = {executor.submit(self.ping_ip, ip): ip for ip in ip_list}
            
            for future in as_completed(ping_futures):
                ip = ping_futures[future]
                try:
                    if future.result():
                        pingable_ips.append(ip)
                        logger.info(f"✓ {ip} is pingable")
                    else:
                        self.failed_ips.append(ip)
                        logger.info(f"✗ {ip} is not pingable")
                except Exception as e:
                    self.failed_ips.append(ip)
                    logger.error(f"Error pinging {ip}: {e}")
        
        logger.info(f"Ping results: {len(pingable_ips)} pingable, {len(self.failed_ips)} failed")
        
        # Step 2: SSH to pingable devices
        logger.info("Step 2: SSH to pingable devices...")
        
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # Submit SSH tasks
            ssh_futures = {executor.submit(self.get_device_info_ssh, ip): ip for ip in pingable_ips}
            
            for future in as_completed(ssh_futures):
                ip = ssh_futures[future]
                try:
                    device_info = future.result()
                    self.results.append(device_info)
                    
                    if device_info.ssh_status == "Connected":
                        self.successful_devices.append(device_info)
                        logger.info(f"✓ {ip} processed successfully")
                    else:
                        logger.warning(f"✗ {ip} failed: {device_info.error_message}")
                        
                except Exception as e:
                    logger.error(f"Error processing {ip}: {e}")
                    # Add failed device to results
                    failed_device = DeviceInfo(
                        ip_address=ip,
                        ping_status="Success",
                        ssh_status="Processing Error",
                        error_message=str(e),
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                    self.results.append(failed_device)

        # Add failed ping results to overall results
        for ip in self.failed_ips:
            failed_device = DeviceInfo(
                ip_address=ip,
                ping_status="Failed",
                ssh_status="N/A",
                error_message="Device not pingable",
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            self.results.append(failed_device)

        logger.info(f"Processing complete: {len(self.successful_devices)} successful, {len(self.results) - len(self.successful_devices)} failed")

    def save_to_excel(self, filename: str = None) -> str:
        """Save results to Excel file"""
        if filename is None:
            filename = f"network_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        try:
            # Convert results to DataFrame
            data = [asdict(device) for device in self.results]
            df = pd.DataFrame(data)
            
            # Create Excel writer with multiple sheets
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # All results
                df.to_excel(writer, sheet_name='All Devices', index=False)
                
                # Successful devices
                successful_data = [asdict(device) for device in self.successful_devices]
                if successful_data:
                    successful_df = pd.DataFrame(successful_data)
                    successful_df.to_excel(writer, sheet_name='Successful', index=False)
                
                # Failed devices
                failed_data = [asdict(device) for device in self.results 
                              if device.ssh_status != "Connected"]
                if failed_data:
                    failed_df = pd.DataFrame(failed_data)
                    failed_df.to_excel(writer, sheet_name='Failed', index=False)
                
                # Summary sheet
                summary_data = {
                    'Metric': ['Total IPs Processed', 'Pingable', 'Not Pingable', 'SSH Successful', 'SSH Failed', 'Credentials Updated'],
                    'Count': [
                        len(self.results),
                        len([d for d in self.results if d.ping_status == "Success"]),
                        len([d for d in self.results if d.ping_status == "Failed"]),
                        len([d for d in self.results if d.ssh_status == "Connected"]),
                        len([d for d in self.results if d.ssh_status not in ["Connected", "N/A"]]),
                        len([d for d in self.results if d.credential_status == "Success"])
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            logger.info(f"Results saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving Excel file: {e}")
            raise

    def send_email_report(self, excel_filename: str) -> bool:
        """Send Excel report via email"""
        try:
            if not self.email_recipients:
                logger.warning("No email recipients configured")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = ', '.join(self.email_recipients)
            msg['Subject'] = f"Network Device Audit Report - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Email body
            body = f"""
Network Device Audit Report

Summary:
- Total IPs Processed: {len(self.results)}
- Successful SSH Connections: {len(self.successful_devices)}
- Failed Connections: {len(self.results) - len(self.successful_devices)}
- Ping Failures: {len(self.failed_ips)}

Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please find the detailed Excel report attached.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach Excel file
            with open(excel_filename, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {os.path.basename(excel_filename)}'
                )
                msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email report sent to {len(self.email_recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def run(self) -> None:
        """Main execution method following the flowchart"""
        logger.info("Starting Network Device Management Automation")
        
        try:
            # Generate IP list
            ip_list = self.generate_ip_list()
            if not ip_list:
                logger.error("No IP addresses to process")
                return
            
            # Process devices
            self.process_devices(ip_list)
            
            # Save results to Excel
            excel_filename = self.save_to_excel()
            
            # Send email report
            if self.email_recipients:
                self.send_email_report(excel_filename)
            
            # Print summary
            self.print_summary()
            
        except Exception as e:
            logger.error(f"Error in main execution: {e}")
            raise

    def print_summary(self) -> None:
        """Print execution summary"""
        print("\n" + "="*60)
        print("NETWORK DEVICE MANAGEMENT AUTOMATION - SUMMARY")
        print("="*60)
        print(f"Total IPs Processed: {len(self.results)}")
        print(f"Successful SSH Connections: {len(self.successful_devices)}")
        print(f"Failed Connections: {len(self.results) - len(self.successful_devices)}")
        print(f"Ping Failures: {len(self.failed_ips)}")
        print(f"Credentials Updated: {len([d for d in self.results if d.credential_status == 'Success'])}")
        print("\nDetailed results saved to Excel file")
        print("="*60)

if __name__ == "__main__":
    # Create and run the network device manager
    manager = NetworkDeviceManager()
    manager.run()