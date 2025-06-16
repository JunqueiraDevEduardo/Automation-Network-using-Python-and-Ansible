#!/usr/bin/env python3
"""
Simple GNS3 v3 Authentication and Project Creation
This script handles the authentication issue and creates a project for your automation.
"""

import requests
import json

def get_auth_token(server="http://127.0.0.1:3080", username="admin", password="admin"):
    """
    Get authentication token from GNS3 v3 API.
    """
    print("🔐 Getting authentication token...")
    
    session = requests.Session()
    session.verify = False
    
    # Try the correct login endpoint based on search results
    auth_url = f"{server}/v3/users/login"
    
    auth_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = session.post(auth_url, json=auth_data, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token') or data.get('token')
            if token:
                print("✅ Authentication token obtained!")
                return token
            else:
                print("❌ No token in response")
                return None
        else:
            print(f"❌ Auth failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return None

def create_authenticated_session(server, token):
    """
    Create authenticated session with token.
    """
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    })
    return session

def list_projects(session, server):
    """
    List all projects using authenticated session.
    """
    print("📋 Listing projects...")
    
    try:
        response = session.get(f"{server}/v3/projects", timeout=10)
        
        if response.status_code == 200:
            projects = response.json()
            print(f"✅ Found {len(projects)} projects:")
            
            for i, project in enumerate(projects, 1):
                print(f"{i}. {project.get('name', 'Unnamed')}")
                print(f"   ID: {project.get('project_id', 'Unknown')}")
                print(f"   Status: {project.get('status', 'Unknown')}")
                print()
            
            return projects
        else:
            print(f"❌ Failed to list projects: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error listing projects: {e}")
        return []

def create_project(session, server, project_name):
    """
    Create a new project using authenticated session.
    """
    print(f"🆕 Creating project: {project_name}")
    
    project_data = {
        "name": project_name,
        "auto_close": True,
        "auto_open": False,
        "auto_start": False
    }
    
    try:
        response = session.post(f"{server}/v3/projects", json=project_data, timeout=15)
        
        if response.status_code == 201:
            project = response.json()
            project_id = project.get('project_id')
            
            print(f"✅ Project created successfully!")
            print(f"   Name: {project.get('name')}")
            print(f"   ID: {project_id}")
            print(f"   Status: {project.get('status')}")
            
            return project_id
        else:
            print(f"❌ Failed to create project: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return None

def open_project(session, server, project_id):
    """
    Open a project using authenticated session.
    """
    print(f"🔓 Opening project: {project_id}")
    
    try:
        response = session.post(f"{server}/v3/projects/{project_id}/open", timeout=15)
        
        if response.status_code in [200, 201]:
            print("✅ Project opened successfully!")
            return True
        else:
            print(f"❌ Failed to open project: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error opening project: {e}")
        return False

def main():
    """
    Main function to authenticate and create/manage projects.
    """
    print("🚀 Simple GNS3 v3 Authentication & Project Manager")
    print("=" * 60)
    
    server = "http://127.0.0.1:3080"
    username = "admin"
    password = "admin"
    
    # Step 1: Get authentication token
    token = get_auth_token(server, username, password)
    if not token:
        print("\n❌ Authentication failed. Possible solutions:")
        print("1. Check if GNS3 server is running")
        print("2. Verify username/password (try: admin/admin)")
        print("3. Check if server is accessible at http://127.0.0.1:3080")
        print("4. Check GNS3 server logs for authentication errors")
        return
    
    # Step 2: Create authenticated session
    session = create_authenticated_session(server, token)
    
    # Step 3: List existing projects
    projects = list_projects(session, server)
    
    # Step 4: Ask user what to do
    print("🔧 What would you like to do?")
    print("1. Create a new project")
    print("2. Use an existing project")
    print("3. Exit")
    
    choice = input("\n👉 Enter choice (1-3): ").strip()
    
    if choice == "1":
        project_name = input("\n📝 Enter project name: ").strip()
        if not project_name:
            project_name = "Network Automation Project"
        
        project_id = create_project(session, server, project_name)
        if project_id:
            # Try to open the project
            open_project(session, server, project_id)
            
            print(f"\n🎉 SUCCESS!")
            print(f"📝 Your new project ID: {project_id}")
            print(f"\n💡 To use this project in your existing scripts:")
            print(f"1. Open: automated/scripts/gns3/verify_existing_project.py")
            print(f"2. Find the line: project_id=\"9a8ab49a-6f61-4fa8-9089-99e6c6594e4f\"")
            print(f"3. Replace with: project_id=\"{project_id}\"")
            print(f"4. Save the file and run your scripts")
    
    elif choice == "2":
        if projects:
            print("\n📋 Available projects:")
            for i, project in enumerate(projects, 1):
                print(f"{i}. {project.get('name', 'Unnamed')}")
                print(f"   ID: {project.get('project_id', 'Unknown')}")
                print(f"   Status: {project.get('status', 'Unknown')}")
                print()
            
            try:
                selection = int(input("👉 Select project number: ")) - 1
                if 0 <= selection < len(projects):
                    selected_project = projects[selection]
                    project_id = selected_project.get('project_id')
                    
                    print(f"\n✅ Selected: {selected_project.get('name')}")
                    print(f"📝 Project ID: {project_id}")
                    
                    # Try to open it
                    open_project(session, server, project_id)
                    
                    print(f"\n💡 To use this project in your scripts:")
                    print(f"Update your project_id to: {project_id}")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid number")
        else:
            print("❌ No projects available")
    
    elif choice == "3":
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()