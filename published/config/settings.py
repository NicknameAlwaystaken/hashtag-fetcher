import json

def save_settings(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file)

def load_settings(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}  # Return an empty dict if the file doesn't exist
