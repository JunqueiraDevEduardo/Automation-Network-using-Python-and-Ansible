#!/bin/bash
# Network Deployment Script
# Deploys complete network configuration from network_data.yml

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    if ! command -v ansible &> /dev/null; then
        error "Ansible is not installed"
        exit 1
    fi
    
    if ! ansible-galaxy collection list | grep -q cisco.ios; then
        warn "Installing Cisco IOS collection..."
        ansible-galaxy collection install cisco.ios
    fi
    
    log "Prerequisites OK"
}

# Test connectivity
test_connectivity() {
    log "Testing device connectivity..."
    
    ansible network_devices -i inventories/hosts.yml -m ping --one-line || {
        warn "Some network devices not reachable"
    }
    
    log "Connectivity test completed"
}

# Deploy network
deploy_network() {
    log "Deploying network configuration..."
    
    info "Configuring VLANs..."
    ansible-playbook -i inventories/hosts.yml playbooks/configure_vlans.yml
    
    info "Deploying complete network..."
    ansible-playbook -i inventories/hosts.yml playbooks/deploy_network.yml
    
    log "Network deployment completed"
}

# Main execution
main() {
    log "Starting network deployment automation..."
    
    case "${1:-deploy}" in
        "check")
            check_prerequisites
            test_connectivity
            ;;
        "deploy")
            check_prerequisites
            deploy_network
            ;;
        "full")
            check_prerequisites
            test_connectivity
            deploy_network
            ;;
        *)
            echo "Usage: $0 {check|deploy|full}"
            echo "  check  - Check prerequisites and connectivity"
            echo "  deploy - Deploy network configuration"
            echo "  full   - Full deployment with checks"
            exit 1
            ;;
    esac
    
    log "Deployment automation completed"
}

main "$@"
