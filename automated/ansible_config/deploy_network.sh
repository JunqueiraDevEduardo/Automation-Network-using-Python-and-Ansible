#!/bin/bash

# Network Deployment Script for GNS3 v3 API
# Automates the complete network deployment using Ansible and GNS3
# Updated for v3 API with OAuth2 authentication

# Exit on any error
set -e

# Color codes for output formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR="${SCRIPT_DIR}/../../config"
ANSIBLE_DIR="${SCRIPT_DIR}"

# Logging functions with timestamp
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Check if all prerequisites are installed and configured
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Ansible is installed
    if ! command -v ansible-playbook &> /dev/null; then
        log_error "Ansible not found. Please install Ansible first:"
        log_error "  pip3 install ansible"
        exit 1
    else
        log_success "Ansible found: $(ansible --version | head -1)"
    fi
    
    # Check if required Ansible collections are installed
    if ! ansible-galaxy collection list | grep -q cisco.ios; then
        log_warning "Cisco IOS collection not found. Installing..."
        ansible-galaxy collection install cisco.ios
    else
        log_success "Cisco IOS collection found"
    fi
    
    # Check if jq is installed (for JSON parsing)
    if ! command -v jq &> /dev/null; then
        log_warning "jq not found. Installing jq for JSON parsing..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install jq
        else
            sudo apt-get update && sudo apt-get install -y jq
        fi
    fi
    
    # Check if network_data.yml exists
    if [ ! -f "${CONFIG_DIR}/network_data.yml" ]; then
        log_error "network_data.yml not found at ${CONFIG_DIR}/network_data.yml"
        exit 1
    else
        log_success "Found network_data.yml configuration file"
    fi
    
    # Test GNS3 v3 API connectivity with OAuth2
    log_info "Testing GNS3 v3 API connection..."
    
    # First try to authenticate and get token
    AUTH_RESPONSE=$(curl -s -X POST http://127.0.0.1:3080/v3/access/users/login \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin&password=admin" 2>/dev/null || echo "FAILED")
    
    if [[ "$AUTH_RESPONSE" == "FAILED" ]] || [[ -z "$AUTH_RESPONSE" ]]; then
        log_error "Cannot connect to GNS3 server at http://127.0.0.1:3080"
        log_error "Please ensure GNS3 is running and accessible"
        exit 1
    fi
    
    # Extract token from response
    TOKEN=$(echo "$AUTH_RESPONSE" | jq -r '.access_token' 2>/dev/null || echo "")
    
    if [[ -z "$TOKEN" ]] || [[ "$TOKEN" == "null" ]]; then
        log_error "Failed to authenticate with GNS3 v3 API"
        log_error "Response: $AUTH_RESPONSE"
        exit 1
    fi
    
    # Test authenticated access
    VERSION_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
        http://127.0.0.1:3080/v3/version 2>/dev/null || echo "FAILED")
    
    if [[ "$VERSION_RESPONSE" != "FAILED" ]]; then
        VERSION=$(echo "$VERSION_RESPONSE" | jq -r '.version' 2>/dev/null || echo "Unknown")
        log_success "Connected to GNS3 v3 API - Version: $VERSION"
    else
        log_error "Failed to verify GNS3 v3 API connection"
        exit 1
    fi
    
    log_success "All prerequisites check completed!"
}

# Deploy network topology using Ansible playbooks
deploy_topology() {
    log_info "Starting network topology deployment..."
    
    cd "$ANSIBLE_DIR"
    
    # Check if the deployment playbook exists
    if [ ! -f "deploy_complete_network.yml" ]; then
        log_error "deploy_complete_network.yml not found in $ANSIBLE_DIR"
        exit 1
    fi
    
    # Run the master deployment playbook with increased verbosity
    log_info "Executing master deployment playbook..."
    ansible-playbook -v deploy_complete_network.yml
    
    if [ $? -eq 0 ]; then
        log_success "Topology deployment completed successfully!"
    else
        log_error "Topology deployment failed!"
        log_error "Check the Ansible output above for details"
        exit 1
    fi
}

