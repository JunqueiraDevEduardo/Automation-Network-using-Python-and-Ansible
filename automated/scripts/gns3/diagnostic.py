#!/usr/bin/env python3
"""
GNS3 Diagnostic and Fix Script
This script diagnoses your GNS3 authentication issue and provides solutions.
"""

import requests
import json
import os
from pathlib import Path

def check_gns3_config():
    """
    Check GNS3 configuration files and database.
    """
    print("🔍 Checking GNS3 Configuration...")
    
    config_dir = Path.home() / ".config" / "GNS3" / "3.0"
    gui_config = Path.home() / ".config" / "GNS3" / "3.0" / "gns3_gui.conf"
    controller_db = config_dir / "gns3_controller.db"
    
    print(f"📁 Config directory: {config_dir}")
    print(f"   Exists: {config_dir.exists()}")
    
    print(f"📄 GUI config: {gui_config}")
    print(f"   Exists: {gui_config.exists()}")
    
    print(f"💾 Controller DB: {controller_db}")
    print(f"   Exists: {controller_db.exists()}")
    
    if gui_config.exists():
        try:
            with open(gui_config, 'r') as f:
                content = f.read()
                print(f"📄 GUI Config content preview:")
                lines = content.split('\n')[:10]  # First 10 lines
                for line in lines:
                    if line.strip():
                        print(f"   {line}")
        except Exception as e:
            print(f"   Error reading config: {e}")
    
    return config_dir, controller_db

