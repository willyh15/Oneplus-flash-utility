import unittest
from unittest.mock import patch
from device_manager import DeviceManager

class TestDeviceManager(unittest.TestCase):
    
    @patch('subprocess.run')
    def test_reboot_to_bootloader(self, mock_run):
        DeviceManager.reboot_to_bootloader()
        mock_run.assert_called_with(["adb", "reboot", "bootloader"], check=True)

    @patch('subprocess.run')
    def test_flash_partition(self, mock_run):
        with patch('device_manager.DeviceManager.verify_image', return_value=True):
            DeviceManager.flash_partition("boot.img", "boot")
            mock_run.assert_called_with(["fastboot", "flash", "boot", "boot.img"], check=True)
    
    @patch('subprocess.run')
    def test_flash_rom(self, mock_run):
        DeviceManager.flash_rom("rom.zip")
        mock_run.assert_called_with(["adb", "sideload", "rom.zip"], check=True)
    
    @patch('subprocess.run')
    def test_flash_kernel(self, mock_run):
        with patch('device_manager.DeviceManager.verify_image', return_value=True):
            DeviceManager.flash_kernel("kernel.img")
            mock_run.assert_any_call(["fastboot", "flash", "boot", "kernel.img"], check=True)
    
    @patch('hashlib.sha256')
    def test_verify_image(self, mock_sha256):
        mock_sha256.return_value.hexdigest.return_value = "dummychecksum"
        result = DeviceManager.verify_image("dummy.img")
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()