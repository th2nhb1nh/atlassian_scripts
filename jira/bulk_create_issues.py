# bulk_create_issues.py
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import sys
import argparse

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from services.jira_service import JiraService
from utils.file_utils import read_json

# Load environment variables from project root
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

class JiraIssueCreator:
    def __init__(self, verbose=False):
        self.jira_service = JiraService()
        self.project_key = os.getenv('JIRA_PROJECT_KEY', 'BL2')
        self.issue_type = os.getenv('JIRA_ISSUE_TYPE', 'Task')
        self.verbose = verbose

    def create_issue(self, summary, description):
        if self.verbose:
            print(f"\nCreating issue with summary: {summary}")
            print(f"Description: {description}")
            print(f"Project: {self.project_key}")
            print(f"Issue Type: {self.issue_type}")

        payload = {
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": summary,
                "description": description,  # Changed to plain text
                "issuetype": {
                    "name": self.issue_type
                }
            }
        }
        
        result = self.jira_service.create_issue(payload)
        if self.verbose:
            print(f"API Response: {json.dumps(result, indent=2)}")
        return result

    def bulk_create_issues(self, issues_data):
        results = []
        if self.verbose:
            print(f"\nStarting bulk creation of {len(issues_data)} issues...")
        
        for i, issue in enumerate(issues_data, 1):
            if self.verbose:
                print(f"\nProcessing issue {i}/{len(issues_data)}")
            result = self.create_issue(issue["summary"], issue["description"])
            issue_key = result.get('key', 'Error')
            print(f"Created issue: {issue_key}")
            results.append(result)
        
        if self.verbose:
            print(f"\nBulk creation completed. Created {len(results)} issues.")
        return results

def load_issues_data(file_path=None):
    if file_path:
        return read_json(file_path)
    return [
        {
            "summary": "Implement OAuth 2.0 and OpenID Connect authentication",
            "description": "Integrate OAuth 2.0 with OpenID Connect to provide secure user authentication and authorization across microservices, ensuring compliance with industry security standards."
        },
        {
            "summary": "Design a scalable RBAC system",
            "description": "Develop a role-based access control (RBAC) system with fine-grained permissions, allowing dynamic assignment and enforcement of access rules across distributed services."
        },
        {
            "summary": "Develop API Gateway with JWT validation",
            "description": "Implement an API Gateway that enforces security policies, validates JWT tokens, and manages rate limiting to protect internal microservices from unauthorized access and DDoS attacks."
        },
        {
            "summary": "Implement centralized logging and monitoring",
            "description": "Set up an ELK or Loki stack to aggregate logs from all microservices, ensuring real-time visibility, anomaly detection, and incident response capabilities."
        },
        {
            "summary": "Enhance database security with encryption and access control",
            "description": "Implement data encryption at rest and in transit, enforce least privilege access policies, and configure database audit logging to detect unauthorized activities."
        },
        {
            "summary": "Optimize microservices communication with service mesh",
            "description": "Deploy a service mesh (e.g., Istio or Linkerd) to manage secure service-to-service communication, enforce mTLS, and apply dynamic traffic policies."
        },
        {
            "summary": "Implement rate limiting and API security policies",
            "description": "Configure rate limiting, API authentication, and security headers in the API Gateway to prevent abuse, unauthorized access, and injection attacks."
        },
        {
            "summary": "Develop a secrets management strategy",
            "description": "Integrate HashiCorp Vault or AWS Secrets Manager to securely store and manage credentials, API keys, and sensitive configurations across microservices."
        },
        {
            "summary": "Establish CI/CD security checks",
            "description": "Integrate security scanning tools into the CI/CD pipeline, enforcing dependency vulnerability checks, container image security validation, and infrastructure-as-code policy enforcement."
        },
        {
            "summary": "Build an automated compliance reporting system",
            "description": "Develop a system to generate compliance reports based on security policies, audit logs, and access control configurations, ensuring adherence to SOC 2, GDPR, and ISO 27001 standards."
        }
    ]

def main():
    try:
        # Set up argument parser
        parser = argparse.ArgumentParser(description='Bulk create Jira issues')
        parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
        parser.add_argument('json_file', nargs='?', help='Path to JSON file containing issues data')
        args = parser.parse_args()
        
        # Load issues data from file or use default data
        issues_data = load_issues_data(args.json_file)
        
        # Create and execute bulk creation
        jira_creator = JiraIssueCreator(verbose=args.verbose)
        results = jira_creator.bulk_create_issues(issues_data)
        
        # Save results to a file
        output_path = project_root / 'jira' / 'output_results.json'
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\nResults saved to: {output_path}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
