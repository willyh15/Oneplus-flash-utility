import logging
import json
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog,
                             QComboBox, QProgressBar, QTextEdit, QTableWidget, QTableWidgetItem)
import sys
import subprocess
import os
from device_manager import DeviceManager
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

class TaskManagerWindow(QTableWidget):
    """Manages task display and status updates."""
    def __init__(self):
        super(TaskManagerWindow, self).__init__(0, 2)
        self.setHorizontalHeaderLabels(["Task Name", "Status"])
        self.setColumnWidth(0, 250)
        self.setColumnWidth(1, 200)

    def update_tasks(self, task_name, status):
        """Update the task table with the current status."""
        row_count = self.rowCount()
        for row in range(row_count):
            if self.item(row, 0).text() == task_name:
                self.setItem(row, 1, QTableWidgetItem(status))
                return
        self.insertRow(row_count)
        self.setItem(row_count, 0, QTableWidgetItem(task_name))
        self.setItem(row_count, 1, QTableWidgetItem(status))

    def add_suggestion(self, suggestion):
        """Add a new suggestion to the suggestions box."""
        row_count = self.rowCount()
        self.insertRow(row_count)
        self.setItem(row_count, 0, QTableWidgetItem("Suggestion"))
        self.setItem(row_count, 1, QTableWidgetItem(suggestion))

class FlashTool(QMainWindow):
    def __init__(self):
        super(FlashTool, self).__init__()
        self.config = self.load_config()
        self.device_profile = None
        self.logcat_thread = None
        self.workflow_state = {}  # Workflow state tracking
        self.init_ui()
        self.task_manager = TaskManagerWindow()

    def init_ui(self):
        self.setWindowTitle("Rooting & Rescue Tool")
        self.setGeometry(300, 300, 1000, 600)

        # Device dropdown
        self.device_dropdown = QComboBox(self)
        self.device_dropdown.setGeometry(50, 50, 400, 30)
        self.device_dropdown.addItems(self.config.keys())  # Populate based on config.json

        # Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(50, 400, 400, 30)
        self.progressBar.setValue(0)

        # Task manager table
        self.task_manager.setGeometry(500, 50, 450, 300)
        self.setCentralWidget(self.task_manager)

        # Add buttons for various actions
        self.add_button("Root Device (Preserve Encryption)", 90, self.root_with_encryption)
        self.add_button("Root Device (Disable Encryption)", 130, self.root_without_encryption)
        self.add_button("Install Custom ROM", 170, self.install_custom_rom)
        self.add_button("Flash Custom Kernel", 210, self.flash_kernel)
        self.add_button("Backup Before OTA Update", 250, self.backup_before_ota)
        self.add_button("Apply OTA Update & Preserve Root", 290, self.apply_ota_update)
        self.add_button("One-Click Rescue Mode", 330, self.enter_rescue_mode)

        # Logcat button
        self.button_logcat = QPushButton(self)
        self.button_logcat.setText("Start Logcat")
        self.button_logcat.setGeometry(50, 370, 400, 30)
        self.button_logcat.clicked.connect(self.toggle_logcat)

        # Log viewer
        self.log_viewer = QTextEdit(self)
        self.log_viewer.setGeometry(50, 410, 900, 150)
        self.log_viewer.setReadOnly(True)

    def add_button(self, label, y_position, function):
        button = QPushButton(self)
        button.setText(label)
        button.setGeometry(50, y_position, 400, 30)
        button.clicked.connect(function)

    def root_with_encryption(self):
        success, error_code = DeviceManager.root_device(preserve_encryption=True)
        if success:
            self.task_manager.update_tasks("Root with Encryption", "Completed")
            self.workflow_state['root_with_encryption'] = 'Completed'
            QtWidgets.QMessageBox.information(self, "Info", "Rooting completed with encryption preserved.")
        else:
            self.handle_error("Root with Encryption", error_code)

    def root_without_encryption(self):
        success, error_code = DeviceManager.root_device(preserve_encryption=False)
        if success:
            self.task_manager.update_tasks("Root without Encryption", "Completed")
            self.workflow_state['root_without_encryption'] = 'Completed'
            QtWidgets.QMessageBox.information(self, "Info", "Rooting completed with encryption disabled.")
        else:
            self.handle_error("Root without Encryption", error_code)

    def install_custom_rom(self):
        rom_zip = QFileDialog.getOpenFileName(self, "Select Custom ROM ZIP", "", "Zip files (*.zip)")[0]
        if rom_zip:
            success, error_code = DeviceManager.flash_rom(rom_zip)
            if success:
                self.task_manager.update_tasks("Install Custom ROM", "Success")
                self.workflow_state['install_custom_rom'] = "Success"
                QtWidgets.QMessageBox.information(self, "Info", "Custom ROM installed successfully.")
            else:
                self.handle_error("Install Custom ROM", error_code)

    def flash_kernel(self):
        kernel_img = QFileDialog.getOpenFileName(self, "Select Custom Kernel Image", "", "Image files (*.img)")[0]
        if kernel_img:
            success, error_code = DeviceManager.flash_kernel(kernel_img)
            if success:
                self.task_manager.update_tasks("Flash Kernel", "Success")
                QtWidgets.QMessageBox.information(self, "Info", "Custom kernel flashed successfully.")
            else:
                self.handle_error("Flash Kernel", error_code)

    def handle_error(self, task_name, error_code):
        """Handle errors by updating TaskManagerWindow and providing suggestions."""
        error_message = DeviceManager.error_suggestions.get(error_code, "Unknown error.")
        self.task_manager.update_tasks(task_name, "Failed")
        self.task_manager.add_suggestion(f"{task_name}: {error_message}")
        QtWidgets.QMessageBox.critical(self, "Error", error_message)

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

    def load_config(self, config_file='config.json'):
        """Load configuration from a JSON file."""
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
        logging.exception("An unexpected error occurred during application execution.")