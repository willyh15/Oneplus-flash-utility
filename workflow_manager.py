import logging
import time


class WorkflowManager:
    def __init__(self, progress_bar, device_profile, workflow_type, *args):
        self.progress_bar = progress_bar
        self.device_profile = device_profile
        self.workflow_type = workflow_type
        self.args = args

    def start(self):
        logging.info(
            f"Starting workflow: {self.workflow_type} for device {self.device_profile}"
        )
        self.progress_bar.setValue(0)

        # Simulate each step of the workflow
        if self.workflow_type == "partition_flash":
            self._flash_partitions(*self.args)
        elif self.workflow_type == "backup_restore":
            self._backup_restore()

        self.progress_bar.setValue(100)
        logging.info(f"Completed workflow: {self.workflow_type}")

    def _flash_partitions(self, boot_img, vendor_img, system_img):
        logging.info(f"Flashing boot partition with {boot_img}")
        time.sleep(1)  # Simulate flashing time
        self.progress_bar.setValue(30)

        logging.info(f"Flashing vendor partition with {vendor_img}")
        time.sleep(1)
        self.progress_bar.setValue(60)

        logging.info(f"Flashing system partition with {system_img}")
        time.sleep(1)
        self.progress_bar.setValue(100)

    def _backup_restore(self):
        logging.info("Starting backup operation...")
        time.sleep(2)
        self.progress_bar.setValue(50)

        logging.info("Backup completed. Restoring...")
        time.sleep(2)
        self.progress_bar.setValue(100)
