# bulk_create_issues.py
import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class JiraIssueCreator:
    def __init__(self):
        self.base_url = os.getenv('JIRA_URL')
        self.email = os.getenv('EMAIL')
        self.api_token = os.getenv('API_KEY')
        self.project_key = "BTOI"
        self.issue_type = "Task"

    def create_issue(self, summary, description):
        url = f"{self.base_url}/rest/api/3/issue"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        payload = json.dumps({
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "text": description,
                                    "type": "text"
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {
                    "name": self.issue_type
                }
            }
        })
        
        response = requests.post(
            url,
            data=payload,
            headers=headers,
            auth=(self.email, self.api_token)
        )
        
        return response.json()

    def bulk_create_issues(self, issues_data):
        for issue in issues_data:
            result = self.create_issue(issue["summary"], issue["description"])
            print(f"Created issue: {result.get('key', 'Error')}")
            print(result)

# Sample data for 10 issues
issues_data = [
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

if __name__ == "__main__":
    jira_creator = JiraIssueCreator()
    jira_creator.bulk_create_issues(issues_data)
