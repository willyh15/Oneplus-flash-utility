import pytest
from unittest.mock import patch, mock_open
from device_manager import DeviceManager
import subprocess


@pytest.fixture(autouse=True)
def clear_logs(caplog):
    """Fixture to clear logs before each test."""
    caplog.clear()


@patch('builtins.open', new_callable=mock_open, read_data="dummy content")
@patch('os.path.exists', return_value=True)
@patch('device_manager.hashlib')
def test_verify_image(mock_hashlib, mock_exists, mock_open):
    mock_hash = mock_hashlib.sha256.return_value
    mock_hash.hexdigest.return_value = 'fakechecksum'

    result = DeviceManager.verify_image('dummy.img')
    assert result


@patch('subprocess.run')
def test_flash_rom(mock_subprocess):
    mock_subprocess.return_value = True
    result = DeviceManager.flash_rom("dummy_rom.zip")
    mock_subprocess.assert_called_once_with(["adb", "sideload", "dummy_rom.zip"], check=True)
    assert result


@patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'adb'))
def test_flash_rom_error(mock_subprocess, caplog):
    result = DeviceManager.flash_rom("dummy_rom.zip")
    assert not result
    assert "Failed to flash ROM" in caplog.text


@patch('subprocess.run')
def test_reboot_to_bootloader(mock_subprocess, caplog):
    mock_subprocess.return_value = True
    DeviceManager.reboot_to_bootloader()
    mock_subprocess.assert_called_once_with(["adb", "reboot", "bootloader"], check=True)
    assert "Rebooted to bootloader." in caplog.text


@patch('subprocess.run')
def test_flash_partition(mock_subprocess, caplog):
    mock_subprocess.return_value = True
    DeviceManager.flash_partition("dummy.img", "system")
    mock_subprocess.assert_called_once_with(["fastboot", "flash", "system", "dummy.img"], check=True)
    assert "Flashed system partition with dummy.img" in caplog.text


@patch('subprocess.run')
@patch('device_manager.DeviceManager.verify_image', return_value=True)
def test_flash_kernel(mock_verify_image, mock_subprocess, caplog):
    mock_subprocess.return_value = True
    DeviceManager.flash_kernel("dummy_kernel.img")
    mock_subprocess.assert_any_call(["adb", "reboot", "bootloader"], check=True)
    mock_subprocess.assert_any_call(["fastboot", "flash", "boot", "dummy_kernel.img"], check=True)
    assert "Flashed kernel: dummy_kernel.img" in caplog.text
