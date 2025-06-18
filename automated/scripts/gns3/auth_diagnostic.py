"""
GNS3 Network Authentication:
All HTTP codes are here:https://umbraco.com/knowledge-base/http-status-codes/
This file:
 prove if the http://127.0.0.1:3080 is works with Auth.
Based on the OAuth2PasswordBearer requirement from  API docs is the best way to prove it.
"""
##################################
#Imports
##################################
import requests
import json
from urllib.parse import urlencode

def try_oauth2_format():
    """
    Try OAuth2 password bearer format (form data instead of JSON).
    """
    print(" Trying OAuth2 Password:")

    #default values from API
    server = "http://127.0.0.1:3080"
    username = "admin"
    password = "admin"
    #Request
    session = requests.Session()
    session.verify = False
    
    # OAuth2 typically expects form data, not JSON
    auth_data = {
        "username": username, #admin
        "password": password #admin
    }
    # Get endpoints 
    endpoints_to_try = [
        "/v3/access/users/login",
        "/v3/access/users/authenticate"
    ]
    #Testing for cicle
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
            #code== 200:OK Works open 2xx Succesful!
            if response.status_code == 200:
                print(f" Form data worked! 200:OK ")
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
            #code== 422 4xx Client Error!        
            elif response.status_code == 422:
                print(f"   Still 422  Client Error: {response.text}")
            else:
                print(f"   Status Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   Error: {e}")

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

def main():
    """
    Main function to try all authentication methods.
    """
    print(" Complete GNS3 Authentication Test")
    print("=" * 50)
    
    # Step 2: Try OAuth2 format
    if try_oauth2_format():
        print(f"\n OAuth2 authentication working!")
        return
    

if __name__ == "__main__":
    main()