import unittest
from unittest.mock import patch
from device_manager import DeviceManager
import logging
import subprocess


class TestDeviceManager(unittest.TestCase):

    @patch('builtins.open', unittest.mock.mock_open(read_data="dummy content"))
    @patch('os.path.exists', return_value=True)
    @patch('device_manager.hashlib')
    def test_verify_image(self, mock_hashlib, mock_exists):
        mock_hash = mock_hashlib.sha256.return_value
        mock_hash.hexdigest.return_value = 'fakechecksum'

        result = DeviceManager.verify_image('dummy.img')
        self.assertTrue(result)

    @patch('subprocess.run')
    def test_flash_rom(self, mock_subprocess):
        mock_subprocess.return_value = True
        result = DeviceManager.flash_rom("dummy_rom.zip")
        mock_subprocess.assert_called_once_with(["adb", "sideload", "dummy_rom.zip"], check=True)
        self.assertTrue(result)

    @patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'adb'))
    def test_flash_rom_error(self, mock_subprocess):
        result = DeviceManager.flash_rom("dummy_rom.zip")
        self.assertFalse(result)
        # Check for the specific error message in the logs
        self.assertIn("Failed to flash ROM", logging.getLogger().handlers[0].messages)

    @patch('subprocess.run')
    def test_reboot_to_bootloader(self, mock_subprocess):
        mock_subprocess.return_value = True
        DeviceManager.reboot_to_bootloader()
        mock_subprocess.assert_called_once_with(["adb", "reboot", "bootloader"], check=True)
        # Check for the expected log message
        self.assertIn("Rebooted to bootloader.", logging.getLogger().handlers[0].messages)

    @patch('subprocess.run')
    def test_flash_partition(self, mock_subprocess):
        mock_subprocess.return_value = True
        DeviceManager.flash_partition("dummy.img", "system")
        mock_subprocess.assert_called_once_with(["fastboot", "flash", "system", "dummy.img"], check=True)
        # Check for the expected log message
        self.assertIn("Flashed system partition with dummy.img", logging.getLogger().handlers[0].messages)

    @patch('device_manager.DeviceManager.verify_image', return_value=True)
    @patch('subprocess.run')  # Indentation fixed
    def test_flash_kernel(self, mock_verify_image, mock_subprocess):
        mock_subprocess.return_value = True
        DeviceManager.flash_kernel("dummy_kernel.img")
        mock_subprocess.assert_called_once_with(["adb", "reboot", "bootloader"], check=True)
        mock_subprocess.assert_called_once_with(["fastboot", "flash", "boot", "dummy_kernel.img"], check=True)
        # Check for the expected log message
        self.assertIn("Flashed kernel: dummy_kernel.img", logging.getLogger().handlers[0].messages)

if __name__ == '__main__':
    unittest.main()
