import json
import logging

def load_config(config_file='config.json'):
    """
    Loads configuration from a JSON file.

    Args:
        config_file (str): The path to the configuration file (default: 'config.json').

    Returns:
        dict: The loaded configuration as a dictionary. Returns an empty dictionary if an error occurs.
    """
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            logging.info(f"Loaded {config_file} successfully.")
            return config
    except FileNotFoundError as e:
        logging.error(f"{config_file} not found: {e}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding {config_file}: {e}")
        return {}
