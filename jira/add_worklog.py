# add_worklog.py
import requests
import json
import logging
from datetime import datetime, timezone
from config import JiraConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JiraWorklogManager:
    def __init__(self):
        self.config = JiraConfig()

    def add_worklog(self, issue_key, comment, time_spent_seconds, visibility=None):
        url = f"{self.config.JIRA_URL}/rest/api/2/issue/{issue_key}/worklog"

        if not isinstance(time_spent_seconds, int) or time_spent_seconds <= 0:
            raise ValueError("time_spent_seconds must be a positive integer")

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

        try:
            response = requests.post(
                url,
                data=json.dumps(payload),
                headers=self.config.HEADERS
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error adding worklog to {issue_key}: {str(e)}")
            return None

if __name__ == "__main__":
    jira_manager = JiraWorklogManager()
    issue_key = "BTP-2"  # Replace with your actual issue key

    try:
        # Example with group visibility
        worklog_group = jira_manager.add_worklog(
            issue_key,
            f"Working on issue {issue_key}",
            12000,  # 3 hours and 20 minutes in seconds
            {"type": "group", "value": "fa2ee2a7-fc1f-49ad-a7d2-34e24c056377"}
        )

        # Example with role visibility
        worklog_role = jira_manager.add_worklog(
            issue_key,
            f"Working on issue {issue_key}",
            7200,  # 2 hours in seconds
            {"type": "role", "value": "Administrators"}
        )

        # Example without visibility restrictions
        worklog_no_visibility = jira_manager.add_worklog(
            issue_key,
            f"Working on issue {issue_key}",
            3600,  # 1 hour in seconds
        )

        # Print the responses
        for worklog, description in [
            (worklog_group, "Worklog with group visibility"),
            (worklog_role, "Worklog with role visibility"),
            (worklog_no_visibility, "Worklog without visibility restrictions")
        ]:
            if worklog:
                print(f"\n{description}:")
                print(json.dumps(worklog, sort_keys=True, indent=4, separators=(",", ": ")))
            else:
                print(f"\n{description}: Failed to add worklog")

    except ValueError as e:
        logger.error(f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
