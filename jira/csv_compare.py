import pandas as pd

def compare_csv_files(file1_path, file2_path):
    # Read CSV files
    df1 = pd.read_csv(file1_path)
    df2 = pd.read_csv(file2_path)
    
    # Get unique IDs from both files
    ids_file1 = set(df1['id'])
    ids_file2 = set(df2['id'])
    
    # Find missing IDs in file2
    missing_in_file2 = ids_file1 - ids_file2
    
    # Print summary
    print(f"Total records in file1: {len(df1)}")
    print(f"Total records in file2: {len(df2)}")
    print(f"Unique IDs in file1: {len(ids_file1)}")
    print(f"Unique IDs in file2: {len(ids_file2)}")
    
    if missing_in_file2:
        print("\nIDs present in file1 but missing in file2:")
        for id in missing_in_file2:
            # Get the full record from file1 for this ID
            record = df1[df1['id'] == id].iloc[0]
            print(f"\nID: {id}")
            print(f"Name: {record['name']}")
            print(f"ClientKey: {record['clientKey']}")
            print(f"Path: {record['path']}")
    else:
        print("\nFile2 contains all IDs from file1")

# Replace these paths with your actual file paths
file1_path = "file1.csv"  # Original script result
file2_path = "file2.csv"          # Modified script result

compare_csv_files(file1_path, file2_path)