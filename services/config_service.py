import json
from pathlib import Path

FILE = Path(__file__).parent.parent / 'config' / 'filters_config.json'

# Load the filter configuration from the JSON file
def load_filter_config(config_file=FILE):
    with open(config_file) as f:
        return json.load(f)