def test_endpoints():
    """
    Test various GNS3 endpoints to understand the authentication setup.
    """
    print("\n🔬 Testing GNS3 Endpoints...")
    
    server = "http://127.0.0.1:3080"
    session = requests.Session()
    session.verify = False
    
    # Test endpoints
    endpoints = [
        "/v3/version",
        "/v3/projects",
        "/v3/users/login",
        "/v3/users/me",
        "/v3/auth/login",
        "/auth/login",
        "/login",
    ]
    
    results = {}
    
    for endpoint in endpoints:
        try:
            print(f"🔗 Testing: {endpoint}")
            response = session.get(f"{server}{endpoint}", timeout=5)
            
            results[endpoint] = {
                'status': response.status_code,
                'size': len(response.text),
                'content_type': response.headers.get('content-type', 'unknown')
            }
            
            if response.status_code == 200:
                print(f"   ✅ {response.status_code} - Working")
            elif response.status_code == 401:
                print(f"   🔒 {response.status_code} - Requires authentication")
            elif response.status_code == 404:
                print(f"   ❌ {response.status_code} - Not found")
            elif response.status_code == 405:
                print(f"   ⚠️  {response.status_code} - Method not allowed (try POST)")
            else:
                print(f"   ❓ {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[endpoint] = {'error': str(e)}
    
    return results

def test_post_login():
    """
    Test POST requests to login endpoints.
    """
    print("\n🔑 Testing Login Endpoints with POST...")
    
    server = "http://127.0.0.1:3080"
    session = requests.Session()
    session.verify = False
    
    login_data = {
        "username": "admin",
        "password": "admin"
    }
    
    login_endpoints = [
        "/v3/users/login",
        "/v3/auth/login", 
        "/auth/login",
        "/login",
    ]
    
    for endpoint in login_endpoints:
        try:
            print(f"🔗 POST to: {endpoint}")
            response = session.post(f"{server}{endpoint}", json=login_data, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'access_token' in data or 'token' in data:
                        token = data.get('access_token') or data.get('token')
                        print(f"   ✅ Token received: {token[:20]}...")
                        return token
                    else:
                        print(f"   ✅ Login successful but no token")
                        print(f"   Response keys: {list(data.keys())}")
                except:
                    print(f"   ✅ Login successful (non-JSON response)")
            elif response.status_code == 404:
                print(f"   ❌ Endpoint not found")
            elif response.status_code == 422:
                print(f"   ⚠️  Invalid request format")
                print(f"   Response: {response.text}")
            else:
                print(f"   ❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

def try_no_auth_access():
    """
    Try to access projects without authentication (maybe auth is disabled).
    """
    print("\n🚫 Testing No-Auth Access...")
    
    server = "http://127.0.0.1:3080"
    session = requests.Session()
    session.verify = False
    
    # Try different ways to access projects
    project_endpoints = [
        "/v3/projects",
        "/v2/projects", 
        "/projects",
        "/api/v3/projects",
        "/controller/v3/projects"
    ]
    
    for endpoint in project_endpoints:
        try:
            print(f"🔗 Testing: {endpoint}")
            response = session.get(f"{server}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                try:
                    projects = response.json()
                    print(f"   ✅ Success! Found {len(projects)} projects")
                    for project in projects[:3]:  # Show first 3
                        print(f"      - {project.get('name', 'Unknown')} ({project.get('project_id', 'No ID')})")
                    return projects
                except:
                    print(f"   ✅ Success but non-JSON response")
            else:
                print(f"   ❌ {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return None

def check_webui_access():
    """
    Check if we can access the web UI and extract information.
    """
    print("\n🌐 Testing Web UI Access...")
    
    server = "http://127.0.0.1:3080"
    session = requests.Session()
    session.verify = False
    
    try:
        # Try to access a specific project via web UI
        project_id = "9a8ab49a-6f61-4fa8-9089-99e6c6594e4f"
        response = session.get(f"{server}/static/web-ui/controller/1/project/{project_id}", timeout=10)
        
        if response.status_code == 200:
            print(f"   ✅ Web UI accessible")
            print(f"   Response size: {len(response.text)} bytes")
            
            # Try to extract project info from HTML
            if "GNS3 Web UI" in response.text:
                print(f"   ✅ This is the GNS3 Web UI")
                return True
        else:
            print(f"   ❌ Web UI not accessible: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return False

def suggest_solutions(results):
    """
    Analyze results and suggest solutions.
    """
    print("\n💡 SUGGESTED SOLUTIONS")
    print("=" * 50)
    
    # Check if authentication is the issue
    has_401_errors = any(r.get('status') == 401 for r in results.values() if isinstance(r, dict))
    has_404_login = results.get('/v3/users/login', {}).get('status') == 404
    
    if has_404_login:
        print("🚨 MAIN ISSUE: Login endpoint not found")
        print("   This suggests your GNS3 server might not have authentication enabled")
        print("   or is using a different authentication method.")
        print()
        print("📋 Try these solutions:")
        print("1. Check if authentication is disabled in GNS3 server")
        print("2. Reset GNS3 controller database")
        print("3. Use direct project access via existing project ID")
        print()
        
    if has_401_errors:
        print("🔒 AUTHENTICATION REQUIRED")
        print("   Your server requires authentication but the login endpoint may be wrong")
        print()
        
    print("🛠️  SOLUTION STEPS:")
    print("1. RESET CONTROLLER DATABASE:")
    print("   mv ~/.config/GNS3/3.0/gns3_controller.db ~/.config/GNS3/3.0/gns3_controller.db.backup")
    print("   # Then restart GNS3 server")
    print()
    print("2. USE EXISTING PROJECT:")
    print("   # Your current project ID works via web UI")
    print("   # Update your scripts to use web UI access method")
    print()
    print("3. CHECK SERVER LOGS:")
    print("   # Look for GNS3 server process and check its logs")
    print("   ps aux | grep gns3")
    print()

def main():
    """
    Main diagnostic function.
    """
    print("🔍 GNS3 Diagnostic Tool")
    print("=" * 40)
    
    # Step 1: Check configuration
    config_dir, controller_db = check_gns3_config()
    
    # Step 2: Test endpoints
    results = test_endpoints()
    
    # Step 3: Test login with POST
    token = test_post_login()
    
    # Step 4: Try no-auth access
    projects = try_no_auth_access()
    
    # Step 5: Check web UI
    webui_works = check_webui_access()
    
    # Step 6: Provide solutions
    suggest_solutions(results)
    
    # Final recommendation
    print("\n🎯 IMMEDIATE ACTION:")
    if webui_works:
        print("✅ Your web UI works! Use the existing project ID:")
        print("   9a8ab49a-6f61-4fa8-9089-99e6c6594e4f")
        print("   Update your scripts to work with this project")
    elif projects:
        print("✅ Found projects without authentication!")
        print("   You can use these project IDs directly")
    else:
        print("🔄 Try resetting the controller database:")
        print("   1. Stop GNS3 server")
        print("   2. Backup and remove: ~/.config/GNS3/3.0/gns3_controller.db")
        print("   3. Restart GNS3 server")
        print("   4. This will reset authentication to defaults")

if __name__ == "__main__":
    main()