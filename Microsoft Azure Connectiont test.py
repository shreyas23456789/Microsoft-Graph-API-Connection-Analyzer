import requests
import json
import os
import time
import base64
from datetime import datetime

def graph_api_connection_analyzer():
    """
    A comprehensive Microsoft Graph API connection testing utility.
    Takes user credentials and performs multiple tests to analyze connection capabilities.
    """
    print("\n" + "=" * 70)
    print("MICROSOFT GRAPH API CONNECTION ANALYZER".center(70))
    print("=" * 70)
    print("This utility tests your Microsoft Graph API connection capabilities")
    print("and provides detailed information about what your connection can access.")
    print("-" * 70)
    
    # Get user input for necessary credentials
    tenant_id = input("Enter your Azure AD Tenant ID: ")
    client_id = input("Enter your Application (client) ID: ")
    client_secret = input("Enter your Client Secret: ")
    
    # Initialize results dictionary
    results = {
        "authentication": {"status": "Not tested", "details": []},
        "directory": {"status": "Not tested", "details": []},
        "files": {"status": "Not tested", "details": []},
        "mail": {"status": "Not tested", "details": []},
        "users": {"status": "Not tested", "details": []},
        "groups": {"status": "Not tested", "details": []},
        "sites": {"status": "Not tested", "details": []},
        "teams": {"status": "Not tested", "details": []},
        "permissions": []
    }
    
    # Endpoints
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    graph_endpoint = "https://graph.microsoft.com/v1.0/"
    
    # Step 1: Authentication Test
    print("\n🔑 TESTING AUTHENTICATION...")
    
    # Get access token
    token_data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default'
    }
    
    try:
        token_response = requests.post(token_url, data=token_data)
        
        if token_response.status_code == 200:
            token_json = token_response.json()
            access_token = token_json.get('access_token')
            expires_in = token_json.get('expires_in', 'Unknown')
            token_type = token_json.get('token_type', 'Unknown')
            
            results["authentication"]["status"] = "Success"
            results["authentication"]["details"].append(f"Token type: {token_type}")
            results["authentication"]["details"].append(f"Expires in: {expires_in} seconds")
            
            # Extract scopes from token if possible
            try:
                # Parse token parts (JWT format: header.payload.signature)
                token_parts = access_token.split('.')
                if len(token_parts) >= 2:
                    # Add padding if needed
                    payload = token_parts[1]
                    padding = '=' * (4 - len(payload) % 4)
                    payload_data = json.loads(base64.b64decode(payload + padding).decode('utf-8'))
                    
                    # Extract roles (app permissions)
                    if 'roles' in payload_data:
                        roles = payload_data['roles']
                        results["permissions"] = roles
                        results["authentication"]["details"].append(f"Application has {len(roles)} role(s)")
                    
                    # Extract additional useful info
                    if 'app_displayname' in payload_data:
                        results["authentication"]["details"].append(f"App name: {payload_data['app_displayname']}")
                    if 'aud' in payload_data:
                        results["authentication"]["details"].append(f"Audience: {payload_data['aud']}")
            except Exception as e:
                results["authentication"]["details"].append(f"Could not parse token payload: {str(e)}")
            
            print("✅ Authentication successful")
            
            # Create headers for subsequent requests
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Step 2: Test service root (minimal permissions needed)
            print("\n🌐 TESTING SERVICE ROOT ACCESS...")
            try:
                service_root_response = requests.get(graph_endpoint, headers=headers)
                if service_root_response.status_code == 200:
                    print("✅ Service root access successful")
                    endpoints = service_root_response.json().get('value', [])
                    endpoint_count = len(endpoints)
                    
                    # Count types of endpoints
                    entity_sets = [e for e in endpoints if e.get('kind') == 'EntitySet']
                    singletons = [e for e in endpoints if e.get('kind') == 'Singleton']
                    
                    results["authentication"]["details"].append(f"Available endpoints: {endpoint_count} total ({len(entity_sets)} EntitySets, {len(singletons)} Singletons)")
                else:
                    print(f"❌ Service root access failed: {service_root_response.status_code} - {service_root_response.reason}")
            except Exception as e:
                print(f"❌ Service root access error: {str(e)}")
            
            # Step 3: Test Directory capabilities
            print("\n📁 TESTING DIRECTORY ACCESS...")
            
            # Test Organization endpoint
            try:
                org_response = requests.get(f"{graph_endpoint}organization", headers=headers)
                if org_response.status_code == 200:
                    org_data = org_response.json().get('value', [])
                    results["directory"]["status"] = "Available"
                    results["directory"]["details"].append(f"Organization data accessible ({len(org_data)} organizations)")
                    print("✅ Organization data accessible")
                else:
                    results["directory"]["status"] = "Limited"
                    results["directory"]["details"].append(f"Organization data not accessible ({org_response.status_code})")
                    print(f"❌ Organization data not accessible: {org_response.status_code}")
            except Exception as e:
                results["directory"]["details"].append(f"Organization data error: {str(e)}")
                print(f"❌ Organization data error: {str(e)}")
            
            # Test Directory Objects
            try:
                dir_response = requests.get(f"{graph_endpoint}directoryObjects", headers=headers)
                if dir_response.status_code == 200:
                    results["directory"]["details"].append("Directory objects accessible")
                    print("✅ Directory objects accessible")
                else:
                    results["directory"]["details"].append(f"Directory objects not accessible ({dir_response.status_code})")
                    print(f"❌ Directory objects not accessible: {dir_response.status_code}")
            except Exception as e:
                results["directory"]["details"].append(f"Directory objects error: {str(e)}")
                print(f"❌ Directory objects error: {str(e)}")
            
            # Step 4: Test Users capabilities
            print("\n👤 TESTING USERS ACCESS...")
            try:
                users_response = requests.get(f"{graph_endpoint}users?$top=5", headers=headers)
                if users_response.status_code == 200:
                    user_data = users_response.json().get('value', [])
                    results["users"]["status"] = "Available"
                    results["users"]["details"].append(f"Users data accessible (sample of {len(user_data)} users)")
                    print(f"✅ Users data accessible (sample of {len(user_data)} users)")
                else:
                    results["users"]["status"] = "Limited"
                    results["users"]["details"].append(f"Users data not accessible ({users_response.status_code})")
                    print(f"❌ Users data not accessible: {users_response.status_code}")
            except Exception as e:
                results["users"]["details"].append(f"Users data error: {str(e)}")
                print(f"❌ Users data error: {str(e)}")
            
            # Step 5: Test Groups capabilities
            print("\n👥 TESTING GROUPS ACCESS...")
            try:
                groups_response = requests.get(f"{graph_endpoint}groups?$top=5", headers=headers)
                if groups_response.status_code == 200:
                    group_data = groups_response.json().get('value', [])
                    results["groups"]["status"] = "Available"
                    results["groups"]["details"].append(f"Groups data accessible (sample of {len(group_data)} groups)")
                    print(f"✅ Groups data accessible (sample of {len(group_data)} groups)")
                else:
                    results["groups"]["status"] = "Limited"
                    results["groups"]["details"].append(f"Groups data not accessible ({groups_response.status_code})")
                    print(f"❌ Groups data not accessible: {groups_response.status_code}")
            except Exception as e:
                results["groups"]["details"].append(f"Groups data error: {str(e)}")
                print(f"❌ Groups data error: {str(e)}")
            
            # Step 6: Test Files capabilities
            print("\n📄 TESTING FILES ACCESS...")
            # Test Drives
            try:
                drives_response = requests.get(f"{graph_endpoint}drives", headers=headers)
                if drives_response.status_code == 200:
                    drive_data = drives_response.json().get('value', [])
                    results["files"]["status"] = "Available"
                    results["files"]["details"].append(f"Drives accessible ({len(drive_data)} drives)")
                    print(f"✅ Drives accessible ({len(drive_data)} drives)")
                else:
                    results["files"]["status"] = "Limited"
                    results["files"]["details"].append(f"Drives not accessible ({drives_response.status_code})")
                    print(f"❌ Drives not accessible: {drives_response.status_code}")
            except Exception as e:
                results["files"]["details"].append(f"Drives error: {str(e)}")
                print(f"❌ Drives error: {str(e)}")
            
            # Step 7: Test SharePoint/Sites capabilities
            print("\n🌐 TESTING SHAREPOINT SITES ACCESS...")
            try:
                sites_response = requests.get(f"{graph_endpoint}sites", headers=headers)
                if sites_response.status_code == 200:
                    site_data = sites_response.json().get('value', [])
                    results["sites"]["status"] = "Available"
                    results["sites"]["details"].append(f"SharePoint sites accessible ({len(site_data)} sites)")
                    print(f"✅ SharePoint sites accessible ({len(site_data)} sites)")
                else:
                    results["sites"]["status"] = "Limited"
                    results["sites"]["details"].append(f"SharePoint sites not accessible ({sites_response.status_code})")
                    print(f"❌ SharePoint sites not accessible: {sites_response.status_code}")
            except Exception as e:
                results["sites"]["details"].append(f"SharePoint sites error: {str(e)}")
                print(f"❌ SharePoint sites error: {str(e)}")
            
            # Step 8: Test Mail capabilities
            print("\n✉️ TESTING MAIL ACCESS...")
            try:
                # Try to access shared mailboxes (application permission)
                mail_response = requests.get(f"{graph_endpoint}users?$filter=mail ne null&$select=id,displayName,mail&$top=5", headers=headers)
                if mail_response.status_code == 200:
                    mail_users = mail_response.json().get('value', [])
                    results["mail"]["status"] = "Available"
                    results["mail"]["details"].append(f"Mail users accessible ({len(mail_users)} users with mail)")
                    print(f"✅ Mail users accessible ({len(mail_users)} users with mail)")
                    
                    # Try to access a mailbox if users were found
                    if mail_users:
                        user_id = mail_users[0].get('id')
                        mailbox_response = requests.get(f"{graph_endpoint}users/{user_id}/messages?$top=5", headers=headers)
                        if mailbox_response.status_code == 200:
                            results["mail"]["details"].append("Mailbox content accessible")
                            print("✅ Mailbox content accessible")
                        else:
                            results["mail"]["details"].append(f"Mailbox content not accessible ({mailbox_response.status_code})")
                            print(f"❌ Mailbox content not accessible: {mailbox_response.status_code}")
                else:
                    results["mail"]["status"] = "Limited"
                    results["mail"]["details"].append(f"Mail users not accessible ({mail_response.status_code})")
                    print(f"❌ Mail users not accessible: {mail_response.status_code}")
            except Exception as e:
                results["mail"]["details"].append(f"Mail access error: {str(e)}")
                print(f"❌ Mail access error: {str(e)}")
            
            # Step 9: Test Teams capabilities
            print("\n👥 TESTING TEAMS ACCESS...")
            try:
                teams_response = requests.get(f"{graph_endpoint}teams", headers=headers)
                if teams_response.status_code == 200:
                    teams_data = teams_response.json().get('value', [])
                    results["teams"]["status"] = "Available"
                    results["teams"]["details"].append(f"Teams accessible ({len(teams_data)} teams)")
                    print(f"✅ Teams accessible ({len(teams_data)} teams)")
                else:
                    results["teams"]["status"] = "Limited"
                    results["teams"]["details"].append(f"Teams not accessible ({teams_response.status_code})")
                    print(f"❌ Teams not accessible: {teams_response.status_code}")
            except Exception as e:
                results["teams"]["details"].append(f"Teams error: {str(e)}")
                print(f"❌ Teams error: {str(e)}")
            
        else:
            results["authentication"]["status"] = "Failed"
            results["authentication"]["details"].append(f"Status code: {token_response.status_code}")
            results["authentication"]["details"].append(f"Error: {token_response.text}")
            print(f"❌ Authentication failed: {token_response.status_code} - {token_response.reason}")
            print(f"Error details: {token_response.text}")
    
    except Exception as e:
        results["authentication"]["status"] = "Error"
        results["authentication"]["details"].append(f"Exception: {str(e)}")
        print(f"❌ Authentication error: {str(e)}")
    
    # Generate summary report
    print("\n" + "=" * 70)
    print("MICROSOFT GRAPH API CONNECTION SUMMARY".center(70))
    print("=" * 70)
    
    print(f"\nAuthentication: {results['authentication']['status']}")
    
    # Count available services
    available_services = sum(1 for k, v in results.items() if k != 'authentication' and k != 'permissions' and v['status'] == 'Available')
    limited_services = sum(1 for k, v in results.items() if k != 'authentication' and k != 'permissions' and v['status'] == 'Limited')
    
    print(f"\nServices Access Summary:")
    print(f"✅ Available: {available_services}")
    print(f"⚠️ Limited: {limited_services}")
    print(f"❌ Inaccessible: {7 - available_services - limited_services}")
    
    # Print detailed results for each service
    print("\nDetailed Access Report:")
    for service, info in results.items():
        if service != 'authentication' and service != 'permissions':
            status_icon = "✅" if info["status"] == "Available" else "❌"
            print(f"\n{status_icon} {service.upper()}: {info['status']}")
            for detail in info["details"]:
                print(f"   - {detail}")
    
    # Permission recommendations
    print("\n" + "=" * 70)
    print("PERMISSIONS RECOMMENDATIONS".center(70))
    print("=" * 70)
    
    # Based on failed tests, recommend permissions
    if results["directory"]["status"] != "Available":
        print("• To access organization data: Add 'Organization.Read.All' permission")
        print("• To access directory objects: Add 'Directory.Read.All' permission")
    
    if results["users"]["status"] != "Available":
        print("• To access user data: Add 'User.Read.All' permission")
    
    if results["groups"]["status"] != "Available":
        print("• To access groups: Add 'Group.Read.All' permission")
    
    if results["files"]["status"] != "Available":
        print("• To access files and drives: Add 'Files.Read.All' permission")
    
    if results["sites"]["status"] != "Available":
        print("• To access SharePoint sites: Add 'Sites.Read.All' permission")
    
    if results["mail"]["status"] != "Available":
        print("• To access mailboxes: Add 'Mail.Read' permission")
    
    if results["teams"]["status"] != "Available":
        print("• To access teams: Add 'Team.ReadBasic.All' permission")
    
    print("\nNote: After adding permissions, an admin must grant consent in the Azure portal")
    
    # Write report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"graph_api_report_{timestamp}.txt"
    
    try:
        with open(report_filename, "w") as f:
            f.write("MICROSOFT GRAPH API CONNECTION REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("AUTHENTICATION:\n")
            f.write(f"Status: {results['authentication']['status']}\n")
            for detail in results['authentication']['details']:
                f.write(f"- {detail}\n")
            
            f.write("\nSERVICE ACCESS SUMMARY:\n")
            for service, info in results.items():
                if service != 'authentication' and service != 'permissions':
                    f.write(f"{service.upper()}: {info['status']}\n")
                    for detail in info["details"]:
                        f.write(f"- {detail}\n")
                    f.write("\n")
            
            f.write("\nPERMISSIONS:\n")
            if results["permissions"]:
                for perm in results["permissions"]:
                    f.write(f"- {perm}\n")
            else:
                f.write("No permissions detected in token\n")
        
        print(f"\nDetailed report saved to: {report_filename}")
    
    except Exception as e:
        print(f"\nCould not save report to file: {str(e)}")
    
    print("\n" + "=" * 70)
    print("THANK YOU FOR USING THE GRAPH API CONNECTION ANALYZER".center(70))
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    graph_api_connection_analyzer()