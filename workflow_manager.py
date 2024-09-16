import logging
from device_manager import DeviceManager
import time
import json

class WorkflowManager:
    def __init__(self, progressBar, device, workflow_type, custom_rom=None):
        self.progressBar = progressBar
        self.device = device
        self.workflow_type = workflow_type
        self.custom_rom = custom_rom
        self.load_workflow()

    def load_workflow(self):
        try:
            with open('workflows.json', 'r') as f:
                self.workflows = json.load(f)
            logging.info(f"Loaded workflow for {self.workflow_type}")
        except FileNotFoundError as e:
            logging.error(f"workflows.json not found: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding workflows.json: {e}")

    def start(self):
        steps = self.workflows.get(self.workflow_type, [])
        self.progressBar.setValue(0)
        total_steps = len(steps)

        for i, step in enumerate(steps):
            success = self.execute_step(step)
            if not success:
                logging.error(f"Failed at step: {step}")
                break
            self.progressBar.setValue(int((i + 1) / total_steps * 100))
            time.sleep(1)  # Simulating time delay between steps

        if self.progressBar.value() == 100:
            logging.info(f"{self.workflow_type} completed successfully!")

    def execute_step(self, step):
        if step == "boot_into_twrp":
            DeviceManager.reboot_to_bootloader()
        elif step == "wipe_data":
            DeviceManager.backup_partitions()
            # Assume wipe data logic here
        elif step == "flash_magisk":
            version, url = DeviceManager.get_latest_magisk_version()
            if url:
                # Flash Magisk (code to download and flash Magisk here)
                logging.info(f"Magisk flashed: {url}")
        elif step == "flash_custom_rom" and self.custom_rom:
            DeviceManager.flash_recovery(self.custom_rom)
        elif step == "decrypt_storage":
            if DeviceManager.is_storage_encrypted():
                # Flash decryption tool here
                logging.info("Storage decrypted successfully")
            else:
                logging.info("Storage is already decrypted")
        elif step == "enter_edl_mode":
            DeviceManager.enter_edl_mode()
        else:
            logging.warning(f"Unknown step: {step}")
            return False
        return True
