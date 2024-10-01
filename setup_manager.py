import os
import subprocess
import logging

class SetupManager:
    """
    Handles initial setup, path validation, and dependency checks.
    Ensures that adb, fastboot, and other binaries are accessible.
    """

    required_binaries = {
        "adb": "adb.exe",
        "fastboot": "fastboot.exe"
    }

    def __init__(self, tool_paths):
        self.tool_paths = tool_paths

    def validate_setup(self):
        for tool_name, tool_path in self.tool_paths.items():
            if not os.path.exists(tool_path):
                logging.error(f"{tool_name} not found at path: {tool_path}")
                raise FileNotFoundError(f"{tool_name} not found at path: {tool_path}")
            else:
                logging.info(f"{tool_name} found at path: {tool_path}")

    @staticmethod
    def check_adb_devices():
        """
        Checks if a device is connected using adb.
        """
        try:
            result = subprocess.check_output([SetupManager.required_binaries['adb'], "devices"]).decode()
            logging.info(f"Connected devices: \n{result}")
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"Error checking connected devices: {e}")
            return None