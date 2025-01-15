import json

def compare_json_files(file1_path, file2_path, output_path):
    # Read file1
    with open(file1_path, 'r') as f1:
        data1 = json.load(f1)
    
    # Read file2
    with open(file2_path, 'r') as f2:
        data2 = json.load(f2)
    
    # Convert file2 data to a set of tuples for easier comparison
    # Using tuples because lists/dicts aren't hashable for sets
    data2_set = {(item['name'], item['groupId'], item['self']) for item in data2}
    
    # Find items in file1 that aren't in file2
    difference = [
        item for item in data1
        if (item['name'], item['groupId'], item['self']) not in data2_set
    ]
    
    # Write the difference to output file
    with open(output_path, 'w') as output:
        json.dump(difference, output, indent=4)
    
    return len(difference)

# Example usage:
file1_path = 'jira/data/file1.json'
file2_path = 'jira/data/file2.json'
output_path = 'jira/data/difference.json'

num_differences = compare_json_files(file1_path, file2_path, output_path)
print(f"Found {num_differences} items in {file1_path} that are not in {file2_path}")