import logging
import json
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog,
                             QComboBox, QProgressBar, QTextEdit)
import sys
import subprocess
import os
from device_manager import DeviceManager
from setup_manager import SetupManager
from log_manager import LogManager
from workflow_manager import WorkflowManager
import warnings


# Configure logging
logging.basicConfig(
    filename='flash_tool.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Suppress DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Function to log uncaught exceptions
def exception_hook(exc_type, exc_value, exc_traceback):
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.exit(1)

# Hook up uncaught exceptions
sys.excepthook = exception_hook

class LogcatThread(QtCore.QThread):
    new_log = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(LogcatThread, self).__init__(parent)
        self.running = True
        self.process = None

    def run(self):
        # Start adb logcat process
        self.process = subprocess.Popen(["adb", "logcat"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while self.running:
            log_line = self.process.stdout.readline().decode('utf-8')
            if log_line:
                self.new_log.emit(log_line.strip())

    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()
        self.wait()

class DeviceMonitorThread(QtCore.QThread):
    device_state_signal = QtCore.pyqtSignal(str)
    battery_level_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(DeviceMonitorThread, self).__init__(parent)
        self.running = True

    def run(self):
        while self.running:
            # Track device state
            device_state = DeviceManager.get_device_state()
            battery_level = DeviceManager.check_battery_level()
            
            # Emit signals for UI update
            self.device_state_signal.emit(device_state)
            self.battery_level_signal.emit(battery_level)

            # Check every 5 seconds
            self.sleep(5)

    def stop(self):
        self.running = False


class FlashTool(QMainWindow):
    def __init__(self):
        super(FlashTool, self).__init__()
        LogManager.configure_logger()
        self.config = load_config()
        self.device_profile = None
        self.logcat_thread = None
        self.device_monitor_thread = DeviceMonitorThread()  # Create device monitor thread
        self.device_monitor_thread.device_state_signal.connect(self.update_device_state)
        self.device_monitor_thread.battery_level_signal.connect(self.update_battery_level)
        self.init_ui()
        self.device_monitor_thread.start()  # Start monitoring




    def init_ui(self):
        self.setWindowTitle("Rooting & Rescue Tool")
        self.setGeometry(300, 300, 800, 600)

        # Device state label
        self.device_state_label = QtWidgets.QLabel("Device State: Unknown", self)
        self.device_state_label.setGeometry(50, 20, 400, 20)

        # Battery level label
        self.battery_level_label = QtWidgets.QLabel("Battery Level: Unknown", self)
        self.battery_level_label.setGeometry(500, 20, 200, 20)

        # Device dropdown
        self.device_dropdown = QComboBox(self)
        self.device_dropdown.setGeometry(50, 50, 400, 30)
        self.device_dropdown.addItems(self.config.keys())  # Populate based on config.json

        # Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(50, 400, 400, 30)
        self.progressBar.setValue(0)

        # Add buttons for various actions
        self.add_button("Root Device (Preserve Encryption)", 90, self.root_with_encryption)
        self.add_button("Root Device (Disable Encryption)", 130, self.root_without_encryption)
        self.add_button("Install Custom ROM", 170, self.install_custom_rom)
        self.add_button("Flash Custom Kernel", 210, self.flash_kernel)
        self.add_button("Backup Before OTA Update", 250, self.backup_before_ota)
        self.add_button("Apply OTA Update & Preserve Root", 290, self.apply_ota_update)
        self.add_button("One-Click Rescue Mode", 330, self.enter_rescue_mode)
        self.add_button("Export Logs", 450, self.export_logs)

        # Add buttons for workflow automation
        self.add_button("Full Device Reset", 370, self.run_full_device_reset)
        self.add_button("Automated Root & ROM Installation", 410, self.run_automated_root_and_rom)

        # Detect connected devices and populate dropdown
        self.connected_devices = DeviceManager.detect_connected_devices()
        self.device_dropdown = QComboBox(self)
        self.device_dropdown.setGeometry(50, 50, 400, 30)
        if self.connected_devices:
            self.device_dropdown.addItems(self.connected_devices)
        else:
            self.device_dropdown.addItem("No devices connected")

        # Check if the selected device is supported
        self.check_device_button = QPushButton(self)
        self.check_device_button.setText("Check Device Compatibility")
        self.check_device_button.setGeometry(50, 90, 400, 30)
        self.check_device_button.clicked.connect(self.check_device_compatibility)


         # Log Level Dropdown
        self.log_level_dropdown = QComboBox(self)
        self.log_level_dropdown.setGeometry(500, 50, 200, 30)
        self.log_level_dropdown.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_dropdown.currentTextChanged.connect(self.change_log_level)

        # Logcat button
        self.button_logcat = QPushButton(self)
        self.button_logcat.setText("Start Logcat")
        self.button_logcat.setGeometry(50, 370, 400, 30)
        self.button_logcat.clicked.connect(self.toggle_logcat)

        # Log viewer
        self.log_viewer = QTextEdit(self)
        self.log_viewer.setGeometry(50, 410, 700, 150)
        self.log_viewer.setReadOnly(True)

    def run_full_device_reset(self):
        workflow = WorkflowManager(self.device_dropdown.currentText(), self.progressBar)
        workflow.full_device_reset()

    def run_automated_root_and_rom(self):
        rom_zip = QFileDialog.getOpenFileName(self, "Select Custom ROM ZIP", "", "Zip files (*.zip)")[0]
        magisk_zip = QFileDialog.getOpenFileName(self, "Select Magisk ZIP", "", "Zip files (*.zip)")[0]
        if rom_zip and magisk_zip:
            workflow = WorkflowManager(self.device_dropdown.currentText(), self.progressBar)
            workflow.automated_root_and_rom_installation(rom_zip, magisk_zip)
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select both a ROM and a Magisk ZIP file.")


    def export_logs(self):
        """Allow the user to export the current log file."""
        export_file, _ = QFileDialog.getSaveFileName(self, "Export Logs", "", "Text Files (*.txt)")
        if export_file:
            try:
                with open('flash_tool.log', 'r') as log_file:
                    logs = log_file.read()
                with open(export_file, 'w') as export_file_obj:
                    export_file_obj.write(logs)
                QtWidgets.QMessageBox.information(self, "Info", f"Logs exported successfully to {export_file}.")
            except Exception as e:
                logging.error(f"Failed to export logs: {e}")
                QtWidgets.QMessageBox.critical(self, "Error", "Failed to export logs. Check log file for details.")


    def update_device_state(self, state):
        """Update the device state label based on the device monitor."""
        self.device_state_label.setText(f"Device State: {state}")
        logging.info(f"Device state updated: {state}")

    def update_battery_level(self, level):
        """Update the battery level label based on the device monitor."""
        self.battery_level_label.setText(f"Battery Level: {level}")
        logging.info(f"Battery level updated: {level}")


    def change_log_level(self, level_text):
        """Update log level based on user selection."""
        level = getattr(logging, level_text.upper(), logging.DEBUG)
        LogManager.change_log_level(level)
        QtWidgets.QMessageBox.information(self, "Info", f"Log level changed to: {level_text}")


    def check_device_compatibility(self):
        """Checks the compatibility of the selected device."""
        selected_device = self.device_dropdown.currentText()
        if selected_device == "No devices connected":
            QtWidgets.QMessageBox.warning(self, "Warning", "No devices connected. Please connect a device.")
        else:
            is_supported = DeviceManager.is_device_supported(selected_device)
            if is_supported:
                QtWidgets.QMessageBox.information(self, "Info", f"Device {selected_device} is supported.")
            else:
                QtWidgets.QMessageBox.critical(self, "Error", f"Device {selected_device} is not supported.")

    def add_button(self, label, y_position, function):
        button = QPushButton(self)
        button.setText(label)
        button.setGeometry(50, y_position, 400, 30)
        button.clicked.connect(function)

    def root_with_encryption(self):
        state = DeviceManager.get_device_state()
        if state != "device":
            QtWidgets.QMessageBox.warning(self, "Warning", f"Device is not in the correct state ({state}). Rebooting to normal mode.")
            DeviceManager.reboot_to_normal_mode()
        DeviceManager.root_device(preserve_encryption=True)
        QtWidgets.QMessageBox.information(self, "Info", "Rooting completed with encryption preserved.")

    def root_without_encryption(self):
        DeviceManager.root_device(preserve_encryption=False)
        QtWidgets.QMessageBox.information(self, "Info", "Rooting completed with encryption disabled.")

    def install_custom_rom(self):
        rom_zip = QFileDialog.getOpenFileName(self, "Select Custom ROM ZIP", "", "Zip files (*.zip)")[0]
        if rom_zip:
            success = DeviceManager.flash_rom(rom_zip)
            if success:
                QtWidgets.QMessageBox.information(self, "Info", "Custom ROM installed successfully.")
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "Custom ROM installation failed. Check logs for details.")

    def flash_kernel(self):
        kernel_img = QFileDialog.getOpenFileName(self, "Select Custom Kernel Image", "", "Image files (*.img)")[0]
        if kernel_img:
            success = DeviceManager.flash_kernel(kernel_img)
            if success:
                QtWidgets.QMessageBox.information(self, "Info", "Custom kernel flashed successfully.")
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "Kernel flashing failed. Check logs for details.")

    def enter_rescue_mode(self):
        success = DeviceManager.enter_rescue_mode()
        if success:
            QtWidgets.QMessageBox.information(self, "Info", "Rescue mode completed successfully.")
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to enter rescue mode. Check logs for details.")

    def backup_before_ota(self):
        success = DeviceManager.backup_device()
        if success:
            QtWidgets.QMessageBox.information(self, "Info", "Backup completed successfully.")
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Backup failed. Check logs for details.")

    def apply_ota_update(self):
        ota_zip = QFileDialog.getOpenFileName(self, "Select OTA Update ZIP", "", "Zip files (*.zip)")[0]
        if ota_zip:
            success = DeviceManager.apply_ota_update(ota_zip)
            if success:
                magisk_installed = DeviceManager.reflash_magisk_after_ota()
                if magisk_installed:
                    QtWidgets.QMessageBox.information(self, "Info", "OTA Update applied and Magisk re-flashed successfully.")
                else:
                    QtWidgets.QMessageBox.critical(self, "Error", "Magisk re-flashing failed. Root may be lost.")
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "OTA Update failed. Restoring from backup.")
                DeviceManager.restore_device()

    def toggle_logcat(self):
        if self.logcat_thread is None:
            self.start_logcat()
        else:
            self.stop_logcat()

    def start_logcat(self):
        self.button_logcat.setText("Stop Logcat")
        self.log_viewer.clear()
        self.logcat_thread = LogcatThread()
        self.logcat_thread.new_log.connect(self.update_log_viewer)
        self.logcat_thread.start()

    def stop_logcat(self):
        self.button_logcat.setText("Start Logcat")
        if self.logcat_thread:
            self.logcat_thread.stop()
        self.logcat_thread = None

    def update_log_viewer(self, log_line):
        self.log_viewer.append(log_line)

def load_config(config_file='config.json'):
    """Loads configuration from a JSON file."""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            logging.info(f"Loaded {config_file} successfully.")
            return config
    except FileNotFoundError:
        logging.warning(f"{config_file} not found. Creating default config.")
        default_config = {
            "oneplus7pro": {
                "twrp": "https://dl.twrp.me/guacamoleb/twrp-3.3.1-1-guacamoleb.img",
                "magisk": "https://github.com/topjohnwu/Magisk/releases/latest"
            }
        }
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding {config_file}: {e}")
        return {}

def application():
    app = QApplication(sys.argv)
    window = FlashTool()
    window.show()
    try:
        sys.exit(app.exec_())
    except Exception as _:
        logging.exception("An unexpected error occurred.")

if __name__ == "__main__":
    try:
        application()
    except Exception as e:
        logging.exception("An unexpected error occurred.")
