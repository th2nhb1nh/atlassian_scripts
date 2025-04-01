# update_issue_descriptions.py
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import sys
import csv
import re

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from services.jira_service import JiraService

# Load environment variables
env_path = Path(project_root) / '.env'
load_dotenv(dotenv_path=str(env_path))

class JiraIssueUpdater:
    def __init__(self, scripts_dir_path):
        self.jira_service = JiraService()
        self.scripts_dir = Path(scripts_dir_path)
        
    def load_script_content(self, script_id):
        script_path = self.scripts_dir / f"{script_id}.groovy"
        try:
            with open(str(script_path), 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Script file not found: {script_path}")
            return ""

    def get_issue_summary(self, issue_key):
        issue_data = self.jira_service.get_issue(issue_key)
        return issue_data.get('fields', {}).get('summary', '')

    def extract_script_id(self, summary):
        # Pattern to match either "digits.txt" or "digits.txt:"
        match = re.match(r'^(\d+)\.txt(?::|$)', summary)
        if match:
            return match.group(1)
        return None

    def create_description(self, info_row, script_content):
        description = f"""
| Workflow Name| Transition ID| Transition Name| Conditions| Validators| Post functions|
| {info_row['Workflow Name']}| {info_row['Transition ID']}| {info_row['Transition Name']}| {info_row['Conditions']}| {info_row['Validators']}| {info_row['Post functions']}|

h3. Server-based script
{{code:groovy}}
{script_content}
{{code}}
"""
        return description

    def update_issue(self, issue_key, description):
        payload = {
            "fields": {
                "description": description
            }
        }
        return self.jira_service.update_issue(issue_key, payload)

def load_info_data(csv_path):
    info_data = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter=';')
            for row in csvreader:
                # Using scriptID as key
                info_data[row['scriptID']] = {k.strip(): v.strip() for k, v in row.items()}
    except FileNotFoundError:
        print(f"CSV file not found: {csv_path}")
        sys.exit(1)
    return info_data

def load_results_data(json_path):
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"JSON file not found: {json_path}")
        sys.exit(1)

def main():
    try:
        # Initialize paths
        info_csv_path = Path(project_root) / 'jira' / 'data' / 'info.csv'
        results_json_path = Path(project_root) / 'jira' / 'data' / 'output_results.json'
        
        # Specify the actual path to your scripts directory
        scripts_dir_path = "ProjectJira/Workflows"

        # Load data
        info_data = load_info_data(info_csv_path)
        results_data = load_results_data(results_json_path)

        # Initialize updater with scripts directory path
        jira_updater = JiraIssueUpdater(scripts_dir_path)

        # Process each issue
        for issue in results_data:
            issue_key = issue['key']
            
            # Get issue summary and extract script ID
            summary = jira_updater.get_issue_summary(issue_key)
            script_id = jira_updater.extract_script_id(summary)
            
            if not script_id:
                print(f"Could not extract script ID from summary for issue: {issue_key}")
                continue

            if script_id in info_data:
                # Load script content
                script_content = jira_updater.load_script_content(script_id)
                
                # Create new description
                new_description = jira_updater.create_description(info_data[script_id], script_content)
                
                # Update issue
                result = jira_updater.update_issue(issue_key, new_description)
                print(f"Updated issue: {issue_key} with script ID: {script_id}")
            else:
                print(f"No matching info found for script ID: {script_id} (Issue: {issue_key})")

        print("\nDescription updates completed successfully")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()