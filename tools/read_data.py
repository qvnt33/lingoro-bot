import json


def load_data_from_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


data = load_data_from_json('./data.json')