# Start all nodes in the GNS3 project
start_all_nodes() {
    log_info "Starting all nodes in GNS3 project..."
    
    # Get authentication token
    TOKEN=$(curl -s -X POST http://127.0.0.1:3080/v3/access/users/login \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin&password=admin" | jq -r '.access_token')
    
    # Start all nodes
    curl -s -X POST \
        -H "Authorization: Bearer $TOKEN" \
        http://127.0.0.1:3080/v3/projects/9a8ab49a-6f61-4fa8-9089-99e6c6594e4f/nodes/start \
        > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        log_success "All nodes start command sent"
        log_info "Waiting 15 seconds for nodes to boot..."
        sleep 15
    else
        log_warning "Could not start all nodes automatically"
        log_warning "Please start nodes manually in GNS3 GUI"
    fi
}

# Configure network devices (VLANs and interfaces)
configure_devices() {
    log_info "Configuring network devices..."
    
    cd "$ANSIBLE_DIR"
    
    # Configure VLANs on switches
    if [ -f "configure_vlans.yml" ]; then
        log_info "Configuring VLANs..."
        ansible-playbook -i inventory.yml configure_vlans.yml || log_warning "VLAN configuration had issues"
    else
        log_warning "configure_vlans.yml not found, skipping VLAN configuration"
    fi
    
    # Configure switch interfaces
    if [ -f "configure_interfaces.yml" ]; then
        log_info "Configuring interfaces..."
        ansible-playbook -i inventory.yml configure_interfaces.yml || log_warning "Interface configuration had issues"
    else
        log_warning "configure_interfaces.yml not found, skipping interface configuration"
    fi
    
    log_success "Device configuration phase completed!"
}

# Test basic connectivity by checking node status
test_connectivity() {
    log_info "Testing basic connectivity..."
    
    # Get authentication token
    TOKEN=$(curl -s -X POST http://127.0.0.1:3080/v3/access/users/login \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin&password=admin" | jq -r '.access_token')
    
    # Get all nodes status
    NODES=$(curl -s -H "Authorization: Bearer $TOKEN" \
        http://127.0.0.1:3080/v3/projects/9a8ab49a-6f61-4fa8-9089-99e6c6594e4f/nodes)
    
    if [ $? -eq 0 ]; then
        # Count nodes by status
        TOTAL=$(echo "$NODES" | jq '. | length')
        STARTED=$(echo "$NODES" | jq '[.[] | select(.status == "started")] | length')
        STOPPED=$(echo "$NODES" | jq '[.[] | select(.status == "stopped")] | length')
        
        log_info "Node Status Summary:"
        log_info "  Total nodes: $TOTAL"
        log_info "  Started: $STARTED"
        log_info "  Stopped: $STOPPED"
        
        if [ "$STARTED" -eq "$TOTAL" ]; then
            log_success "All nodes are running!"
        elif [ "$STARTED" -gt 0 ]; then
            log_warning "Some nodes are not running. Check GNS3 GUI for details."
        else
            log_error "No nodes are running. Please start them in GNS3 GUI."
        fi
    else
        log_error "Could not retrieve node status"
    fi
}

# Generate network documentation
generate_docs() {
    log_info "Generating network documentation..."
    
    # Create documentation directory
    mkdir -p "${SCRIPT_DIR}/docs"
    
    # Generate network topology documentation
    cat > "${SCRIPT_DIR}/docs/network_topology.md" << EOF
# Network Topology Documentation

## Deployment Information
- **Deployment Date**: $(date)
- **GNS3 Project ID**: 9a8ab49a-6f61-4fa8-9089-99e6c6594e4f
- **Configuration File**: ${CONFIG_DIR}/network_data.yml
- **GNS3 API Version**: v3 with OAuth2 authentication

## Network Configuration

### Departments and VLANs
EOF

    # Parse network_data.yml and add department information
    if command -v python3 &> /dev/null; then
        python3 << PYTHON_SCRIPT >> "${SCRIPT_DIR}/docs/network_topology.md"
import yaml
import sys

try:
    with open('${CONFIG_DIR}/network_data.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    for dept in config.get('departments', []):
        print(f"\n#### {dept['name']}")
        print(f"- **VLAN ID**: {dept['vlan']}")
        print(f"- **Subnet**: {dept['subnet']}")
        print(f"- **Gateway**: {dept['gateway']}")
        print(f"- **Number of devices**: {len(dept.get('devices', []))}")
        
        # Count device types
        devices = dept.get('devices', [])
        switches = len([d for d in devices if d['type'] == 'switch'])
        routers = len([d for d in devices if d['type'] == 'router'])
        pcs = len([d for d in devices if d['type'] == 'pc'])
        
        print(f"  - Switches: {switches}")
        print(f"  - Routers: {routers}")
        print(f"  - PCs/Servers: {pcs}")
        
except Exception as e:
    print(f"Error parsing configuration: {e}")
    sys.exit(1)
PYTHON_SCRIPT
    fi

    # Add deployment instructions
    cat >> "${SCRIPT_DIR}/docs/network_topology.md" << EOF

## Deployment Instructions

### Prerequisites
1. GNS3 installed and running
2. Ansible installed with cisco.ios collection
3. Python 3.x with PyYAML

### Deployment Steps
1. Run \`./deploy_network.sh check\` to verify prerequisites
2. Run \`./deploy_network.sh full\` for complete deployment
3. Configure PC IP addresses using the generated script
4. Test connectivity between departments

### Post-Deployment
- All nodes should be visible in GNS3 GUI
- VLANs should be configured on switches
- Use GNS3 console to verify device configurations

## Troubleshooting

### Common Issues
1. **Authentication Failed**: Ensure GNS3 is using admin/admin credentials
2. **Nodes Not Starting**: Check GNS3 server resources and permissions
3. **Links Not Created**: Verify all nodes exist before creating links

### Support
- Check GNS3 logs: \`~/.config/GNS3/gns3_server.log\`
- Run with debug: \`ansible-playbook -vvv deploy_complete_network.yml\`
EOF

    log_success "Documentation generated in ${SCRIPT_DIR}/docs/network_topology.md"
}

# Display usage information
show_usage() {
    echo "Usage: $0 {check|topology|start|configure|test|docs|full}"
    echo
    echo "Commands:"
    echo "  check     - Check prerequisites only"
    echo "  topology  - Deploy network topology (nodes + links)"
    echo "  start     - Start all nodes in GNS3"
    echo "  configure - Configure devices (VLANs + interfaces)"
    echo "  test      - Test connectivity"
    echo "  docs      - Generate documentation"
    echo "  full      - Run complete deployment (default)"
    echo
    echo "Examples:"
    echo "  $0 check              # Verify everything is ready"
    echo "  $0 full               # Complete deployment"
    echo "  $0 topology start     # Deploy and start nodes"
}

# Main execution function
main() {
    echo "=============================================="
    echo "NETWORK AUTOMATION DEPLOYMENT SCRIPT"
    echo "GNS3 v3 API with OAuth2 Authentication"
    echo "=============================================="
    echo
    
    # Process command line arguments
    case "${1:-full}" in
        "check")
            check_prerequisites
            ;;
        "topology")
            check_prerequisites
            deploy_topology
            ;;
        "start")
            start_all_nodes
            ;;
        "configure")
            configure_devices
            ;;
        "test")
            test_connectivity
            ;;
        "docs")
            generate_docs
            ;;
        "full")
            # Complete deployment sequence
            check_prerequisites
            deploy_topology
            start_all_nodes
            configure_devices
            test_connectivity
            generate_docs
            
            echo
            echo "=============================================="
            echo "DEPLOYMENT COMPLETED SUCCESSFULLY!"
            echo "=============================================="
            echo
            echo "Next steps:"
            echo "1. Open GNS3 GUI to view your network"
            echo "2. Verify all nodes are running (green status)"
            echo "3. Configure PC IP addresses using console"
            echo "4. Test connectivity between departments"
            echo "5. Check docs/network_topology.md for details"
            ;;
        "help"|"--help"|"-h")
            show_usage
            ;;
        *)
            log_error "Unknown command: $1"
            echo
            show_usage
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"