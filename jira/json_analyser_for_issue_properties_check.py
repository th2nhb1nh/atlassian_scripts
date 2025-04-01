import json
import csv
import time

def traverse_and_search(json_data, search_string, results, root_path="root", parent=None):
    if isinstance(json_data, dict):
        # Check if current node is a "rule" and set it as parent
        if "id" in json_data and "clientKey" in json_data and "name" in json_data and "state" in json_data:
            parent = json_data  # Assign the current dictionary to parent

        found_in_current_node = False  # Flag to track if we found a match in current node
        
        for key, value in json_data.items():
            current_path = f"{root_path}.{key}"
            if isinstance(value, str) and search_string in value and not found_in_current_node:
                if parent and "state" in parent and parent["state"] == "ENABLED":
                    rule_id = parent.get("id", "Not Found")
                    rule_url = f"https://domain.atlassian.net/jira/settings/automation#/rule/{rule_id}"
                    result = {
                        "id": rule_id,
                        "clientKey": parent.get("clientKey", "Not Found"),
                        "name": parent.get("name", "Not Found"),
                        "state": parent.get("state", "Not Found"),
                        "authorAccountId": parent.get("authorAccountId", "Not Found"),
                        "description": parent.get("description", "Not Found"),
                        "path": current_path,
                        "url": rule_url
                    }
                    # Check if this result is already in the list
                    if not any(r["id"] == result["id"] for r in results):
                        results.append(result)
                        found_in_current_node = True  # Set flag to prevent further matches in this node
                        continue  # Skip further processing for this node
            
            if not found_in_current_node:  # Only traverse deeper if we haven't found a match
                traverse_and_search(value, search_string, results, current_path, parent)
                
    elif isinstance(json_data, list):
        for index, item in enumerate(json_data):
            current_path = f"{root_path}[{index}]"
            traverse_and_search(item, search_string, results, current_path, parent)

def search_and_extract(file_path, search_string, output_file="results.csv"):
    """
    Reads a JSON file, searches for the specified {{issue.properties.}} string, 
    extracts data from "ENABLED" rules, and writes the results to a CSV file.

    Args:
        file_path: Path to the JSON file.
        search_string: The string to search for within the JSON data.
        output_file: Name of the output CSV file (default: "results.csv").
    """
    try:
        # Open and load the JSON file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        results = []
        traverse_and_search(json_data, search_string, results)

        if results:
            # Write data to CSV file
            fieldnames = ["id", "clientKey", "name", "state", "authorAccountId", "description", "path", "url"]
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)

            print(f"Kết quả đã được lưu vào file {output_file}")
        else:
            print(f"Không tìm thấy kết quả nào.")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except json.JSONDecodeError:
        print(f"Error: File '{file_path}' is not a valid JSON file.")
    except UnicodeDecodeError as e:
        print(f"Error decoding file '{file_path}': {e}")

# Example usage:
file_path = "jira/data/automation-rules.json"  # Replace with your JSON file path
search_string = "issue.properties.\"proforma.forms."
timestr = time.strftime("%Y%m%d-%H%M%S")
output_file = f"jira/data/automation_enabled_{timestr}.csv"

search_and_extract(file_path, search_string, output_file)