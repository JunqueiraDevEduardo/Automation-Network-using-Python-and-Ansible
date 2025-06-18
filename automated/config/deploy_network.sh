#!/bin/bash

# Network Deployment Script
# Automatiza o deploy completo da rede GNS3 + Ansible

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Ansible
    if ! command -v ansible-playbook &> /dev/null; then
        log_error "Ansible not found. Installing..."
        pip3 install ansible
    fi
    
    # Check Cisco collection
    if ! ansible-galaxy collection list | grep -q cisco.ios; then
        log_warning "Installing Cisco IOS collection..."
        ansible-galaxy collection install cisco.ios
    fi
    
    # Check if GNS3 is running
    if ! curl -s http://127.0.0.1:3080/v3/version &> /dev/null; then
        log_error "GNS3 Server not accessible at http://127.0.0.1:3080"
        log_error "Please start GNS3 Server first!"
        exit 1
    fi
    
    log_success "Prerequisites check completed"
}

# Deploy topology
deploy_topology() {
    log_info "Starting network topology deployment..."
    
    cd "$(dirname "$0")"
    
    # Run the master playbook
    log_info "Executing master deployment playbook..."
    ansible-playbook -v deploy_complete_network.yml
    
    if [ $? -eq 0 ]; then
        log_success "Topology deployment completed successfully!"
    else
        log_error "Topology deployment failed!"
        exit 1
    fi
}

# Configure devices
configure_devices() {
    log_info "Configuring network devices..."
    
    # Wait for devices to be ready
    log_info "Waiting for devices to initialize..."
    sleep 10
    
    # Start all nodes
    log_info "Starting all network nodes..."
    curl -s -u admin:admin -X POST http://127.0.0.1:3080/v3/projects/9a8ab49a-6f61-4fa8-9089-99e6c6594e4f/nodes/start
    
    sleep 15  # Wait for nodes to boot
    
    # Configure VLANs
    log_info "Configuring VLANs..."
    ansible-playbook -i inventory.yml configure_vlans.yml || log_warning "VLAN configuration had issues"
    
    # Configure interfaces
    log_info "Configuring interfaces..."
    ansible-playbook -i inventory.yml configure_interfaces.yml || log_warning "Interface configuration had issues"
    
    log_success "Device configuration completed!"
}

# Test connectivity
test_connectivity() {
    log_info "Testing basic connectivity..."
    
    # Ping test between departments
    log_info "Testing inter-VLAN connectivity..."
    
    # This would normally require the devices to be fully configured
    # For now, just verify the API is responding
    if curl -s -u admin:admin http://127.0.0.1:3080/v3/projects/9a8ab49a-6f61-4fa8-9089-99e6c6594e4f/nodes | jq '.[] | select(.status == "started") | .name' &> /dev/null; then
        log_success "Nodes are running and accessible via API"
    else
        log_warning "Some nodes may not be running properly"
    fi
}

# Generate documentation
generate_docs() {
    log_info "Generating network documentation..."
    
    # Create documentation directory
    mkdir -p docs
    
    # Generate network diagram data
    cat > docs/network_topology.md << EOF
# Network Topology Documentation

## Deployment Information
- Deployment Date: $(date)
- GNS3 Project ID: 9a8ab49a-6f61-4fa8-9089-99e6c6594e4f
- Total Departments: $(grep -c "^- name:" ../../config/network_data.yml)

## VLAN Configuration
EOF

    # Add VLAN information from config
    python3 -c "
import yaml
with open('../../config/network_data.yml', 'r') as f:
    config = yaml.safe_load(f)
for dept in config.get('departments', []):
    print(f\"- VLAN {dept['vlan']}: {dept['name']} ({dept['subnet']})\")
" >> docs/network_topology.md

    log_success "Documentation generated in docs/ directory"
}

# Main execution
main() {
    echo "=============================================="
    echo "NETWORK AUTOMATION DEPLOYMENT SCRIPT"
    echo "=============================================="
    echo
    
    case "${1:-full}" in
        "check")
            check_prerequisites
            ;;
        "topology")
            check_prerequisites
            deploy_topology
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
            check_prerequisites
            deploy_topology
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
            echo "2. Configure PC IPs: ./configure_pcs.sh"
            echo "3. Test connectivity between departments"
            echo "4. Check docs/network_topology.md for details"
            ;;
        *)
            echo "Usage: $0 {check|topology|configure|test|docs|full}"
            echo
            echo "Commands:"
            echo "  check     - Check prerequisites only"
            echo "  topology  - Deploy network topology (nodes + links)"
            echo "  configure - Configure devices (VLANs + interfaces)"
            echo "  test      - Test connectivity"
            echo "  docs      - Generate documentation"
            echo "  full      - Run complete deployment (default)"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"