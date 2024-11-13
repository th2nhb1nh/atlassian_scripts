# bulk_create_issues.py
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from services.jira_service import JiraService
from utils.file_utils import read_json

# Load environment variables from project root
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

class JiraIssueCreator:
    def __init__(self):
        self.jira_service = JiraService()
        self.project_key = os.getenv('JIRA_PROJECT_KEY', 'BL2')
        self.issue_type = os.getenv('JIRA_ISSUE_TYPE', 'Task')

    def create_issue(self, summary, description):
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
        
        return self.jira_service.create_issue(payload)

    def bulk_create_issues(self, issues_data):
        results = []
        for issue in issues_data:
            result = self.create_issue(issue["summary"], issue["description"])
            issue_key = result.get('key', 'Error')
            print(f"Created issue: {issue_key}")
            results.append(result)
        return results

def load_issues_data(file_path=None):
    if file_path:
        return read_json(file_path)
    return [
    {"summary": "Implement user authentication", "description": "Set up secure user login and registration system"},
    {"summary": "Design database schema", "description": "Create efficient database structure for the application"},
    {"summary": "Develop API endpoints", "description": "Create RESTful API endpoints for frontend communication"},
    {"summary": "Implement error handling", "description": "Add robust error handling and logging mechanisms"},
    {"summary": "Create unit tests", "description": "Develop comprehensive unit tests for all major components"},
    {"summary": "Optimize database queries", "description": "Improve database query performance for faster responses"},
    {"summary": "Implement caching system", "description": "Set up caching to reduce server load and improve response times"},
    {"summary": "Develop user dashboard", "description": "Create an intuitive dashboard for users to manage their account"},
    {"summary": "Implement file upload feature", "description": "Add functionality for users to upload and manage files"},
    {"summary": "Create admin panel", "description": "Develop an admin panel for system management and monitoring"}
    ]

def main():
    try:
        # Check if a JSON file path is provided as command line argument
        json_file_path = sys.argv[1] if len(sys.argv) > 1 else None
        
        # Load issues data from file or use default data
        issues_data = load_issues_data(json_file_path)
        
        # Create and execute bulk creation
        jira_creator = JiraIssueCreator()
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
