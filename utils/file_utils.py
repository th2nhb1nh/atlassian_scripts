# file_utils.py
import json
import csv
import os

def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"[INFO] Created directory: {directory}")

def read_csv(csv_path):
    try:
        with open(csv_path, mode='r', encoding='utf-8') as csv_file:
            data = list(csv.DictReader(csv_file))
        print(f"[INFO] Successfully read {len(data)} rows from {csv_path}")
        return data
    except FileNotFoundError:
        print(f"[ERROR] CSV file not found: {csv_path}")
        return []
    except csv.Error as e:
        print(f"[ERROR] Error reading CSV file {csv_path}: {e}")
        return []

def write_csv_to_file(file_path, data, fieldnames):
    ensure_directory_exists(file_path)
    try:
        with open(file_path, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"[SUCCESS] Successfully wrote {len(data)} rows to {file_path}")
        return True
    except IOError as e:
        print(f"[ERROR] Error writing CSV to {file_path}: {e}")
        return False

def read_json(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[INFO] Successfully read JSON data from {file_path}")
        return data
    except FileNotFoundError:
        print(f"[ERROR] JSON file not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Error decoding JSON from {file_path}: {e}")
        return None

def write_json_to_file(file_path, data):
    ensure_directory_exists(file_path)
    try:
        with open(file_path, mode='w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"[SUCCESS] Successfully wrote JSON data to {file_path}")
        return True
    except IOError as e:
        print(f"[ERROR] Error writing JSON to {file_path}: {e}")
        return False

def build_file_name(file_id, file_name):
    return f"{file_id}_{file_name}"
