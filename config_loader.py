import json
import logging
import os

DEFAULT_CONFIG = {
    "oneplus7pro": {
        "twrp": "https://dl.twrp.me/guacamoleb/twrp-3.3.1-1-guacamoleb.img",
        "magisk": "https://github.com/topjohnwu/Magisk/releases/latest",
    },
    "pixel5": {
        "twrp": "https://twrp.me/google/googlepixel5.html",
        "magisk": "https://github.com/topjohnwu/Magisk/releases/latest",
    },
}

CONFIG_FILE_PATH = "config.json"


def load_config(config_file=CONFIG_FILE_PATH):
    """
    Loads configuration from a JSON file, creating default config if not found.

    :param config_file: Path to the configuration file.
    :return: Dictionary containing configuration settings.
    """
    try:
        if not os.path.exists(config_file):
            logging.warning(f"{config_file} not found. Creating default config.")
            with open(config_file, "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            return DEFAULT_CONFIG

        with open(config_file, "r") as f:
            config = json.load(f)
            logging.info(f"Loaded {config_file} successfully.")
            return config

    except FileNotFoundError:
        logging.error(f"Configuration file {config_file} not found.")
        return DEFAULT_CONFIG

    except json.JSONDecodeError as e:
        logging.error(f"Error decoding {config_file}: {e}")
        return DEFAULT_CONFIG


def save_config(config, config_file=CONFIG_FILE_PATH):
    """
    Saves the configuration dictionary to a JSON file.

    :param config: Configuration dictionary to save.
    :param config_file: Path to the configuration file.
    """
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
            logging.info(f"Configuration saved to {config_file} successfully.")
    except Exception as e:
        logging.error(f"Failed to save config: {e}")
