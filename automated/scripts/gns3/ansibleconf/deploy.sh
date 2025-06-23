#!/bin/bash
# Complete Network Deployment Script
# University Network Automation Project

echo "================================================"
echo "UNIVERSITY NETWORK AUTOMATION DEPLOYMENT"
echo "FIXED SEQUENCE: Topology → Configuration"
echo "================================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'  
RED='\033[0;31m'
NC='\033[0m'

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check if ansible is installed
if ! command -v ansible-playbook &> /dev/null; then
    echo -e "${RED}ERROR: Ansible not found. Please install Ansible.${NC}"
    exit 1
fi

# Check if GNS3 is running
if ! curl -s http://127.0.0.1:3080/v3/version > /dev/null; then
    echo -e "${RED}ERROR: GNS3 server not running. Please start GNS3.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"

# Run complete deployment
echo -e "${YELLOW}Starting complete network deployment...${NC}"
echo "This will:"
echo "  1. Create GNS3 topology"
echo "  2. Configure network devices" 
echo "  3. Configure end devices"
echo "  4. Generate summary"

ansible-playbook site.yml

if [ $? -eq 0 ]; then
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo "Your network automation demonstration is ready!"
    echo "Check the output above for deployment details."
else
    echo -e "${RED}================================================${NC}"
    echo -e "${RED}DEPLOYMENT FAILED!${NC}"
    echo -e "${RED}================================================${NC}"
    echo "Check the errors above and try again."
    exit 1
fi
