# file_utils.py
import json
import csv
import os

def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def read_csv(csv_path):
    with open(csv_path, mode='r', encoding='utf-8') as csv_file:
        return list(csv.DictReader(csv_file))

def write_csv_to_file(file_path, data, fieldnames):
    ensure_directory_exists(file_path)
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print("=======================\nOutput is successfully written to {} file.\n".format(file_path))

def read_json(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file {file_path}: {e}")
        return None

def write_json_to_file(file_path, data):
    ensure_directory_exists(file_path)
    try:
        with open(file_path, mode='w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("=======================\nOutput is successfully written to {} file.\n".format(file_path))
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")

def build_file_name(file_id, file_name):
    return f"{file_id}_{file_name}"
