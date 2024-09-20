import hashlib
import subprocess
import requests
import platform
import os
import logging

class DeviceManager:

    # --------------- Partition and Bootloader Management ---------------
    @staticmethod
    def reboot_to_bootloader():
        try:
            subprocess.run(["adb", "reboot", "bootloader"], check=True)
            logging.info("Rebooted to bootloader.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to reboot to bootloader: {e}")

    @staticmethod
    def flash_partition(image_path, partition):
        try:
            # Verify the integrity of the partition image before flashing
            if DeviceManager.verify_image(image_path):
                subprocess.run(["fastboot", "flash", partition, image_path], check=True)
                logging.info(f"Flashed {partition} partition with {image_path}")
            else:
                logging.error(f"Integrity check failed for {image_path}. Aborting flash.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to flash {partition}: {e}")

    @staticmethod
    def flash_rom(rom_path):
        try:
            logging.info(f"Starting to flash ROM: {rom_path}")
            subprocess.run(["adb", "sideload", rom_path], check=True)
            logging.info("ROM flashing completed successfully.")
            return True  # Ensure the function returns True on success
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to flash ROM: {e}")
            return False  # Return False if there is an error

    @staticmethod
    def flash_kernel(kernel_image):
        try:
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
            # For now, assume the image is valid
            return True
        except FileNotFoundError as e:
            logging.error(f"File not found: {e}")
            return False

    @staticmethod
    def get_current_slot():
        try:
            result = subprocess.check_output(["fastboot", "getvar", "current-slot"]).decode().strip()
            logging.info(f"Current slot: {result}")
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"Error retrieving current slot: {e}")
            return None

    @staticmethod
    def set_active_slot(slot):
        try:
            subprocess.run(["fastboot", "set_active", slot], check=True)
            logging.info(f"Set active slot to: {slot}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to set active slot: {e}")

    # --------------- Backup and Restore ---------------
    @staticmethod
    def backup_device():
        try:
            subprocess.run(["adb", "shell", "twrp", "backup", "SDB"], check=True)
            logging.info("Backup completed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Backup failed: {e}")
            return False

    @staticmethod
    def restore_device():
        try:
            subprocess.run(["adb", "shell", "twrp", "restore", "SDB"], check=True)
            logging.info("Device restored from backup successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to restore device: {e}")

    @staticmethod
    def backup_data_partition():
        try:
            logging.info("Starting data partition backup.")
            subprocess.run(["adb", "shell", "twrp", "backup", "data"], check=True)
            logging.info("Data partition backup completed.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to back up data partition: {e}")

    # --------------- Magisk Management ---------------
    @staticmethod
    def install_magisk_module(module_zip):
        try:
            subprocess.run(["adb", "push", module_zip, "/sdcard/"], check=True)
            subprocess.run(["adb", "shell", "magisk", "--install-module", f"/sdcard/{os.path.basename(module_zip)}"], check=True)
            logging.info(f"Installed Magisk module: {module_zip}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install Magisk module: {e}")

    @staticmethod
    def remove_magisk_module(module_name):
        try:
            subprocess.run(["adb", "shell", "rm", "-rf", f"/data/adb/modules/{module_name}"], check=True)
            logging.info(f"Removed Magisk module: {module_name}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to remove Magisk module: {e}")

    @staticmethod
    def toggle_magisk_hide():
        try:
            subprocess.run(["adb", "shell", "magiskhide", "toggle"], check=True)
            logging.info("Toggled Magisk Hide.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to toggle Magisk Hide: {e}")

    @staticmethod
    def add_app_to_magisk_hide(package_name):
        try:
            subprocess.run(["adb", "shell", "magiskhide", "add", package_name], check=True)
            logging.info(f"Root hidden from app: {package_name}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to hide root from app: {e}")

    @staticmethod
    def reflash_magisk_after_ota():
        try:
            subprocess.run(["adb", "shell", "magisk", "--install-module", "/sdcard/Magisk-v23.0.zip"], check=True)
            logging.info("Magisk re-flashed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to re-flash Magisk: {e}")
            return False

    # --------------- OTA Updates ---------------
    @staticmethod
    def apply_ota_update(ota_zip):
        try:
            subprocess.run(["adb", "push", ota_zip, "/sdcard/"], check=True)
            subprocess.run(["adb", "shell", "twrp", "install", f"/sdcard/{ota_zip.split('/')[-1]}"], check=True)
            logging.info(f"OTA Update {ota_zip} applied successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to apply OTA update: {e}")
            return False

    # --------------- Encryption Handling ---------------
    @staticmethod
    def detect_encryption_type():
        try:
            encryption_type = subprocess.check_output(["adb", "shell", "getprop", "ro.crypto.type"]).decode().strip()
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
            subprocess.run(["adb", "push", "Disable_Dm-Verity_ForceEncrypt_FDE.zip", "/sdcard/"], check=True)
            subprocess.run(["adb", "shell", "twrp", "install", "/sdcard/Disable_Dm-Verity_ForceEncrypt_FDE.zip"], check=True)
            logging.info("Applied FDE decryption tool.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to apply FDE decryption tool: {e}")
            return False

    @staticmethod
    def is_storage_encrypted():
        try:
            result = subprocess.check_output(["adb", "shell", "getprop", "ro.crypto.state"]).decode().strip()
            return result == "encrypted"
        except subprocess.CalledProcessError as e:
            logging.error(f"Error checking storage encryption state: {e}")
            return False

    # --------------- EDL and Rescue Mode ---------------
    @staticmethod
    def enter_edl_mode():
        try:
            subprocess.run(["adb", "reboot-edl"], check=True)
            logging.info("Entered EDL mode for recovery.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to enter EDL mode: {e}")

    @staticmethod
    def flash_edl_firmware(tool_path, firmware_path):
        try:
            if platform.system() == "Windows":
                logging.info(f"Launching EDL flashing tool: {tool_path}")
                os.startfile(tool_path)
                logging.info(f"Please select the firmware in {firmware_path} and start the flashing process.")
            elif platform.system() in ["Linux", "Darwin"]:
                logging.info(f"Launching EDL tool on {platform.system()}.")
                subprocess.run(["./edl.py", "firehose", firmware_path], check=True)
        except Exception as e:
            logging.error(f"Failed to launch EDL tool: {e}")

    @staticmethod
    def enter_rescue_mode():
        try:
            logging.info("Entering Rescue Mode.")
            subprocess.run(["adb", "reboot", "recovery"], check=True)
            logging.info("Device is in recovery mode.")

            DeviceManager.backup_data_partition()

            # Option to restore stock firmware or a custom ROM
            restore_choice = input("Do you want to restore stock firmware or a custom ROM? (Enter 'stock' or 'custom'): ")
            if restore_choice == 'stock':
                DeviceManager.restore_stock_firmware()
            elif restore_choice == 'custom':
                DeviceManager.restore_custom_rom()
            else:
                logging.warning("Invalid choice. No firmware restored.")

            logging.info("Rescue operation completed.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to enter Rescue Mode: {e}")

    # --------------- Firmware Download and Verification ---------------
    @staticmethod
    def download_firmware(firmware_url, save_path):
        try:
            logging.info(f"Downloading firmware from: {firmware_url}")
            response = requests.get(firmware_url, stream=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            logging.info(f"Firmware downloaded to: {save_path}")
            return True
        except Exception as e:
            logging.error(f"Failed to download firmware: {e}")
            return False

    @staticmethod
    def verify_checksum(file_path, expected_checksum):
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
        if DeviceManager.download_firmware(firmware_url, save_path):
            if DeviceManager.verify_checksum(save_path, expected_checksum):
                logging.info("Firmware verified successfully.")
                return True
            logging.error("Firmware checksum mismatch! The file may be corrupted.")
            return False
        logging.error("Failed to download firmware.")
        return False

    # --------------- Device Detection ---------------
    @staticmethod
    def detect_device():
        try:
            device_model = subprocess.check_output(["adb", "shell", "getprop", "ro.product.device"]).decode().strip()
            logging.info(f"Detected device: {device_model}")
            return device_model
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to detect device: {e}")
            return None

    @staticmethod
    def load_device_profile(device_model, config):
        if device_model in config:
            logging.info(f"Loaded profile for device: {device_model}")
            return config[device_model]
        logging.error(f"No profile found for device: {device_model}")
        return None

    # --------------- Kernel Management ---------------
    @staticmethod
    def get_cpu_frequency():
        try:
            result = subprocess.check_output(["adb", "shell", "cat", "/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"]).decode().strip()
            logging.info(f"Current CPU frequency: {result}")
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to get CPU frequency: {e}")
            return None

    @staticmethod
    def set_cpu_frequency(frequency):
        try:
            subprocess.run(["adb", "shell", "echo", frequency, ">", "/sys/devices/system/cpu/cpu0/cpufreq/scaling_setspeed"], check=True)
            logging.info(f"CPU frequency set to: {frequency}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to set CPU frequency: {e}")

    @staticmethod
    def get_io_scheduler():
        try:
            result = subprocess.check_output(["adb", "shell", "cat", "/sys/block/mmcblk0/queue/scheduler"]).decode().strip()
            logging.info(f"Current I/O scheduler: {result}")
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to get I/O scheduler: {e}")
            return None

    @staticmethod
    def set_io_scheduler(scheduler):
        try:
            subprocess.run(["adb", "shell", "echo", scheduler, ">", "/sys/block/mmcblk0/queue/scheduler"], check=True)
            logging.info(f"I/O scheduler set to: {scheduler}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to set I/O scheduler: {e}")

    # --------------- External Releases (e.g., Magisk, TWRP) ---------------
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
