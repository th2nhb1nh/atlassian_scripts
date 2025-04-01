# bulk_create_issues_modified.py
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import sys
import csv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from services.jira_service import JiraService

# Load environment variables
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# Specify CSV file path directly
CSV_FILE_PATH = project_root / 'jira' / 'data' / 'issues.csv'

# Define the parent issue key under which sub-tasks will be created
PARENT_ISSUE_KEY = "AAA-17"

class JiraIssueCreator:
    def __init__(self):
        self.jira_service = JiraService()
        self.project_key = os.getenv('JIRA_PROJECT_KEY', 'AAA')
        self.issue_type = os.getenv('JIRA_ISSUE_TYPE', 'Sub-task')

    def create_sub_task(self, summary, labels):
        description = """
| Workflow Name| Transition ID| Transition Name| Conditions| Validators| Post functions|
| Coding workflow| 81| Ready to test| | | update Field = In Test: 9.txt|

h3. Server-based script
{code:groovy}

{code}
"""
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": self.issue_type},
                "parent": {"key": PARENT_ISSUE_KEY},  # Linking sub-task to AAA-17
                "labels": labels.split(',') if labels else []
            }
        }
        return self.jira_service.create_issue(payload)

    def bulk_create_sub_tasks(self, issues_data):
        results = []
        for issue in issues_data:
            result = self.create_sub_task(issue["summary"], issue.get("labels", ""))
            issue_key = result.get('key', 'Error')
            print(f"Created sub-task: {issue_key}")
            results.append(result)
        return results

def load_issues_data(csv_file_path):
    issues_data = []
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter=';')  # Explicitly set delimiter
            csvreader.fieldnames = [name.strip() for name in csvreader.fieldnames]  # Trim spaces
            
            for row in csvreader:
                summary = row.get("summary", "").strip()
                labels = row.get("labels", "").strip()
                
                if not summary:
                    print("Skipping issue creation: Missing summary")
                    continue  # Skip if summary is missing
                
                issues_data.append({"summary": summary, "labels": labels})
    except FileNotFoundError:
        print(f"CSV file not found: {csv_file_path}")
        sys.exit(1)
    except KeyError as e:
        print(f"Required column {e} not found in CSV file. Check column names.")
        sys.exit(1)
    return issues_data

def main():
    try:
        # Load issues data from the hardcoded file path
        issues_data = load_issues_data(CSV_FILE_PATH)
        
        # Create and execute bulk creation
        jira_creator = JiraIssueCreator()
        results = jira_creator.bulk_create_sub_tasks(issues_data)
        
        # Save results to a file
        output_path = project_root / 'jira' / 'data' / 'output_results.json'
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\nResults saved to: {output_path}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
