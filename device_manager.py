import hashlib
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

 def download_decryption_tool(url, file_name):
    try:
        response = requests.get(url, stream=True)
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        logging.info(f"Downloaded decryption tool: {file_name}")
        return file_name
    except Exception as e:
        logging.error(f"Failed to download decryption tool: {e}")
        return None

 @staticmethod
    def toggle_magisk_hide():
        try:
            # Enable Magisk Hide
            subprocess.run(["adb", "shell", "magiskhide", "enable"], check=True)
            logging.info("Magisk Hide enabled.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to enable Magisk Hide: {e}")

    @staticmethod
    def add_app_to_magisk_hide(package_name):
        try:
            # Add an app to Magisk Hide to bypass root detection
            subprocess.run(["adb", "shell", "magiskhide", "add", package_name], check=True)
            logging.info(f"Root hidden from app: {package_name}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to hide root from app: {e}")

    @staticmethod
    def install_safetynet_fix():
        try:
            # Download and install Universal SafetyNet Fix (user can specify URL if needed)
            safetynet_fix_url = "https://example.com/universal-safetynet-fix.zip"  # Replace with actual URL
            DeviceManager.download_and_install_zip(safetynet_fix_url, "/sdcard/SafetyNetFix.zip")
            logging.info("Universal SafetyNet Fix installed.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install SafetyNet Fix: {e}")

    @staticmethod
    def download_and_install_zip(url, file_path):
        try:
            # Download a ZIP file from the URL and install it
            response = requests.get(url, stream=True)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            # Install the downloaded ZIP via Magisk
            subprocess.run(["adb", "push", file_path, "/sdcard/"], check=True)
            subprocess.run(["adb", "shell", "magisk", "--install-module", file_path], check=True)
            logging.info(f"Downloaded and installed: {file_path}")
        except Exception as e:
            logging.error(f"Failed to download or install ZIP: {e}")

 @staticmethod
    def flash_kernel(kernel_image):
        try:
            # Verify the integrity of the kernel image before flashing
            if DeviceManager.verify_image(kernel_image):
                subprocess.run(["adb", "reboot", "bootloader"], check=True)
                subprocess.run(["fastboot", "flash", "boot", kernel_image], check=True)
                logging.info(f"Flashed kernel: {kernel_image}")
            else:
                logging.error(f"Kernel image verification failed for {kernel_image}. Aborting flash.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to flash kernel: {e}")

    @staticmethod
    def verify_image(image_path):
        try:
            sha256_hash = hashlib.sha256()
            with open(image_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            checksum = sha256_hash.hexdigest()
            logging.info(f"Checksum for {image_path}: {checksum}")
            # Add logic to compare checksum with a known value if necessary
            return True  # Assume valid for now
        except FileNotFoundError as e:
            logging.error(f"Kernel image file not found: {e}")
            return False

  @staticmethod
    def get_cpu_frequency():
        try:
            # Query the current CPU frequency
            result = subprocess.check_output(["adb", "shell", "cat", "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"]).decode().strip()
            logging.info(f"Current CPU frequency: {result}")
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to get CPU frequency: {e}")
            return None

    @staticmethod
    def set_cpu_frequency(frequency):
        try:
            # Set the CPU frequency (requires root)
            subprocess.run(["adb", "shell", "echo", frequency, ">", "/sys/devices/system/cpu/cpu0/cpufreq/scaling_setspeed"], check=True)
            logging.info(f"CPU frequency set to: {frequency}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to set CPU frequency: {e}")

    @staticmethod
    def get_io_scheduler():
        try:
            # Query the current I/O scheduler
            result = subprocess.check_output(["adb", "shell", "cat", "/sys/block/mmcblk0/queue/scheduler"]).decode().strip()
            logging.info(f"Current I/O scheduler: {result}")
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to get I/O scheduler: {e}")
            return None

    @staticmethod
    def set_io_scheduler(scheduler):
        try:
            # Set the I/O scheduler (requires root)
            subprocess.run(["adb", "shell", "echo", scheduler, ">", "/sys/block/mmcblk0/queue/scheduler"], check=True)
            logging.info(f"I/O scheduler set to: {scheduler}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to set I/O scheduler: {e}")

   @staticmethod
    def detect_device():
        try:
            # Use adb to get the device's product name (e.g., 'guacamoleb' for OnePlus 7 Pro)
            device_model = subprocess.check_output(["adb", "shell", "getprop", "ro.product.device"]).decode().strip()
            logging.info(f"Detected device: {device_model}")
            return device_model
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to detect device: {e}")
            return None

    @staticmethod
    def load_device_profile(device_model, config):
        # Load the device profile from the config file based on the detected device
        if device_model in config:
            logging.info(f"Loaded profile for device: {device_model}")
            return config[device_model]
        else:
            logging.error(f"No profile found for device: {device_model}")
            return None

   @staticmethod
    def run_rooting_script(device_profile):
        try:
            if "rooting_script" in device_profile:
                script_commands = device_profile["rooting_script"]["commands"]
                for command in script_commands:
                    subprocess.run(command.split(), check=True)
                logging.info(f"Executed rooting script for {device_profile}")
            else:
                logging.warning("No rooting script found for this device.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to run rooting script: {e}")

   @staticmethod
    def download_firmware(firmware_url, save_path):
        try:
            # Download the firmware file from the URL
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
    def verify_checksum(file_path, expected_checksum):
        # Verify file integrity using MD5 checksum
        try:
            md5_hash = hashlib.md5()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    md5_hash.update(byte_block)
            file_md5 = md5_hash.hexdigest()
            logging.info(f"Calculated MD5 checksum: {file_md5}")
            return file_md5 == expected_checksum
        except FileNotFoundError as e:
            logging.error(f"File not found for checksum verification: {e}")
            return False

    @staticmethod
    def download_and_verify_firmware(firmware_url, save_path, expected_checksum):
        # Download firmware and verify the integrity
        if DeviceManager.download_firmware(firmware_url, save_path):
            if DeviceManager.verify_checksum(save_path, expected_checksum):
                logging.info("Firmware verified successfully.")
                return True
            else:
                logging.error("Firmware checksum mismatch! The file may be corrupted.")
                return False
        else:
            logging.error("Failed to download firmware.")
            return False

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
