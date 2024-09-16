import json
import logging

def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            logging.info("Loaded config.json successfully")
            return config
    except FileNotFoundError as e:
        logging.error(f"config.json not found: {e}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding config.json: {e}")
        return {}
