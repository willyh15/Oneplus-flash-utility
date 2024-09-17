import subprocess
import requests
import logging

class DeviceManager:
    @staticmethod
    def reboot_to_bootloader():
        try:
            subprocess.run(["adb", "reboot", "bootloader"], check=True)
            logging.info("Rebooted to bootloader")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to reboot to bootloader: {e}")

    @staticmethod
    def detect_encryption_type():
        try:
            # Detect encryption type using adb
            encryption_type = subprocess.check_output(["adb", "shell", "getprop", "ro.crypto.type"]).decode().strip()
            logging.info(f"Detected encryption type: {encryption_type}")
            return encryption_type
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to detect encryption type: {e}")
            return None

    @staticmethod
    def root_device(preserve_encryption=True):
        encryption_type = DeviceManager.detect_encryption_type()

        if encryption_type:
            if encryption_type == "file":
                logging.info("File-Based Encryption (FBE) detected. Proceeding with Magisk installation.")
            elif encryption_type == "block":
                logging.info("Full-Disk Encryption (FDE) detected. Proceeding with Magisk installation.")
            else:
                logging.warning("Unknown encryption type detected.")

            # Proceed with Magisk installation
            if preserve_encryption:
                logging.info("Preserving encryption during Magisk installation.")
                DeviceManager.install_magisk_with_encryption_preservation()
            else:
                logging.info("Encryption will be disabled.")
                DeviceManager.install_magisk_with_encryption_disabler()

    @staticmethod
    def install_magisk_with_encryption_preservation():
        try:
            # Push and flash Magisk preserving encryption
            subprocess.run(["adb", "push", "Magisk-v23.0.zip", "/sdcard/"], check=True)
            subprocess.run(["adb", "shell", "twrp", "install", "/sdcard/Magisk-v23.0.zip"], check=True)
            logging.info("Magisk installed successfully while preserving encryption.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install Magisk with encryption preservation: {e}")

    @staticmethod
    def install_magisk_with_encryption_disabler():
        try:
            # Push and flash Magisk and encryption disabler
            subprocess.run(["adb", "push", "Magisk-v23.0.zip", "/sdcard/"], check=True)
            subprocess.run(["adb", "push", "Disable_Dm-Verity_ForceEncrypt_11.02.2020.zip", "/sdcard/"], check=True)
            subprocess.run(["adb", "shell", "twrp", "install", "/sdcard/Magisk-v23.0.zip"], check=True)
            subprocess.run(["adb", "shell", "twrp", "install", "/sdcard/Disable_Dm-Verity_ForceEncrypt_11.02.2020.zip"], check=True)
            logging.info("Magisk and encryption disabler installed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install Magisk with encryption disabler: {e}")

    @staticmethod
    def flash_recovery(rom_zip):
        try:
            subprocess.run(["fastboot", "flash", "recovery", rom_zip], check=True)
            logging.info(f"Flashed recovery: {rom_zip}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to flash recovery: {e}")

    def enter_rescue_mode():
        try:
            logging.info("Entering Rescue Mode.")
            # Step 1: Reboot into recovery mode or EDL mode
            subprocess.run(["adb", "reboot", "recovery"], check=True)  # Enter recovery mode
            logging.info("Device is in recovery mode.")

            # Step 2: Create a backup of critical data
            logging.info("Backing up data partition.")
            DeviceManager.backup_data_partition()

            # Step 3: Option to restore stock firmware or a custom ROM
            restore_choice = input("Do you want to restore stock firmware or a custom ROM? (Enter 'stock' or 'custom'): ")
            if restore_choice == 'stock':
                logging.info("Restoring stock firmware.")
                DeviceManager.restore_stock_firmware()
            elif restore_choice == 'custom':
                logging.info("Restoring custom ROM.")
                DeviceManager.restore_custom_rom()
            else:
                logging.warning("Invalid choice. No firmware restored.")

            logging.info("Rescue operation completed.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to enter Rescue Mode: {e}")
            if success:
            QtWidgets.QMessageBox.information(self, "Info", "Rescue mode completed successfully.")
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to enter rescue mode. Check logs for details.")

    @staticmethod
    def backup_data_partition():
        try:
            logging.info("Starting data partition backup.")
            subprocess.run(["adb", "shell", "twrp", "backup", "data"], check=True)
            logging.info("Data partition backup completed.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to back up data partition: {e}")

    @staticmethod
    def restore_stock_firmware():
        try:
            logging.info("Restoring stock firmware.")
            # This would flash stock firmware via fastboot or using recovery
            subprocess.run(["fastboot", "flash", "system", "stock_firmware.img"], check=True)
            logging.info("Stock firmware restored successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to restore stock firmware: {e}")

    @staticmethod
    def restore_custom_rom():
        try:
            logging.info("Restoring custom ROM.")
            # This would sideload a custom ROM via ADB or flash through recovery
            subprocess.run(["adb", "sideload", "custom_rom.zip"], check=True)
            logging.info("Custom ROM restored successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to restore custom ROM: {e}")

    @staticmethod
    def enter_edl_mode():
        try:
            subprocess.run(["adb", "reboot-edl"], check=True)
            logging.info("Entered EDL mode for recovery.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to enter EDL mode: {e}")

    @staticmethod
    def backup_partitions():
        try:
            subprocess.run(["adb", "shell", "twrp", "backup", "SDB"], check=True)
            logging.info("Partitions backed up successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to back up partitions: {e}")

    @staticmethod
    def is_storage_encrypted():
        try:
            result = subprocess.check_output(["adb", "shell", "getprop", "ro.crypto.state"]).decode().strip()
            return result == "encrypted"
        except subprocess.CalledProcessError as e:
            logging.error(f"Error checking storage encryption state: {e}")
            return False

    @staticmethod
    def get_latest_magisk_version():
        try:
            url = "https://api.github.com/repos/topjohnwu/Magisk/releases/latest"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            latest_release = response.json()
            latest_version = latest_release["tag_name"]
            download_url = latest_release["assets"][0]["browser_download_url"]
            logging.info(f"Fetched latest Magisk version: {latest_version}")
            return latest_version, download_url
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching latest Magisk version: {e}")
            return None, None

    @staticmethod
    def get_device_twrp_url(device, config):
        return config.get(device.lower(), {}).get("twrp", None)
