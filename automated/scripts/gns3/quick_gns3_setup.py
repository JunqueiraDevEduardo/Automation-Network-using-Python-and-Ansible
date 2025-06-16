#!/usr/bin/env python3
"""
Quick GNS3 Project Setup Script
This script helps you quickly create a new project and get the project ID
for use with your existing automation scripts.
"""

import requests
import json

def quick_setup():
    """
    Quick setup to create a new GNS3 project and get the ID.
    """
    print("🚀 Quick GNS3 Project Setup")
    print("=" * 40)
    
    # Server configuration
    server = "http://127.0.0.1:3080"
    username = "admin"
    password = "admin"
    
    # Create session with basic auth
    session = requests.Session()
    session.auth = (username, password)
    session.verify = False
    
    print(f"🔗 Connecting to: {server}")
    
    # Test connection first
    try:
        response = session.get(f"{server}/v3/version", timeout=5)
        if response.status_code == 200:
            version_info = response.json()
            print(f"✅ Connected to GNS3 v{version_info.get('version', 'Unknown')}")
        else:
            print(f"❌ Connection failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # List existing projects
    print("\n📋 Existing projects:")
    try:
        response = session.get(f"{server}/v3/projects", timeout=10)
        if response.status_code == 200:
            projects = response.json()
            if projects:
                for i, project in enumerate(projects, 1):
                    print(f"{i}. {project.get('name', 'Unnamed')} (ID: {project.get('project_id', 'Unknown')})")
                    print(f"   Status: {project.get('status', 'Unknown')}")
            else:
                print("   No existing projects found")
        else:
            print(f"   Failed to list projects: {response.status_code}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Ask user what they want to do
    print("\n🔧 What would you like to do?")
    print("1. Create a new project")
    print("2. Use existing project")
    print("3. Exit")
    
    choice = input("\n👉 Enter choice (1-3): ").strip()
    
    if choice == "1":
        # Create new project
        project_name = input("\n📝 Enter project name: ").strip()
        if not project_name:
            project_name = "Network Automation Project"
        
        print(f"\n🆕 Creating project: {project_name}")
        
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
                print(f"📋 Project Details:")
                print(f"   Name: {project.get('name')}")
                print(f"   ID: {project_id}")
                print(f"   Status: {project.get('status')}")
                
                # Open the project
                print(f"\n🔓 Opening project...")
                open_response = session.post(f"{server}/v3/projects/{project_id}/open", timeout=15)
                if open_response.status_code == 201:
                    print("✅ Project opened successfully!")
                else:
                    print(f"⚠️  Project created but couldn't open: {open_response.status_code}")
                
                # Provide instructions
                print(f"\n🎉 SUCCESS! Your new project is ready!")
                print(f"📝 Update your scripts with this project ID:")
                print(f"   {project_id}")
                
                print(f"\n💡 Next steps:")
                print(f"1. Copy the project ID above")
                print(f"2. Update your verify_existing_project.py script")
                print(f"3. Change the project_id variable to: {project_id}")
                print(f"4. Run your automation scripts")
                
                # Show code snippet to update
                print(f"\n📄 Code to update in verify_existing_project.py:")
                print(f"   Change line:")
                print(f"   project_id=\"9a8ab49a-6f61-4fa8-9089-99e6c6594e4f\"")
                print(f"   To:")
                print(f"   project_id=\"{project_id}\"")
                
            else:
                print(f"❌ Failed to create project: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating project: {e}")
    
    elif choice == "2":
        # Use existing project
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
                    
                    print(f"\n✅ Selected project: {selected_project.get('name')}")
                    print(f"📝 Project ID: {project_id}")
                    
                    # Try to open the project
                    try:
                        response = session.post(f"{server}/v3/projects/{project_id}/open", timeout=15)
                        if response.status_code == 201:
                            print("✅ Project opened successfully!")
                        elif response.status_code == 200:
                            print("✅ Project was already open!")
                        else:
                            print(f"⚠️  Couldn't open project: {response.status_code}")
                    except Exception as e:
                        print(f"⚠️  Error opening project: {e}")
                    
                    print(f"\n💡 Update your scripts with this project ID:")
                    print(f"   {project_id}")
                    
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid number")
        else:
            print("❌ No existing projects to select from")
    
    elif choice == "3":
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    quick_setup()