import unittest
from unittest.mock import patch
from device_manager import DeviceManager

class TestDeviceManager(unittest.TestCase):

    @patch('builtins.open', unittest.mock.mock_open(read_data="dummy content"))
    @patch('os.path.exists', return_value=True)
    @patch('device_manager.hashlib')
    def test_verify_image(self, mock_hashlib, mock_exists):
        # Mock the hashlib to avoid computing real checksums
        mock_hash = mock_hashlib.sha256.return_value
        mock_hash.hexdigest.return_value = 'fakechecksum'

        result = DeviceManager.verify_image('dummy.img')
        self.assertTrue(result)

    @patch('subprocess.run')
    def test_flash_rom(self, mock_subprocess):
        mock_subprocess.return_value = True  # Simulate success
        result = DeviceManager.flash_rom("dummy_rom.zip")
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()