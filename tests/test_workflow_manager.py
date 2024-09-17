import unittest
from unittest.mock import patch
from workflow_manager import WorkflowManager

class TestWorkflowManager(unittest.TestCase):

    @patch('workflow_manager.WorkflowManager.load_workflow')
    @patch('device_manager.DeviceManager.flash_partition', return_value=True)
    def test_workflow_success(self, mock_flash_partition, mock_load_workflow):
        mock_load_workflow.return_value = None
        workflow = WorkflowManager(None, "device", "partition_flash", "boot.img", "vendor.img", "system.img")
        workflow.workflows = {
            "partition_flash": ["flash_boot_partition", "flash_vendor_partition", "flash_system_partition"]
        }
        workflow.start()
        self.assertTrue(mock_flash_partition.called)
    
    @patch('workflow_manager.WorkflowManager.load_workflow')
    def test_workflow_fail(self, mock_load_workflow):
        mock_load_workflow.return_value = None
        workflow = WorkflowManager(None, "device", "partition_flash", "boot.img", None, None)
        workflow.workflows = {
            "partition_flash": ["flash_boot_partition", "flash_vendor_partition"]
        }
        workflow.start()
        # Expecting the workflow to fail due to missing images
        self.assertFalse(workflow.progressBar.value() == 100)

if __name__ == "__main__":
    unittest.main()