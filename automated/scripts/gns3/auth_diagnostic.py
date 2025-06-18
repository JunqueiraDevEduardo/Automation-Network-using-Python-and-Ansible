#!/usr/bin/env python3
"""
Final GNS3 Authentication Fix
Based on the OAuth2PasswordBearer requirement from your API docs
"""

import requests
import json
from urllib.parse import urlencode

def try_oauth2_format():
    """
    Try OAuth2 password bearer format (form data instead of JSON).
    """
    print(" Trying OAuth2 Password Bearer format...")
    
    server = "http://127.0.0.1:3080"
    username = "admin"
    password = "admin"
    
    session = requests.Session()
    session.verify = False
    
    # OAuth2 typically expects form data, not JSON
    auth_data = {
        "username": username,
        "password": password
    }
    
    endpoints_to_try = [
        "/v3/access/users/login",
        "/v3/access/users/authenticate"
    ]
    
    for endpoint in endpoints_to_try:
        print(f"\n Testing: {endpoint}")
        
        # Method 1: Form data (OAuth2 standard)
        try:
            print(" Trying form data...")
            response = session.post(
                f"{server}{endpoint}", 
                data=auth_data,  # Using data= instead of json=
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            print(f" Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f" Form data worked!")
                try:
                    data = response.json()
                    token = data.get('access_token') or data.get('token')
                    if token:
                        print(f"   Token received: {token[:20]}...")
                        return test_token(session, server, token)
                    else:
                        print(f"    No token in response: {list(data.keys())}")
                except:
                    print(f"    Non-JSON response: {response.text[:100]}")
            elif response.status_code == 422:
                print(f"   Still 422: {response.text}")
            else:
                print(f"   Status {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   Error: {e}")
        
        # Method 2: Try different field names
        try:
            print("   Trying different field names...")
            alt_data = {
                "email": username,  # Some APIs use email instead of username
                "password": password
            }
            
            response = session.post(
                f"{server}{endpoint}", 
                data=alt_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  Alternative field names worked!")
                data = response.json()
                token = data.get('access_token') or data.get('token')
                if token:
                    print(f"  Token received: {token[:20]}...")
                    return test_token(session, server, token)
                    
        except Exception as e:
            print(f"   Alt fields error: {e}")
        
        # Method 3: Try JSON with different structure
        try:
            print("   Trying nested JSON structure...")
            nested_data = {
                "user": {
                    "username": username,
                    "password": password
                }
            }
            
            response = session.post(
                f"{server}{endpoint}", 
                json=nested_data,
                timeout=10
            )
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   Nested structure worked!")
                data = response.json()
                token = data.get('access_token') or data.get('token')
                if token:
                    print(f"  Token received: {token[:20]}...")
                    return test_token(session, server, token)
                    
        except Exception as e:
            print(f"   Nested JSON error: {e}")
    
    return False

def test_token(session, server, token):
    """
    Test if the token works for accessing protected endpoints.
    """
    print(f"\n Testing token...")
    
    # Set up authenticated session
    session.headers.update({
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    })
    
    try:
        response = session.get(f"{server}/v3/projects", timeout=10)
        print(f" GET /v3/projects: {response.status_code}")
        
        if response.status_code == 200:
            projects = response.json()
            print(f" SUCCESS! Found {len(projects)} projects")
            
            for project in projects:
                print(f"   - {project.get('name', 'Unnamed')} ({project.get('project_id', 'No ID')})")
            
            return True
        else:
            print(f" Token doesn't work: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f" Error testing token: {e}")
        return False

def try_basic_auth_on_projects():
    """
    Try basic auth directly on projects endpoint.
    """
    print(f"\n Trying basic auth directly on projects...")
    
    server = "http://127.0.0.1:3080"
    session = requests.Session()
    session.verify = False
    session.auth = ('admin', 'admin')
    
    try:
        response = session.get(f"{server}/v3/projects", timeout=10)
        print(f" Status: {response.status_code}")
        
        if response.status_code == 200:
            projects = response.json()
            print(f" Basic auth works! Found {len(projects)} projects")
            return True
        else:
            print(f" Basic auth failed: {response.text}")
            return False
            
    except Exception as e:
        print(f" Basic auth error: {e}")
        return False

def check_if_auth_disabled():
    """
    Check if authentication might be completely disabled.
    """
    print(f"\n Checking if authentication is disabled...")
    
    server = "http://127.0.0.1:3080"
    session = requests.Session()
    session.verify = False
    
    # Try accessing projects without any authentication
    try:
        response = session.get(f"{server}/v3/projects", timeout=5)
        print(f" No-auth status: {response.status_code}")
        
        if response.status_code == 200:
            projects = response.json()
            print(f" AUTHENTICATION IS DISABLED! Found {len(projects)} projects")
            print("You can access the API without authentication!")
            return True
        else:
            print(f" Authentication is required: {response.text}")
            return False
            
    except Exception as e:
        print(f" Error: {e}")
        return False

def create_project_no_auth():
    """
    Try to create a project without authentication.
    """
    print(f"\n Trying to create project without authentication...")
    
    server = "http://127.0.0.1:3080"
    session = requests.Session()
    session.verify = False
    
    project_data = {
        "name": "Test Automation Project",
        "auto_close": True,
        "auto_open": False,
        "auto_start": False
    }
    
    try:
        response = session.post(f"{server}/v3/projects", json=project_data, timeout=15)
        print(f" Status: {response.status_code}")
        
        if response.status_code == 201:
            project = response.json()
            project_id = project.get('project_id')
            print(f" SUCCESS! Project created without authentication!")
            print(f" Project ID: {project_id}")
            print(f" Project Name: {project.get('name')}")
            return project_id
        else:
            print(f" Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f" Error: {e}")
        return None

def main():
    """
    Main function to try all authentication methods.
    """
    print(" Complete GNS3 Authentication Test")
    print("=" * 50)
    
    # Step 1: Check if auth is disabled
    if check_if_auth_disabled():
        print(f"\n GREAT NEWS! Authentication is disabled!")
        print(f"You can use the API directly without any authentication.")
        
        # Try to create a project
        project_id = create_project_no_auth()
        if project_id:
            print(f"\n You're all set! Use this new project ID: {project_id}")
        
        return
    
    # Step 2: Try OAuth2 format
    if try_oauth2_format():
        print(f"\n OAuth2 authentication working!")
        return
    
    # Step 3: Try basic auth
    if try_basic_auth_on_projects():
        print(f"\n Basic authentication working!")
        return

  

if __name__ == "__main__":
    main()