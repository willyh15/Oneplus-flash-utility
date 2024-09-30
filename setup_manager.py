import os
import subprocess
import logging

class SetupManager:
    ADB_PATH = "C:/Users/willh/Downloads/platform-tools-latest-windows/platform-tools/adb.exe"
    FASTBOOT_PATH = "C:/Users/willh/Downloads/platform-tools-latest-windows/platform-tools/fastboot.exe"

    @staticmethod
    def is_adb_available():
        """Check if ADB is available at the specified path."""
        if not os.path.isfile(SetupManager.ADB_PATH):
            logging.error(f"ADB not found at {SetupManager.ADB_PATH}")
            return False
        return True

    @staticmethod
    def is_fastboot_available():
        """Check if Fastboot is available at the specified path."""
        if not os.path.isfile(SetupManager.FASTBOOT_PATH):
            logging.error(f"Fastboot not found at {SetupManager.FASTBOOT_PATH}")
            return False
        return True

    @staticmethod
    def check_dependencies():
        """Check all critical dependencies and return a status message."""
        adb_status = "Available" if SetupManager.is_adb_available() else "Missing"
        fastboot_status = "Available" if SetupManager.is_fastboot_available() else "Missing"

        logging.info(f"Dependency check: ADB={adb_status}, Fastboot={fastboot_status}")
        return adb_status, fastboot_status

    @staticmethod
    def configure_paths():
        """Provide a guided setup for configuring missing paths."""
        print("ADB or Fastboot not found. Please enter the correct paths for these tools.")
        SetupManager.ADB_PATH = input("Enter the full path to adb.exe: ").strip()
        SetupManager.FASTBOOT_PATH = input("Enter the full path to fastboot.exe: ").strip()

        # Update paths in DeviceManager as well
        from device_manager import DeviceManager
        DeviceManager.ADB_PATH = SetupManager.ADB_PATH
        DeviceManager.FASTBOOT_PATH = SetupManager.FASTBOOT_PATH

        logging.info("Updated ADB and Fastboot paths in DeviceManager.")

    @staticmethod
    def initialize_environment():
        """Initialize environment and handle missing dependencies."""
        adb_status, fastboot_status = SetupManager.check_dependencies()
        if adb_status == "Missing" or fastboot_status == "Missing":
            logging.warning("Missing dependencies detected. Launching setup wizard...")
            SetupManager.configure_paths()
        else:
            logging.info("All dependencies are available.")
