import json


def load_data_from_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


app_data = load_data_from_json('./data.json')
