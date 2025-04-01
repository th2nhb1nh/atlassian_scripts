# filter_jira_field_values.py
import json
import os
import argparse
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from services.jira_service import JiraService

def get_issues_with_non_empty_field(jira_service, field_name, project_key=None):
    """
    Get issues with a non-empty field using JQL.
    
    Args:
        jira_service: The JiraService instance
        field_name: The field to check (e.g., 'customfield_10001')
        project_key: Optional project key to limit results
        
    Returns:
        List of dictionaries with issue keys and field values
    """
    # Construct JQL query
    jql = f"{field_name} is not EMPTY"
    if project_key:
        jql = f"project = {project_key} AND {jql}"
    
    # Set up search parameters
    search_params = {
        "jql": jql,
        "fields": [field_name],
        "maxResults": 100
    }
    
    # Make the API request
    response = jira_service.post(
        jira_service._build_url("search"),
        json=search_params,
        headers=jira_service.headers
    )
    
    # Handle response
    if not response.ok:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []
    
    # Process results
    issues = response.json().get('issues', [])
    results = []
    
    for issue in issues:
        issue_key = issue.get('key')
        field_value = issue.get('fields', {}).get(field_name)
        
        if field_value:
            results.append({
                'issue_key': issue_key,
                'field_value': field_value
            })
            
    return results

def main():
    parser = argparse.ArgumentParser(description='Filter Jira issues with non-empty fields')
    parser.add_argument('field_name', help='Field name to check (e.g., customfield_10001)')
    parser.add_argument('--project', '-p', help='Limit to a specific project')
    parser.add_argument('--output', '-o', help='Save results to JSON file')
    parser.add_argument('--keys', '-k', action='store_true', help='Show issue keys in output')
    
    args = parser.parse_args()
    
    try:
        # Initialize JiraService
        jira_service = JiraService()
        
        print(f"Searching for issues with non-empty '{args.field_name}'...")
        results = get_issues_with_non_empty_field(
            jira_service, 
            args.field_name,
            project_key=args.project
        )
        
        # Display results
        print(f"\nFound {len(results)} issues with non-empty '{args.field_name}'\n")
        
        if results:
            print("Field values:")
            for i, item in enumerate(results, 1):
                if args.keys:
                    print(f"{i}. [{item['issue_key']}] {item['field_value']}")
                else:
                    print(f"{i}. {item['field_value']}")
        
        # Save results if requested
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {output_path}")
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()