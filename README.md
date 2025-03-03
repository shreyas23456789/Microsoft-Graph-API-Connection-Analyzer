# Microsoft Graph API Connection Analyzer

## Overview

The **Microsoft Graph API Connection Analyzer** is a Python-based utility designed to test and analyze your connection to the Microsoft Graph API. It provides insights into authentication capabilities and access to various Microsoft 365 services, such as users, groups, mail, files, sites, and Teams.

## Features

- **Authentication Testing**: Ensures that your credentials are valid and retrieves an access token.
- **Directory Access**: Checks if your connection can access organization and directory objects.
- **User Data Access**: Verifies access to user-related data.
- **Group Access**: Tests access to Microsoft 365 Groups.
- **File Access**: Evaluates permissions for accessing OneDrive and SharePoint files.
- **Mail Access**: Determines if mail-related operations are possible.
- **Teams Access**: Checks for permissions related to Microsoft Teams.
- **Permissions Analysis**: Extracts and displays granted application permissions.

## Prerequisites

Before using the script, ensure you have the following:

- Python 3.x installed on your machine.
- `requests` library installed (`pip install requests`).
- A registered Azure AD application with the necessary API permissions.
- Tenant ID, Client ID, and Client Secret from the Azure portal.

## Installation

1. Clone or download the script.
2. Open a terminal or command prompt and navigate to the script directory.
3. Install dependencies (if not already installed):
   ```sh
   pip install requests
   ```

## Usage

1. Run the script:
   ```sh
   Microsoft Azure Connection tester.py
   ```
2. Enter your Azure AD credentials when prompted:
   - **Tenant ID**
   - **Client ID**
   - **Client Secret**
3. The script will perform tests and display the results on the console.

## Expected Output

The script provides real-time updates on:

- Authentication success/failure.
- Access to Microsoft Graph API services.
- Detected permissions.
- Errors or issues encountered during execution.

## Troubleshooting

- Ensure that the Azure AD app has the correct permissions assigned.
- Check that your Client Secret has not expired.
- Verify your Tenant ID, Client ID, and Client Secret are correct.
- If authentication fails, check Azure AD logs for more details.

## License

This project is open-source and available for use under the MIT License.

## Author

Developed by **Shreyas Pravin Phatak**.

For questions or support, feel free to contact: shreyasphatak2928\@gmail.com.


