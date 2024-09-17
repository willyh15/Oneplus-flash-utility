import logging
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QComboBox, QProgressBar
import sys
from device_manager import DeviceManager
from config_loader import load_config
from workflow_manager import WorkflowManager

# Initialize logging
logging.basicConfig(filename='flash_tool.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class FlashTool(QMainWindow):
    def __init__(self):
        super(FlashTool, self).__init__()
        self.config = load_config()
        self.device_profile = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("OnePlus 7 Pro Rooting Tool")
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle("User-Friendly Rescue Mode")
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle("Secure Rooting (Root + Encryption)")
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle("Web-Based Update Checker for ROMs & Kernels")
        self.setGeometry(300, 300, 800, 600)

        # Check ROM Update button
        self.button_check_rom_update = QPushButton(self)
        self.button_check_rom_update.setText("Check for ROM Updates")
        self.button_check_rom_update.setGeometry(50, 90, 400, 30)
        self.button_check_rom_update.clicked.connect(self.check_rom_update)

        # Check Kernel Update button
        self.button_check_kernel_update = QPushButton(self)
        self.button_check_kernel_update.setText("Check for Kernel Updates")
        self.button_check_kernel_update.setGeometry(50, 130, 400, 30)
        self.button_check_kernel_update.clicked.connect(self.check_kernel_update)

        # Status label to show the latest version
        self.label_status = QLabel(self)
        self.label_status.setGeometry(50, 170, 700, 30)

    def check_rom_update(self):
        if self.device_profile and "roms" in self.device_profile:
            for rom in self.device_profile["roms"]:
                version, download_url = DeviceManager.get_latest_release(rom["repo_url"])
                if version:
                    self.label_status.setText(f"Latest {rom['name']} version: {version}. Download: {download_url}")
                else:
                    self.label_status.setText(f"Failed to fetch update for {rom['name']}.")
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "No ROMs configured for this device.")

    def check_kernel_update(self):
        if self.device_profile and "kernel" in self.device_profile:
            version, download_url = DeviceManager.get_latest_release(self.device_profile["kernel"]["repo_url"])
            if version:
                self.label_status.setText(f"Latest Kernel version: {version}. Download: {download_url}")
            else:
                self.label_status.setText("Failed to fetch kernel update.")
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "No kernel configured for this device.")

        # Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(50, 400, 400, 30)
        self.progressBar.setValue(0)

        # Root device with encryption preservation button
        self.button_root_with_encryption = QPushButton(self)
        self.button_root_with_encryption.setText("Root Device (Preserve Encryption)")
        self.button_root_with_encryption.setGeometry(50, 90, 400, 30)
        self.button_root_with_encryption.clicked.connect(self.root_with_encryption)

        # Root device without encryption preservation button
        self.button_root_disable_encryption = QPushButton(self)
        self.button_root_disable_encryption.setText("Root Device (Disable Encryption)")
        self.button_root_disable_encryption.setGeometry(50, 130, 400, 30)
        self.button_root_disable_encryption.clicked.connect(self.root_without_encryption)

        

        # Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(50, 400, 400, 30)
        self.progressBar.setValue(0)

        # Rescue Mode button
        self.button_rescue_mode = QPushButton(self)
        self.button_rescue_mode.setText("One-Click Rescue Mode")
        self.button_rescue_mode.setGeometry(50, 90, 400, 30)
        self.button_rescue_mode.clicked.connect(self.enter_rescue_mode)

        # Dropdown for device selection
        self.device_dropdown = QComboBox(self)
        self.device_dropdown.setGeometry(50, 50, 400, 30)
        self.device_dropdown.addItem("OnePlus 7 Pro")
        self.device_dropdown.addItem("Pixel 5")

        # Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(50, 300, 400, 30)
        self.progressBar.setValue(0)

        # Root device button
        self.button_root_device = QPushButton(self)
        self.button_root_device.setText("Root Device")
        self.button_root_device.setGeometry(50, 90, 400, 30)
        self.button_root_device.clicked.connect(self.root_device)

        # Install Custom ROM button
        self.button_custom_rom = QPushButton(self)
        self.button_custom_rom.setText("Install Custom ROM")
        self.button_custom_rom.setGeometry(50, 130, 400, 30)
        self.button_custom_rom.clicked.connect(self.install_custom_rom)

        # Decrypt storage button
        self.button_decrypt_storage = QPushButton(self)
        self.button_decrypt_storage.setText("Decrypt Storage")
        self.button_decrypt_storage.setGeometry(50, 170, 400, 30)
        self.button_decrypt_storage.clicked.connect(self.decrypt_storage)

    def root_device(self):
        device = self.device_dropdown.currentText()
        workflow = WorkflowManager(self.progressBar, device, 'rooting')
        workflow.start()

    def load_logs(self):
    try:
        with open('flash_tool.log', 'r') as f:
            log_content = f.read()
            self.log_viewer.setPlainText(log_content)

        # Set a timer to refresh the log viewer every second (real-time updates)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.load_logs)
        self.timer.start(1000)  # Refresh every 1 second
    except FileNotFoundError:
        logging.warning("Log file not found.")
        self.log_viewer.setPlainText("No logs available.")

    def root_with_encryption(self):
        logging.info("Rooting device while preserving encryption.")
        DeviceManager.root_device(preserve_encryption=True)
        QtWidgets.QMessageBox.information(self, "Info", "Rooting completed with encryption preserved.")

    def root_without_encryption(self):
        logging.info("Rooting device with encryption disabled.")
        DeviceManager.root_device(preserve_encryption=False)
        QtWidgets.QMessageBox.information(self, "Info", "Rooting completed with encryption disabled.")

    def enter_rescue_mode(self):
        logging.info("Entering Rescue Mode.")
        success = DeviceManager.enter_rescue_mode()
        if success:
            QtWidgets.QMessageBox.information(self, "Info", "Rescue mode completed successfully.")
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to enter rescue mode. Check logs for details.")

    def install_custom_rom(self):
        rom_zip = QFileDialog.getOpenFileName(self, "Select Custom ROM ZIP", "", "Zip files (*.zip)")
        if rom_zip[0]:
            device = self.device_dropdown.currentText()
            workflow = WorkflowManager(self.progressBar, device, 'custom_rom', custom_rom=rom_zip[0])
            workflow.start()

    def decrypt_storage(self):
        device = self.device_dropdown.currentText()
        workflow = WorkflowManager(self.progressBar, device, 'decrypt')
        workflow.start()

def application():
    app = QApplication(sys.argv)
    window = FlashTool()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    application()
