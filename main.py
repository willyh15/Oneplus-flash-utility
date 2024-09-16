import logging

# Setup logging
logging.basicConfig(filename='flash_tool.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Log application start
logging.info('Application started')

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QComboBox
import sys
from device_manager import DeviceManager
from config_loader import load_config

class FlashTool(QMainWindow):
    def __init__(self):
        super(FlashTool, self).__init__()
        self.config = load_config()
        self.init_ui()

    def init_ui(self):
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
        latest_version, download_url = DeviceManager.get_latest_magisk_version()
        if latest_version:
            QtWidgets.QMessageBox.information(self, "Info", f"Latest Magisk version: {latest_version}\nDownload URL: {download_url}")
            logging.info(f"Checked latest Magisk version: {latest_version}")
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to fetch latest Magisk version.")
            logging.error("Failed to fetch latest Magisk version.")

    def flash_custom_rom(self):
        rom_zip = QFileDialog.getOpenFileName(self, "Select Custom ROM ZIP", "", "Zip files (*.zip)")
        if rom_zip[0]:
            DeviceManager.reboot_to_bootloader()
            DeviceManager.flash_recovery(rom_zip[0])
            QtWidgets.QMessageBox.information(self, "Info", f"{rom_zip[0]} flashed successfully.")
            logging.info(f"Flashed custom ROM: {rom_zip[0]}")
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "No ROM selected!")
            logging.warning("No ROM selected for flashing.")

    def download_twrp(self):
        device = self.device_dropdown.currentText()
        twrp_url = DeviceManager.get_device_twrp_url(device, self.config)
        if twrp_url:
            QtWidgets.QMessageBox.information(self, "Info", f"Download TWRP for {device} from: {twrp_url}")
            logging.info(f"Download TWRP URL: {twrp_url}")
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", f"No TWRP URL available for {device}")
            logging.warning(f"No TWRP URL available for {device}")

def application():
    app = QApplication(sys.argv)
    window = FlashTool()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    application()
