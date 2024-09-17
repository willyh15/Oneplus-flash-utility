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
        self.setWindowTitle("Advanced Logging & Diagnostics")
        self.setGeometry(300, 300, 900, 700)
        self.setWindowTitle("EDL Mode Recovery Tool")
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle("Rooting Tool with Driver Management")
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle("Rooting Tool with Firmware Downloader")
        self.setGeometry(300, 300, 800, 600)

        # Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(50, 400, 400, 30)
        self.progressBar.setValue(0)

        # Download Firmware button
        self.button_download_firmware = QPushButton(self)
        self.button_download_firmware.setText("Download Firmware")
        self.button_download_firmware.setGeometry(50, 90, 400, 30)
        self.button_download_firmware.clicked.connect(self.download_firmware)

        # Download Kernel button
        self.button_download_kernel = QPushButton(self)
        self.button_download_kernel.setText("Download Kernel")
        self.button_download_kernel.setGeometry(50, 130, 400, 30)
        self.button_download_kernel.clicked.connect(self.download_kernel)

    def detect_and_load_device(self):
        detected_device = DeviceManager.detect_device()
        if detected_device:
            self.device_profile = DeviceManager.load_device_profile(detected_device, self.config)
            if self.device_profile:
                logging.info(f"Loaded device profile for: {detected_device}")
                QtWidgets.QMessageBox.information(self, "Info", f"Device detected: {detected_device}")
            else:
                QtWidgets.QMessageBox.warning(self, "Warning", f"No profile found for detected device: {detected_device}")
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "No device detected!")

    def download_rom(self):
    if self.device_profile and "roms" in self.device_profile:
        rom_urls = [rom["url"] for rom in self.device_profile["roms"]]
        selected_rom_url = self.select_rom(rom_urls)
        if selected_rom_url:
            save_path = QFileDialog.getSaveFileName(self, "Save ROM As", "", "Zip files (*.zip)")[0]
            if save_path:
                success = DeviceManager.download_firmware(selected_rom_url, save_path)
                if success:
                    QtWidgets.QMessageBox.information(self, "Info", "ROM downloaded successfully.")
    else:
        logging.warning("No ROMs available for the detected device.")
        QtWidgets.QMessageBox.warning(self, "Warning", "No ROMs available for this device!")


    def download_firmware(self):
        if self.device_profile and "stock_firmware" in self.device_profile:
            firmware_url = self.device_profile["stock_firmware"]["url"]
            expected_md5 = self.device_profile["stock_firmware"]["md5"]
            save_path = QFileDialog.getSaveFileName(self, "Save Firmware As", "", "Zip files (*.zip)")[0]
            if save_path:
                success = DeviceManager.download_and_verify_firmware(firmware_url, save_path, expected_md5)
                if success:
                    QtWidgets.QMessageBox.information(self, "Info", "Firmware downloaded and verified successfully.")
                else:
                    QtWidgets.QMessageBox.critical(self, "Error", "Failed to verify firmware. Check logs for details.")
        else:
            logging.warning("No stock firmware URL available for the detected device.")
            QtWidgets.QMessageBox.warning(self, "Warning", "No stock firmware available for this device!")

    def download_kernel(self):
        if self.device_profile and "kernel" in self.device_profile:
            kernel_url = self.device_profile["kernel"]["url"]
            expected_md5 = self.device_profile["kernel"]["md5"]
            save_path = QFileDialog.getSaveFileName(self, "Save Kernel As", "", "Image files (*.img)")[0]
            if save_path:
                success = DeviceManager.download_and_verify_firmware(kernel_url, save_path, expected_md5)
                if success:
                    QtWidgets.QMessageBox.information(self, "Info", "Kernel downloaded and verified successfully.")
                else:
                    QtWidgets.QMessageBox.critical(self, "Error", "Failed to verify kernel. Check logs for details.")
        else:
            logging.warning("No kernel URL available for the detected device.")
            QtWidgets.QMessageBox.warning(self, "Warning", "No kernel available for this device!")


        # Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(50, 400, 400, 30)
        self.progressBar.setValue(0)

        # Check ADB Driver button
        self.button_check_adb = QPushButton(self)
        self.button_check_adb.setText("Check ADB Driver")
        self.button_check_adb.setGeometry(50, 90, 400, 30)
        self.button_check_adb.clicked.connect(self.check_adb_driver)

        # Install ADB Driver button
        self.button_install_adb = QPushButton(self)
        self.button_install_adb.setText("Install ADB Driver (Windows)")
        self.button_install_adb.setGeometry(50, 130, 400, 30)
        self.button_install_adb.clicked.connect(self.install_adb_driver)

        # Check Fastboot Driver button
        self.button_check_fastboot = QPushButton(self)
        self.button_check_fastboot.setText("Check Fastboot Driver")
        self.button_check_fastboot.setGeometry(50, 170, 400, 30)
        self.button_check_fastboot.clicked.connect(self.check_fastboot_driver)

    def check_adb_driver(self):
        logging.info("Checking ADB driver...")
        if DeviceManager.check_adb_driver():
            QtWidgets.QMessageBox.information(self, "Info", "ADB driver is installed and working.")
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "ADB driver is not installed or not working properly.")

    def install_adb_driver(self):
        logging.info("Installing ADB driver for Windows...")
        if DeviceManager.install_adb_driver_windows():
            QtWidgets.QMessageBox.information(self, "Info", "ADB driver downloaded. Please install it manually.")
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to install ADB driver.")

    def check_fastboot_driver(self):
        logging.info("Checking Fastboot driver...")
        if DeviceManager.check_fastboot_driver():
            QtWidgets.QMessageBox.information(self, "Info", "Fastboot driver is installed and working.")
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Fastboot driver is not installed or not working properly.")

        # Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(50, 400, 400, 30)
        self.progressBar.setValue(0)

        # Check EDL Mode button
        self.button_check_edl = QPushButton(self)
        self.button_check_edl.setText("Check EDL Mode")
        self.button_check_edl.setGeometry(50, 90, 400, 30)
        self.button_check_edl.clicked.connect(self.check_edl_mode)

        # Flash Firmware in EDL Mode button
        self.button_flash_edl = QPushButton(self)
        self.button_flash_edl.setText("Flash Firmware (EDL Mode)")
        self.button_flash_edl.setGeometry(50, 130, 400, 30)
        self.button_flash_edl.clicked.connect(self.flash_edl_firmware)

    def check_edl_mode(self):
        if DeviceManager.check_edl_mode():
            QtWidgets.QMessageBox.information(self, "Info", "Device is in EDL mode and ready for flashing.")
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Device is not in EDL mode. Please boot into EDL mode.")

    def flash_edl_firmware(self):
        tool_path = QFileDialog.getOpenFileName(self, "Select EDL Tool (MsmDownloadTool or QFIL)", "", "Executable files (*.exe);;All files (*)")[0]
        firmware_path = QFileDialog.getOpenFileName(self, "Select Prebuilt Firmware", "", "All files (*)")[0]
        if tool_path and firmware_path:
            DeviceManager.flash_edl_firmware(tool_path, firmware_path)
            QtWidgets.QMessageBox.information(self, "Info", f"EDL tool launched. Select firmware: {firmware_path} in the tool.")
        else:
            logging.warning("No tool or firmware selected.")
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select the EDL tool and firmware file.")

        # Log Viewer (QTextEdit)
        self.log_viewer = QTextEdit(self)
        self.log_viewer.setGeometry(50, 50, 800, 400)
        self.log_viewer.setReadOnly(True)  # Set to read-only

        # Log Search field
        self.search_field = QLineEdit(self)
        self.search_field.setGeometry(50, 470, 400, 30)
        self.search_field.setPlaceholderText("Search logs...")

        # Search button
        self.button_search_logs = QPushButton(self)
        self.button_search_logs.setText("Search")
        self.button_search_logs.setGeometry(460, 470, 100, 30)
        self.button_search_logs.clicked.connect(self.search_logs)

        # Filter Dropdown (Errors/Warnings/Info)
        self.filter_dropdown = QComboBox(self)
        self.filter_dropdown.setGeometry(580, 470, 150, 30)
        self.filter_dropdown.addItem("All")
        self.filter_dropdown.addItem("Errors")
        self.filter_dropdown.addItem("Warnings")
        self.filter_dropdown.addItem("Info")
        self.filter_dropdown.currentIndexChanged.connect(self.filter_logs)

        # Export Logs button
        self.button_export_logs = QPushButton(self)
        self.button_export_logs.setText("Export Logs")
        self.button_export_logs.setGeometry(50, 510, 400, 30)
        self.button_export_logs.clicked.connect(self.export_logs)

        # Load logs from the log file and display them in the log viewer
        self.load_logs()

    def load_logs(self):
        # Load logs from the log file and display them in the log viewer
        try:
            with open('flash_tool.log', 'r') as f:
                log_content = f.read()
                self.log_viewer.setPlainText(log_content)
        except FileNotFoundError:
            logging.warning("Log file not found.")
            self.log_viewer.setPlainText("No logs available.")

    def search_logs(self):
        search_term = self.search_field.text()
        if search_term:
            logging.info(f"Searching for logs with term: {search_term}")
            with open('flash_tool.log', 'r') as f:
                results = [line for line in f if search_term.lower() in line.lower()]
                self.log_viewer.setPlainText(''.join(results))
        else:
            self.load_logs()

    def filter_logs(self):
        filter_type = self.filter_dropdown.currentText()
        with open('flash_tool.log', 'r') as f:
            if filter_type == "Errors":
                filtered_logs = [line for line in f if "ERROR" in line]
            elif filter_type == "Warnings":
                filtered_logs = [line for line in f if "WARNING" in line]
            elif filter_type == "Info":
                filtered_logs = [line for line in f if "INFO" in line]
            else:
                filtered_logs = f.readlines()
            self.log_viewer.setPlainText(''.join(filtered_logs))

    def export_logs(self):
        # Export the logs to a file
        save_path = QFileDialog.getSaveFileName(self, "Export Logs", "", "Log files (*.log)")[0]
        if save_path:
            with open('flash_tool.log', 'r') as f:
                log_content = f.read()
            with open(save_path, 'w') as export_file:
                export_file.write(log_content)
            QtWidgets.QMessageBox.information(self, "Info", f"Logs exported to {save_path}.")

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
