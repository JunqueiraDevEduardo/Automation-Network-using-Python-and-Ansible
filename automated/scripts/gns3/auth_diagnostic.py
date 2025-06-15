#!/usr/bin/env python3
"""
GNS3 Authentication Diagnostic Tool
This script helps diagnose authentication issues with GNS3 server
"""

import requests
import getpass
import json
from typing import Dict, Any

class GNS3AuthDiagnostic:
    def __init__(self, server_url: str = "http://127.0.0.1:3080"):
        self.server = server_url.rstrip('/')
        self.session = requests.Session()
        self.session.verify = False
        
    def test_endpoint(self, endpoint: str, auth_method: str = None, auth_data: Any = None) -> Dict:
        """Test a specific endpoint with given authentication"""
        test_session = requests.Session()
        test_session.verify = False
        
        if auth_method == 'basic' and auth_data:
            test_session.auth = auth_data
        elif auth_method == 'bearer' and auth_data:
            test_session.headers.update({'Authorization': f'Bearer {auth_data}'})
        
        try:
            response = test_session.get(f"{self.server}{endpoint}", timeout=10)
            return {
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'response_size': len(response.text),
                'content_type': response.headers.get('content-type', 'unknown'),
                'error': None
            }
        except Exception as e:
            return {
                'status_code': None,
                'success': False,
                'response_size': 0,
                'content_type': 'error',
                'error': str(e)
            }
    
    def get_auth_token(self, username: str, password: str) -> str:
        """Try to get authentication token"""
        login_endpoints = [
            "/v3/access/users/login",
            "/v2/auth/login", 
            "/auth/login",
            "/login"
        ]
        
        for endpoint in login_endpoints:
            try:
                response = requests.post(
                    f"{self.server}{endpoint}",
                    json={"username": username, "password": password},
                    timeout=10,
                    verify=False
                )
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("token") or data.get("access_token")
                    if token:
                        print(f"✓ Token obtained from {endpoint}")
                        return token
                else:
                    print(f"⚠ {endpoint}: {response.status_code}")
                    
            except Exception as e:
                print(f"⚠ {endpoint} failed: {e}")
        
        return None
    
    def comprehensive_test(self, username: str, password: str):
        """Run comprehensive authentication tests"""
        print("🔍 GNS3 Authentication Diagnostic")
        print("=" * 50)
        
        # Test basic connectivity
        print("\n1. Basic Connectivity Test")
        print("-" * 30)
        
        basic_endpoints = [
            "/",
            "/version", 
            "/v2/version",
            "/v3/version",
            "/static/web-ui/server/version"
        ]
        
        for endpoint in basic_endpoints:
            result = self.test_endpoint(endpoint)
            status = "✓" if result['success'] else "✗"
            print(f"{status} {endpoint}: {result['status_code']} ({result['response_size']} bytes)")
        
        # Try to get authentication token
        print("\n2. Authentication Token Test")
        print("-" * 30)
        
        token = self.get_auth_token(username, password)
        
        # Test different authentication methods
        print("\n3. Authentication Method Tests")
        print("-" * 30)
        
        auth_methods = [
            ('none', None),
            ('basic', (username, password))
        ]
        
        if token:
            auth_methods.append(('bearer', token))
        
        test_endpoints = [
            "/v2/projects",
            "/v3/projects", 
            "/v2/templates",
            "/v3/templates"
        ]
        
        results = {}
        
        for auth_name, auth_data in auth_methods:
            print(f"\nTesting {auth_name} authentication:")
            results[auth_name] = {}
            
            for endpoint in test_endpoints:
                result = self.test_endpoint(endpoint, auth_name, auth_data)
                status = "✓" if result['success'] else "✗"
                results[auth_name][endpoint] = result
                print(f"  {status} {endpoint}: {result['status_code']}")
        
        # Summary and recommendations
        print("\n4. Summary & Recommendations")
        print("-" * 30)
        
        working_methods = []
        for auth_name, endpoints in results.items():
            working_count = sum(1 for r in endpoints.values() if r['success'])
            if working_count > 0:
                working_methods.append((auth_name, working_count, len(endpoints)))
                print(f"✓ {auth_name}: {working_count}/{len(endpoints)} endpoints working")
            else:
                print(f"✗ {auth_name}: No endpoints working")
        
        if working_methods:
            best_method = max(working_methods, key=lambda x: x[1])
            print(f"\n🎯 Recommended: Use '{best_method[0]}' authentication")
            
            if best_method[0] == 'bearer' and token:
                print(f"   Token: {token[:20]}...")
            elif best_method[0] == 'basic':
                print(f"   Username: {username}")
                print(f"   Password: [hidden]")
        else:
            print("\n❌ No working authentication method found!")
            print("\nTroubleshooting steps:")
            print("1. Check if GNS3 server is running")
            print("2. Verify server address and port")
            print("3. Check username/password")
            print("4. Try accessing GNS3 web interface manually")
        
        # Check for specific error patterns
        print("\n5. Error Pattern Analysis")
        print("-" * 30)
        
        all_results = []
        for endpoints in results.values():
            all_results.extend(endpoints.values())
        
        status_codes = [r['status_code'] for r in all_results if r['status_code']]
        
        if 401 in status_codes:
            print("⚠ Found 401 Unauthorized errors - authentication issue")
        if 403 in status_codes:
            print("⚠ Found 403 Forbidden errors - permission issue")
        if 404 in status_codes:
            print("⚠ Found 404 Not Found errors - wrong API version or endpoint")
        if 500 in status_codes:
            print("⚠ Found 500 Server errors - GNS3 server issue")
        
        connection_errors = [r for r in all_results if r['error']]
        if connection_errors:
            print(f"⚠ Found {len(connection_errors)} connection errors")
            for error in connection_errors[:3]:  # Show first 3 errors
                print(f"   - {error['error']}")

def main():
    """Main diagnostic function"""
    print("🌐 GNS3 Authentication Diagnostic Tool")
    print("=" * 50)
    
    # Get user input
    server = input("GNS3 Server URL (default: http://127.0.0.1:3080): ").strip() or "http://127.0.0.1:3080"
    username = input("Username (default: admin): ").strip() or "admin"
    password = getpass.getpass("Password (default: admin): ") or "admin"
    
    # Run diagnostic
    diagnostic = GNS3AuthDiagnostic(server)
    diagnostic.comprehensive_test(username, password)

if __name__ == "__main__":
    main()