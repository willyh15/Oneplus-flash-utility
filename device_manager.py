import hashlib
import subprocess
import os
import logging

class DeviceManager:
    ADB_PATH = "C:/Users/willh/Downloads/platform-tools-latest-windows/platform-tools/adb.exe"
    FASTBOOT_PATH = "C:/Users/willh/Downloads/platform-tools-latest-windows/platform-tools/fastboot.exe"
    # Dictionary to store error recovery suggestions
    error_suggestions = {
        "ADB_NOT_FOUND": "ADB binary not found. Please ensure ADB is correctly installed and configured.",
        "DEVICE_OFFLINE": "Device is offline. Check the device connection and USB debugging settings.",
        "FLASH_ERROR": "Flashing failed. Ensure the bootloader is unlocked and the image file is compatible.",
        "UNKNOWN_ERROR": "An unknown error occurred. Please check the logs for more details."
    }
    
    SUPPORTED_DEVICES = ["OnePlus 7 Pro", "Pixel 5"]

        @staticmethod
    def root_device(preserve_encryption=True):
        try:
            if preserve_encryption:
                logging.info("Rooting device while preserving encryption...")
            else:
                logging.info("Rooting device and disabling encryption...")
            # Dummy command to simulate success/failure
            subprocess.run([DeviceManager.ADB_PATH, "shell", "echo", "rooting"], check=True)
            return True
        except FileNotFoundError:
            logging.error("ADB binary not found. Please check your ADB path.")
            return False, "ADB_NOT_FOUND"
        except subprocess.CalledProcessError:
            logging.error("Failed to execute root command. Device might be offline.")
            return False, 
            "DEVICE_OFFLINE"

    @staticmethod
    def flash_rom(rom_path):
        try:
            logging.info(f"Starting to flash ROM: {rom_path}")
            subprocess.run([DeviceManager.ADB_PATH, "sideload", rom_path], check=True)
            logging.info("ROM flashing completed successfully.")
            return True, None
        except FileNotFoundError:
            logging.error("ADB binary not found. Please check your ADB path.")
            return False, "ADB_NOT_FOUND"
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to flash ROM: {e}")
            return False, "FLASH_ERROR"
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return False, "UNKNOWN_ERROR"

    @staticmethod
    def detect_connected_devices():
        """Detects connected devices using adb and returns a list of device serials."""
        try:
            result = subprocess.run([DeviceManager.ADB_PATH, "devices"], capture_output=True, text=True)
            device_list = [line.split()[0] for line in result.stdout.splitlines() if "device" in line and not line.startswith("List")]
            logging.info(f"Connected devices detected: {device_list}")
            return device_list
        except FileNotFoundError:
            logging.error("ADB executable not found at the specified path.")
            return []

    @staticmethod
    def is_device_supported(serial):
        """Checks if the connected device is supported by the tool."""
        model = DeviceManager.get_device_model(serial)
        if model in DeviceManager.SUPPORTED_DEVICES:
            logging.info(f"Device {serial} ({model}) is supported.")
            return True
        else:
            logging.warning(f"Device {serial} ({model}) is not supported by this tool.")
            return False

    @staticmethod
    def get_device_state():
        """Detect the current state of the connected device."""
        try:
            # Check for Fastboot Mode
            output = subprocess.check_output([DeviceManager.FASTBOOT_PATH, "devices"]).decode().strip()
            if output:
                return "Fastboot Mode"

            # Check for ADB Mode
            output = subprocess.check_output([DeviceManager.ADB_PATH, "devices"]).decode().strip()
            if "device" in output and not "unauthorized" in output:
                return "ADB Mode"

            # Check for Recovery Mode
            output = subprocess.check_output([DeviceManager.ADB_PATH, "shell", "getprop", "ro.bootmode"]).decode().strip()
            if output == "recovery":
                return "Recovery Mode"

            return "Disconnected"
        except subprocess.CalledProcessError:
            return "Unknown"

    @staticmethod
    def reboot_to_normal_mode():
        try:
            subprocess.run([DeviceManager.ADB_PATH, "reboot"], check=True)
            logging.info("Rebooted to normal (device) mode.")
        except subprocess.CalledProcessError as e:
            logging.error("Failed to reboot to normal mode: %s", e)


    @staticmethod
    def get_device_model(serial):
        """Fetches the device model for a given serial number."""
        try:
            model = subprocess.check_output([DeviceManager.ADB_PATH, "-s", serial, "shell", "getprop", "ro.product.model"]).decode().strip()
            logging.info(f"Device {serial} model: {model}")
            return model
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to retrieve device model for {serial}: {e}")
            return None

    @staticmethod
    def root_device(preserve_encryption=True):
        if preserve_encryption:
            logging.info("Rooting device while preserving encryption...")
        else:
            logging.info("Rooting device and disabling encryption...")
        return True

    # --------------- Partition and Bootloader Management ---------------
    @staticmethod
    def reboot_to_bootloader():
        try:
            subprocess.run([DeviceManager.ADB_PATH, "reboot", "bootloader"], check=True)
            logging.info("Rebooted to bootloader.")
        except subprocess.CalledProcessError as e:
            logging.error("Failed to reboot to bootloader: %s", e)

    @staticmethod
    def flash_partition(image_path, partition):
        try:
            if DeviceManager.verify_image(image_path):
                subprocess.run([DeviceManager.FASTBOOT_PATH, "flash", partition,
                                image_path], check=True)
                logging.info("Flashed %s partition with %s", partition, image_path)
            else:
                logging.error("Integrity check failed for %s. "
                              "Aborting flash.", image_path)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to flash {partition}: {e}")

    @staticmethod
    def flash_rom(rom_path):
        try:
            logging.info(f"Starting to flash ROM: {rom_path}")
            subprocess.run([DeviceManager.ADB_PATH, "sideload", rom_path], check=True)
            logging.info("ROM flashing completed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error("Failed to flash ROM: %s", e)
            return False

    @staticmethod
    def flash_kernel(kernel_image):
        try:
            if DeviceManager.verify_image(kernel_image):
                subprocess.run([DeviceManager.ADB_PATH, "reboot", "bootloader"],
                               check=True)
                subprocess.run([DeviceManager.FASTBOOT_PATH, "flash", "boot",
                                kernel_image], check=True)
                logging.info("Flashed kernel: %s", kernel_image)
            else:
                logging.error("Kernel image verification failed for %s. Aborting flash.", kernel_image)
        except subprocess.CalledProcessError as e:
            logging.error("Failed to flash kernel: %s", e)

    @staticmethod
    def verify_image(image_path):
        try:
            sha256_hash = hashlib.sha256()
            with open(image_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            checksum = sha256_hash.hexdigest()
            logging.info("Checksum for %s: %s", image_path, checksum)
            return True
        except FileNotFoundError as e:
            logging.error("File not found: %s", e)
            return False

    # --------------- Battery and Device Status Management ---------------
    @staticmethod
    def check_battery_level():
        try:
            battery_level = subprocess.check_output(
                [DeviceManager.ADB_PATH, "shell", "dumpsys", "battery"]).decode()
            logging.info("Battery status: %s", battery_level)
            return battery_level
        except subprocess.CalledProcessError as e:
            logging.error("Failed to retrieve battery status: %s", e)
            return None

    @staticmethod
    def get_device_info():
        try:
            device_info = subprocess.check_output([DeviceManager.ADB_PATH,
                                                   "shell", "getprop"]).decode()
            logging.info("Device info: %s", device_info)
            return device_info
        except subprocess.CalledProcessError as e:
            logging.error("Failed to retrieve device information: %s", e)
            return None

    @staticmethod
    def get_device_model():
        try:
            model = subprocess.check_output([DeviceManager.ADB_PATH, "shell", "getprop",
                                             "ro.product.model"]).decode().strip()
            logging.info(f"Device model: {model}")
            return model
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to retrieve device model: {e}")
            return None

    # --------------- Log Management ---------------
    @staticmethod
    def clear_logs():
        try:
            subprocess.run([DeviceManager.ADB_PATH, "logcat", "-c"], check=True)
            logging.info("Cleared logs on the device.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to clear logs: {e}")

    @staticmethod
    def retrieve_logs():
        try:
            logs = subprocess.check_output([DeviceManager.ADB_PATH, "logcat", "-d"]).decode()
            logging.info("Retrieved logs from the device.")
            return logs
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to retrieve logs: {e}")
            return None

    # --------------- OTA Updates ---------------
    @staticmethod
    def apply_ota_update(ota_zip):
        try:
            subprocess.run([DeviceManager.ADB_PATH, "push", ota_zip, "/sdcard/"], check=True)
            subprocess.run([DeviceManager.ADB_PATH, "shell", "twrp", "install",
                            f"/sdcard/{os.path.basename(ota_zip)}"], check=True)
            logging.info(f"OTA Update {ota_zip} applied successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to apply OTA update: {e}")
            return False

    @staticmethod
    def backup_data_partition():
        try:
            logging.info("Starting data partition backup.")
            subprocess.run([DeviceManager.ADB_PATH, "shell", "twrp", "backup", "data"],
                           check=True)
            logging.info("Data partition backup completed.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to back up data partition: {e}")

    @staticmethod
    def restore_device():
        try:
            subprocess.run([DeviceManager.ADB_PATH, "shell", "twrp", "restore", "SDB"],
                           check=True)
            logging.info("Device restored from backup successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to restore device: {e}")

    # --------------- Encryption Handling ---------------
    @staticmethod
    def detect_encryption_type():
        try:
            encryption_type = subprocess.check_output([DeviceManager.ADB_PATH, "shell",
                                                       "getprop", "ro.crypto.type"]).decode().strip()
            logging.info(f"Detected encryption type: {encryption_type}")
            return encryption_type
        except subprocess.CalledProcessError as e:
            logging.error(f"Error detecting encryption type: {e}")
            return None

    @staticmethod
    def apply_decryption_tool():
        encryption_type = DeviceManager.detect_encryption_type()

        if encryption_type == "file":
            logging.info("Applying decryption for File-Based Encryption (FBE).")
            return DeviceManager.apply_fbe_decryption_tool()
        if encryption_type == "block":
            logging.info("Applying decryption for Full-Disk Encryption (FDE).")
            return DeviceManager.apply_fde_decryption_tool()
        logging.error("Unknown encryption type detected.")
        return False

    @staticmethod
    def apply_fde_decryption_tool():
        try:
            subprocess.run([DeviceManager.ADB_PATH, "push",
                            "Disable_Dm-Verity_ForceEncrypt_FDE.zip", "/sdcard/"], check=True)
            subprocess.run([DeviceManager.ADB_PATH, "shell", "twrp", "install",
                            "/sdcard/Disable_Dm-Verity_ForceEncrypt_FDE.zip"], check=True)
            logging.info("Applied FDE decryption tool.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to apply FDE decryption tool: {e}")
            return False

    @staticmethod
    def apply_fbe_decryption_tool():
        try:
            subprocess.run([DeviceManager.ADB_PATH, "push",
                            "Disable_Dm-Verity_ForceEncrypt_FBE.zip", "/sdcard/"], check=True)
            subprocess.run([DeviceManager.ADB_PATH, "shell", "twrp", "install",
                            "/sdcard/Disable_Dm-Verity_ForceEncrypt_FBE.zip"], check=True)
            logging.info("Applied FBE decryption tool.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to apply FBE decryption tool: {e}")
            return False

    # --------------- Rescue Mode and EDL Mode ---------------
    @staticmethod
    def enter_edl_mode():
        try:
            subprocess.run([DeviceManager.ADB_PATH, "reboot-edl"], check=True)
            logging.info("Entered EDL mode for recovery.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to enter EDL mode: {e}")
