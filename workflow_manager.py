import logging
from device_manager import DeviceManager
import time
import json

class WorkflowManager:
    def __init__(self, progressBar, device, workflow_type, boot_img=None, vendor_img=None, system_img=None):
        """
        Initializes the WorkflowManager with necessary data for executing the workflow.

        Args:
            progressBar (QProgressBar): The progress bar UI element to show progress.
            device (str): The device being flashed or managed.
            workflow_type (str): The type of workflow to run (e.g., partition flashing).
            boot_img (str): Path to the boot image.
            vendor_img (str): Path to the vendor image.
            system_img (str): Path to the system image.
        """
        self.progressBar = progressBar
        self.device = device
        self.workflow_type = workflow_type
        self.boot_img = boot_img
        self.vendor_img = vendor_img
        self.system_img = system_img
        self.workflows = {}
        self.load_workflow()

    def load_workflow(self):
        """
        Loads the workflow steps from the 'workflows.json' file based on the 
        workflow type.
        """
        try:
            with open('workflows.json', 'r') as f:
                self.workflows = json.load(f)
                logging.info(f"Loaded workflow configuration for {self.workflow_type}.")
        except FileNotFoundError as e:
            logging.error(f"workflows.json file not found: {e}")
            self.workflows = {}
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding workflows.json: {e}")
            self.workflows = {}

    def start(self):
        """Starts the workflow by executing each step and updating the progress bar."""
        steps = self.workflows.get(self.workflow_type, [])
        if not steps:
            logging.error(f"No steps found for workflow type: {self.workflow_type}")
            return

        total_steps = len(steps)
        self.progressBar.setValue(0)

        for i, step in enumerate(steps):
            success = self.execute_step(step)
            if not success:
                logging.error(f"Workflow failed at step: {step}")
                break

            # Update progress bar
            progress = int((i + 1) / total_steps * 100)
            self.progressBar.setValue(progress)
            time.sleep(1)  # Simulating time delay between steps

        if self.progressBar.value() == 100:
            logging.info(f"{self.workflow_type} workflow completed successfully!")
        else:
            logging.error(f"{self.workflow_type} workflow did not complete successfully.")

    def execute_step(self, step):
        """
        Executes a single step in the workflow based on the step type.

        Args:
            step (str): The current step to execute.

        Returns:
            bool: True if the step was executed successfully, False otherwise.
        """
        if step == "flash_boot_partition" and self.boot_img:
            logging.info("Flashing boot partition.")
            return DeviceManager.flash_partition(self.boot_img, "boot")
        if step == "flash_vendor_partition" and self.vendor_img:
            logging.info("Flashing vendor partition.")
            return DeviceManager.flash_partition(self.vendor_img, "vendor")
        if step == "flash_system_partition" and self.system_img:
            logging.info("Flashing system partition.")
            return DeviceManager.flash_partition(self.system_img, "system")
        logging.warning(f"Unknown or unsupported step: {step}")
        return False
