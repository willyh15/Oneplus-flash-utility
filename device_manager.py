import subprocess
import requests
import platform
import os
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
    def check_adb_driver():
        try:
            if platform.system() == "Windows":
                # Check if ADB driver is installed on Windows
                adb_output = subprocess.check_output(["adb", "devices"]).decode().strip()
                if "List of devices attached" in adb_output:
                    logging.info("ADB driver is installed and device is detected.")
                    return True
            elif platform.system() == "Linux" or platform.system() == "Darwin":
                # Check if ADB is installed on Linux/macOS
                subprocess.check_output(["which", "adb"])
                logging.info("ADB driver is installed.")
                return True
            return False
        except subprocess.CalledProcessError as e:
            logging.error("ADB driver is not installed or the device is not detected.")
            return False

    @staticmethod
    def check_fastboot_driver():
        try:
            if platform.system() == "Windows":
                # Check if Fastboot driver is installed on Windows
                fastboot_output = subprocess.check_output(["fastboot", "devices"]).decode().strip()
                if fastboot_output:
                    logging.info("Fastboot driver is installed and device is detected.")
                    return True
            elif platform.system() == "Linux" or platform.system() == "Darwin":
                # Check if Fastboot is installed on Linux/macOS
                subprocess.check_output(["which", "fastboot"])
                logging.info("Fastboot driver is installed.")
                return True
            return False
        except subprocess.CalledProcessError as e:
            logging.error("Fastboot driver is not installed or the device is not detected.")
            return False

   @staticmethod
    def install_adb_driver_windows():
        # URL to download Google USB drivers for Windows
        driver_url = "https://dl.google.com/android/repository/latest_usb_driver_windows.zip"
        driver_zip = "usb_driver.zip"
        driver_dir = "usb_driver"

        try:
            # Download the USB driver ZIP file
            logging.info("Downloading ADB driver for Windows...")
            DeviceManager.download_file(driver_url, driver_zip)

            # Unzip the driver file
            if DeviceManager.unzip_file(driver_zip, driver_dir):
                logging.info("Driver unzipped successfully. Please install it manually from: " + os.path.abspath(driver_dir))
                return True
            else:
                logging.error("Failed to unzip driver.")
                return False
        except Exception as e:
            logging.error(f"Failed to download or install ADB driver: {e}")
            return False

    @staticmethod
    def download_file(url, save_path):
        try:
            response = requests.get(url, stream=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    if chunk:
                        f.write(chunk)
            logging.info(f"Downloaded: {save_path}")
        except Exception as e:
            logging.error(f"Failed to download file: {e}")

    @staticmethod
    def unzip_file(zip_path, extract_to):
        try:
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            return True
        except Exception as e:
            logging.error(f"Failed to unzip file: {e}")
            return False

   @staticmethod
    def install_adb_driver_linux():
        logging.info("Please install ADB using your package manager. For example: sudo apt install adb")

   @staticmethod
    def check_edl_mode():
        try:
            if platform.system() == "Windows":
                # On Windows, you can check Device Manager or run commands via devcon or wmic to detect the device in EDL mode
                edl_output = subprocess.check_output(["wmic", "path", "Win32_PnPEntity", "where", "Caption like '%Qualcomm%'"]).decode().strip()
                if "Qualcomm" in edl_output:
                    logging.info("Device is in EDL mode (Qualcomm HS-USB QDLoader detected).")
                    return True
            elif platform.system() == "Linux":
                # On Linux, use lsusb to check for the Qualcomm device in EDL mode
                edl_output = subprocess.check_output(["lsusb"]).decode().strip()
                if "Qualcomm" in edl_output:
                    logging.info("Device is in EDL mode (Qualcomm HS-USB QDLoader detected).")
                    return True
            elif platform.system() == "Darwin":  # macOS
                # Similar to Linux, use system_profiler or lsusb equivalent to detect Qualcomm device
                edl_output = subprocess.check_output(["system_profiler", "SPUSBDataType"]).decode().strip()
                if "Qualcomm" in edl_output:
                    logging.info("Device is in EDL mode (Qualcomm HS-USB QDLoader detected).")
                    return True
            logging.warning("Device is not in EDL mode.")
            return False
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to detect EDL mode: {e}")
            return False

   @staticmethod
    def flash_edl_firmware(tool_path, firmware_path):
        try:
            if platform.system() == "Windows":
                # Launch MsmDownloadTool or QFIL with the specified firmware
                logging.info(f"Launching EDL flashing tool: {tool_path}")
                os.startfile(tool_path)  # On Windows, this will open the specified tool
                logging.info(f"Please select the firmware in {firmware_path} and start the flashing process.")
            elif platform.system() == "Linux" or platform.system() == "Darwin":
                # EDL flashing on Linux/macOS is done via edl.py or open-source tools like QFIL
                logging.info(f"Launching EDL tool or QFIL on {platform.system()}. Please proceed manually.")
                subprocess.run(["./edl.py", "firehose", firmware_path], check=True)
        except Exception as e:
            logging.error(f"Failed to launch EDL tool: {e}")

   @staticmethod
    def flash_rom(rom_path):
        try:
            logging.info(f"Starting to flash ROM: {rom_path}")
            subprocess.run(["adb", "sideload", rom_path], check=True)
            logging.info("ROM flashing completed successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to flash ROM: {e}")

    @staticmethod
    def download_firmware(firmware_url, save_path):
        try:
            logging.info(f"Downloading firmware from: {firmware_url}")
            response = requests.get(firmware_url, stream=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    if chunk:
                        f.write(chunk)
            logging.info(f"Firmware downloaded to: {save_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to download firmware: {e}")
            return False

     @staticmethod
    def get_latest_release(repo_url):
        try:
            api_url = f"https://api.github.com/repos/{repo_url}/releases/latest"
            response = requests.get(api_url)
            if response.status_code == 200:
                latest_release = response.json()
                version = latest_release['tag_name']
                download_url = latest_release['assets'][0]['browser_download_url']
                logging.info(f"Latest release for {repo_url}: {version}")
                return version, download_url
            else:
                logging.warning(f"Failed to fetch latest release from {repo_url}. Status code: {response.status_code}")
                return None, None
        except Exception as e:
            logging.error(f"Error fetching latest release: {e}")
            return None, None

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
