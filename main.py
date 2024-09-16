from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QComboBox
import requests
import subprocess
import sys

class FlashTool(QMainWindow):
    def __init__(self):
        super(FlashTool, self).__init__()
        self.setWindowTitle("OnePlus 7 Pro Rooting Tool")
        self.setGeometry(300, 300, 500, 400)

        # Dropdown for device selection
        self.device_dropdown = QComboBox(self)
        self.device_dropdown.setGeometry(50, 50, 400, 30)
        self.device_dropdown.addItem("OnePlus 7 Pro")
        self.device_dropdown.addItem("Pixel 5")

        # Check latest versions
        self.button_check_latest = QPushButton(self)
        self.button_check_latest.setText("Check Latest Magisk Version")
        self.button_check_latest.setGeometry(50, 90, 400, 30)
        self.button_check_latest.clicked.connect(self.check_latest_magisk)

        # Flash custom ROM
        self.button_flash_rom = QPushButton(self)
        self.button_flash_rom.setText("Flash Custom ROM")
        self.button_flash_rom.setGeometry(50, 130, 400, 30)
        self.button_flash_rom.clicked.connect(self.flash_custom_rom)

        # Download TWRP
        self.button_download_twrp = QPushButton(self)
        self.button_download_twrp.setText("Download Latest TWRP")
        self.button_download_twrp.setGeometry(50, 170, 400, 30)
        self.button_download_twrp.clicked.connect(self.download_twrp)

    def check_latest_magisk(self):
        latest_version, download_url = self.get_latest_magisk_version()
        if latest_version:
            QtWidgets.QMessageBox.information(self, "Info", f"Latest Magisk version: {latest_version}\nDownload URL: {download_url}")
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to fetch latest Magisk version.")

    def get_latest_magisk_version(self):
        url = "https://api.github.com/repos/topjohnwu/Magisk/releases/latest"
        response = requests.get(url)
        if response.status_code == 200:
            latest_release = response.json()
            latest_version = latest_release["tag_name"]
            download_url = latest_release["assets"][0]["browser_download_url"]
            return latest_version, download_url
        else:
            return None, None

    def flash_custom_rom(self):
        rom_zip = QFileDialog.getOpenFileName(self, "Select Custom ROM ZIP", "", "Zip files (*.zip)")
        if rom_zip[0]:
            subprocess.run(["adb", "reboot", "bootloader"])
            subprocess.run(["fastboot", "flash", "recovery", rom_zip[0]])
            QtWidgets.QMessageBox.information(self, "Info", f"{rom_zip[0]} flashed successfully.")
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "No ROM selected!")

    def download_twrp(self):
        device = self.device_dropdown.currentText()
        twrp_url = self.get_device_twrp_url(device)
        if twrp_url:
            QtWidgets.QMessageBox.information(self, "Info", f"Download TWRP for {device} from: {twrp_url}")
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", f"No TWRP URL available for {device}")

    def get_device_twrp_url(self, device):
        config = {
            "OnePlus 7 Pro": "https://dl.twrp.me/guacamoleb/twrp-3.3.1-1-guacamoleb.img",
            "Pixel 5": "https://example.com/twrp_pixel5.img"
        }
        return config.get(device, None)

def application():
    app = QApplication(sys.argv)
    window = FlashTool()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    application()
