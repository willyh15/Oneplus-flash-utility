import json
import logging

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self):
        """Load the configuration from the specified JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                logging.info(f"Loaded {self.config_file} successfully.")
                return config
        except FileNotFoundError:
            logging.warning(f"{self.config_file} not found. Creating a new default config.")
            default_config = {
                "oneplus7pro": {
                    "twrp": "https://dl.twrp.me/guacamoleb/twrp-3.3.1-1-guacamoleb.img",
                    "magisk": "https://github.com/topjohnwu/Magisk/releases/latest"
                }
            }
            self.save_config(default_config)
            return default_config
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding {self.config_file}: {e}")
            return {}

    def save_config(self, config_data=None):
        """Save the current or provided configuration to the file."""
        try:
            config_to_save = config_data if config_data else self.config_data
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=4)
                logging.info(f"Configuration saved to {self.config_file}.")
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")

    def update_config(self, section, key, value):
        """Update a specific configuration value and save."""
        if section in self.config_data:
            self.config_data[section][key] = value
            self.save_config()
            logging.info(f"Updated {section} -> {key} to {value} in configuration.")
        else:
            logging.warning(f"Section {section} not found in configuration.")

    def get_config_value(self, section, key):
        """Retrieve a specific configuration value."""
        return self.config_data.get(section, {}).get(key, None)

    def reload_config(self):
        """Reload the configuration file to apply changes dynamically."""
        self.config_data = self.load_config()
        logging.info("Configuration reloaded.")
