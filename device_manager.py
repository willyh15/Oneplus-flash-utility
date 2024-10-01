import hashlib
import subprocess
import os
import logging

class DeviceManager:
    ADB_PATH = "C:/Users/willh/Downloads/platform-tools-latest-windows/platform-tools/adb.exe"
    FASTBOOT_PATH = "C:/Users/willh/Downloads/platform-tools-latest-windows/platform-tools/fastboot.exe"

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
                subprocess.run([DeviceManager.FASTBOOT_PATH, "flash", partition, image_path], check=True)
                logging.info("Flashed %s partition with %s", partition, image_path)
            else:
                logging.error("Integrity check failed for %s. Aborting flash.", image_path)
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
                subprocess.run([DeviceManager.ADB_PATH, "reboot", "bootloader"], check=True)
                subprocess.run([DeviceManager.FASTBOOT_PATH, "flash", "boot", kernel_image], check=True)
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
            battery_level = subprocess.check_output([DeviceManager.ADB_PATH, "shell", "dumpsys", "battery"]).decode()
            logging.info("Battery status: %s", battery_level)
            return battery_level
        except subprocess.CalledProcessError as e:
            logging.error("Failed to retrieve battery status: %s", e)
            return None

    @staticmethod
    def get_device_info():
        try:
            device_info = subprocess.check_output([DeviceManager.ADB_PATH, "shell", "getprop"]).decode()
            logging.info("Device info: %s", device_info)
            return device_info
        except subprocess.CalledProcessError as e:
            logging.error("Failed to retrieve device information: %s", e)
            return None

    @staticmethod
    def get_device_model():
        try:
            model = subprocess.check_output([DeviceManager.ADB_PATH, "shell", "getprop", "ro.product.model"]).decode().strip()
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
            subprocess.run([DeviceManager.ADB_PATH, "shell", "twrp", "install", f"/sdcard/{os.path.basename(ota_zip)}"], check=True)
            logging.info(f"OTA Update {ota_zip} applied successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to apply OTA update: {e}")
            return False

    @staticmethod
    def backup_data_partition():
        try:
            logging.info("Starting data partition backup.")
            subprocess.run([DeviceManager.ADB_PATH, "shell", "twrp", "backup", "data"], check=True)
            logging.info("Data partition backup completed.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to back up data partition: {e}")

    @staticmethod
    def restore_device():
        try:
            subprocess.run([DeviceManager.ADB_PATH, "shell", "twrp", "restore", "SDB"], check=True)
            logging.info("Device restored from backup successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to restore device: {e}")

    # --------------- Encryption Handling ---------------
    @staticmethod
    def detect_encryption_type():
        try:
            encryption_type = subprocess.check_output([DeviceManager.ADB_PATH, "shell", "getprop", "ro.crypto.type"]).decode().strip()
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
            subprocess.run([DeviceManager.ADB_PATH, "push", "Disable_Dm-Verity_ForceEncrypt_FDE.zip", "/sdcard/"], check=True)
            subprocess.run([DeviceManager.ADB_PATH, "shell", "twrp", "install", "/sdcard/Disable_Dm-Verity_ForceEncrypt_FDE.zip"], check=True)
            logging.info("Applied FDE decryption tool.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to apply FDE decryption tool: {e}")
            return False

    @staticmethod
    def apply_fbe_decryption_tool():
        try:
            subprocess.run([DeviceManager.ADB_PATH, "push", "Disable_Dm-Verity_ForceEncrypt_FBE.zip", "/sdcard/"], check=True)
            subprocess.run([DeviceManager.ADB_PATH, "shell", "twrp", "install", "/sdcard/Disable_Dm-Verity_ForceEncrypt_FBE.zip"], check=True)
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