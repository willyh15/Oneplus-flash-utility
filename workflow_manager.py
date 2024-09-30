import logging
import time
from device_manager import DeviceManager

class WorkflowManager:
    def __init__(self, device, progress_bar=None):
        self.device = device
        self.progress_bar = progress_bar

    def update_progress(self, value, message=""):
        """Update the progress bar and log a message."""
        if self.progress_bar:
            self.progress_bar.setValue(value)
        logging.info(message)

    def full_device_reset(self):
        """Perform a full device reset workflow."""
        try:
            logging.info("Starting full device reset workflow.")
            
            # Step 1: Backup Data
            self.update_progress(10, "Backing up data partition...")
            DeviceManager.backup_data_partition()

            # Step 2: Flash Stock ROM
            self.update_progress(30, "Flashing stock ROM...")
            if not DeviceManager.flash_rom("path/to/stock_rom.zip"):
                raise Exception("Failed to flash stock ROM.")

            # Step 3: Flash Custom Recovery
            self.update_progress(50, "Flashing custom recovery...")
            if not DeviceManager.flash_partition("path/to/twrp.img", "recovery"):
                raise Exception("Failed to flash custom recovery.")

            # Step 4: Root Device
            self.update_progress(70, "Rooting device...")
            DeviceManager.root_device(preserve_encryption=False)

            # Step 5: Restore Data
            self.update_progress(90, "Restoring data partition...")
            DeviceManager.restore_device()

            self.update_progress(100, "Full device reset completed successfully!")
            logging.info("Full device reset workflow completed.")
        except Exception as e:
            logging.error(f"Workflow failed: {e}")
            self.update_progress(0, "Workflow failed. See logs for details.")

    def automated_root_and_rom_installation(self, rom_path, magisk_path):
        """Perform automated root and custom ROM installation."""
        try:
            logging.info("Starting automated root and ROM installation workflow.")
            
            # Step 1: Backup Current State
            self.update_progress(10, "Backing up data partition...")
            DeviceManager.backup_data_partition()

            # Step 2: Flash Custom ROM
            self.update_progress(30, f"Flashing custom ROM: {rom_path}")
            if not DeviceManager.flash_rom(rom_path):
                raise Exception(f"Failed to flash custom ROM: {rom_path}")

            # Step 3: Flash Magisk for Root
            self.update_progress(70, f"Flashing Magisk for root: {magisk_path}")
            if not DeviceManager.flash_partition(magisk_path, "boot"):
                raise Exception(f"Failed to flash Magisk: {magisk_path}")

            self.update_progress(100, "Automated root and ROM installation completed successfully!")
            logging.info("Automated root and ROM installation workflow completed.")
        except Exception as e:
            logging.error(f"Workflow failed: {e}")
            self.update_progress(0, "Workflow failed. See logs for details.")
