import os
import subprocess
import requests
import hashlib
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
import sys

class FlashTool(QMainWindow):
    def __init__(self):
        super(FlashTool, self).__init__()
        self.setWindowTitle("OnePlus 7 Pro Rooting Tool")
        self.setGeometry(300, 300, 500, 400)

        # Step Labels
        self.label = QLabel(self)
        self.label.setText("OnePlus 7 Pro Rooting Tool")
        self.label.adjustSize()
        self.label.move(150, 20)

        # Buttons for each step
        self.button_check_device = QPushButton(self)
        self.button_check_device.setText("Check Device Compatibility")
        self.button_check_device.clicked.connect(self.check_device_compatibility)
        self.button_check_device.setGeometry(50, 50, 400, 30)

        self.button_download_files = QPushButton(self)
        self.button_download_files.setText("Download Latest TWRP, Magisk")
        self.button_download_files.clicked.connect(self.download_files)
        self.button_download_files.setGeometry(50, 90, 400, 30)

        self.button_verify_integrity = QPushButton(self)
        self.button_verify_integrity.setText("Verify File Integrity")
        self.button_verify_integrity.clicked.connect(self.verify_file_integrity)
        self.button_verify_integrity.setGeometry(50, 130, 400, 30)

        self.button_flash_twrp = QPushButton(self)
        self.button_flash_twrp.setText("Flash TWRP and Magisk")
        self.button_flash_twrp.clicked.connect(self.flash_twrp_magisk)
        self.button_flash_twrp.setGeometry(50, 170, 400, 30)

        self.button_backup_restore = QPushButton(self)
        self.button_backup_restore.setText("Backup & Restore")
        self.button_backup_restore.clicked.connect(self.backup_restore)
        self.button_backup_restore.setGeometry(50, 210, 400, 30)

    def check_device_compatibility(self):
        try:
            # Detect connected device using adb
            device_info = subprocess.check_output(["adb", "devices"]).decode('utf-8')
            if "device" in device_info:
                QtWidgets.QMessageBox.information(self, "Info", f"Device detected: {device_info}")
            else:
                QtWidgets.QMessageBox.warning(self, "Error", "No compatible device detected. Make sure USB debugging is enabled.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error detecting device: {e}")

    def download_files(self):
        # Download the latest TWRP and Magisk from trusted sources
        twrp_url = "https://official-site.com/twrp.img"  # Example URL
        magisk_url = "https://github.com/topjohnwu/Magisk/releases/download/v23.0/Magisk-v23.0.zip"  # Example URL

        # Download TWRP image
        twrp_file = "twrp.img"
        magisk_file = "Magisk-v23.0.zip"

        self.download_file(twrp_url, twrp_file)
        self.download_file(magisk_url, magisk_file)

    def download_file(self, url, filename):
        try:
            response = requests.get(url, stream=True)
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            QtWidgets.QMessageBox.information(self, "Info", f"{filename} downloaded successfully!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error downloading {filename}: {e}")

    def verify_file_integrity(self):
        # Check the SHA256 checksum of the downloaded files
        self.verify_checksum("twrp.img", "expected_twrp_checksum")
        self.verify_checksum("Magisk-v23.0.zip", "expected_magisk_checksum")

    def verify_checksum(self, file_path, expected_checksum):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        actual_checksum = sha256_hash.hexdigest()

        if actual_checksum == expected_checksum:
            QtWidgets.QMessageBox.information(self, "Info", f"{file_path} checksum verified.")
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", f"{file_path} checksum mismatch!")

    def flash_twrp_magisk(self):
        twrp_img = "twrp.img"
        magisk_zip = "Magisk-v23.0.zip"
        subprocess.run(["adb", "reboot", "bootloader"])
        subprocess.run(["fastboot", "boot", twrp_img])
        QtWidgets.QMessageBox.information(self, "Info", "Phone rebooted into TWRP. Proceed to install TWRP and Magisk.")

    def backup_restore(self):
        # Add backup/restore functionality
        QtWidgets.QMessageBox.information(self, "Info", "Backup & Restore feature coming soon.")

def application():
    app = QApplication(sys.argv)
    window = FlashTool()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    application()
