import logging
from device_manager import DeviceManager
import time
import json

class WorkflowManager:
    def __init__(self, progressBar, device, workflow_type, boot_img=None, vendor_img=None, system_img=None):
        self.progressBar = progressBar
        self.device = device
        self.workflow_type = workflow_type
        self.boot_img = boot_img
        self.vendor_img = vendor_img
        self.system_img = system_img
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
        if step == "flash_boot_partition" and self.boot_img:
            DeviceManager.flash_partition(self.boot_img, "boot")
        elif step == "flash_vendor_partition" and self.vendor_img:
            DeviceManager.flash_partition(self.vendor_img, "vendor")
        elif step == "flash_system_partition" and self.system_img:
            DeviceManager.flash_partition(self.system_img, "system")
        else:
            logging.warning(f"Unknown step: {step}")
            return False
        return True
