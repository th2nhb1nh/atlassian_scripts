import requests
import json
from datetime import datetime, timezone
from config import JiraConfig

class JiraWorklogManager:
    def __init__(self):
        self.config = JiraConfig()

    def add_worklog(self, issue_key, comment, time_spent_seconds, visibility=None):
        url = f"{self.config.JIRA_URL}/rest/api/2/issue/{issue_key}/worklog"

        payload = {
            "comment": comment,
            "started": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000+0000"),
            "timeSpentSeconds": time_spent_seconds
        }

        if visibility:
            if visibility['type'] not in ['group', 'role']:
                raise ValueError("Visibility type must be either 'group' or 'role'")
            
            payload["visibility"] = {
                "type": visibility['type'],
                "identifier" if visibility['type'] == 'group' else "value": visibility['value']
            }

        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=self.config.HEADERS
        )

        return response.json()

if __name__ == "__main__":
    jira_manager = JiraWorklogManager()

    # Specify the issue key you want to add the worklog to
    issue_key = "BTP-2"  # Replace with your actual issue key

    # Example with group visibility
    worklog_group = jira_manager.add_worklog(
        issue_key,
        "I did some work here (visible to a specific group).",
        12000,  # 3 hours and 20 minutes in seconds
        {"type": "group", "value": "fa2ee2a7-fc1f-49ad-a7d2-34e24c056377"}
    )

    # Example with role visibility
    worklog_role = jira_manager.add_worklog(
        issue_key,
        "I did some more work here (visible to a specific role).",
        7200,  # 2 hours in seconds
        {"type": "role", "value": "Administrators"}
    )

    # Example without visibility restrictions
    worklog_no_visibility = jira_manager.add_worklog(
        issue_key,
        "I did some public work here.",
        3600,  # 1 hour in seconds
    )

    # Print the responses
    print("Worklog with group visibility:")
    print(json.dumps(worklog_group, sort_keys=True, indent=4, separators=(",", ": ")))
    
    print("\nWorklog with role visibility:")
    print(json.dumps(worklog_role, sort_keys=True, indent=4, separators=(",", ": ")))
    
    print("\nWorklog without visibility restrictions:")
    print(json.dumps(worklog_no_visibility, sort_keys=True, indent=4, separators=(",", ": ")))
    