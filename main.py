import logging
import json
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog,
                             QComboBox, QProgressBar, QTextEdit, QDialog, QVBoxLayout, QLabel, QListWidget)
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


class TaskManagerWindow(QDialog):
    """Task management window for viewing task states and details."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.setGeometry(500, 300, 600, 400)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Task list
        self.task_list = QListWidget()
        layout.addWidget(self.task_list)

        # Error suggestion box
        self.error_label = QLabel("Error Suggestions:")
        self.error_suggestions = QListWidget()
        layout.addWidget(self.error_label)
        layout.addWidget(self.error_suggestions)

        # Set the layout
        self.setLayout(layout)

    def update_tasks(self, task_name, status):
        """Add a new task with its status."""
        self.task_list.addItem(f"{task_name}: {status}")

    def add_suggestion(self, suggestion):
        """Add a recovery suggestion."""
        self.error_suggestions.addItem(suggestion)


class FlashTool(QMainWindow):
    def __init__(self):
        super(FlashTool, self).__init__()
        self.config = self.load_config()  # Load config from 'config.json'
        self.device_profile = None
        self.logcat_thread = None
        self.workflow_state = {}  # Workflow state tracking
        self.init_ui()
        self.task_manager = TaskManagerWindow()

    def init_ui(self):
        self.setWindowTitle("Rooting & Rescue Tool")
        self.setGeometry(300, 300, 900, 700)

        # Device dropdown
        self.device_dropdown = QComboBox(self)
        self.device_dropdown.setGeometry(50, 50, 400, 30)
        self.device_dropdown.addItems(self.config.keys())  # Populate based on config.json

        # Progress bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(50, 500, 400, 30)
        self.progressBar.setValue(0)

        # Add buttons for various actions
        self.add_button("Root Device (Preserve Encryption)", 90, self.root_with_encryption)
        self.add_button("Root Device (Disable Encryption)", 130, self.root_without_encryption)
        self.add_button("Install Custom ROM", 170, self.install_custom_rom)
        self.add_button("Flash Custom Kernel", 210, self.flash_kernel)
        self.add_button("Backup Before OTA Update", 250, self.backup_before_ota)
        self.add_button("Apply OTA Update & Preserve Root", 290, self.apply_ota_update)
        self.add_button("One-Click Rescue Mode", 330, self.enter_rescue_mode)

        # Task Manager button
        self.add_button("Open Task Manager", 370, self.open_task_manager)

        # Save and Load Workflow buttons
        self.add_button("Save Workflow", 410, self.save_workflow_state)
        self.add_button("Load Workflow", 450, self.load_workflow_state)

        # Logcat button
        self.button_logcat = QPushButton(self)
        self.button_logcat.setText("Start Logcat")
        self.button_logcat.setGeometry(50, 490, 400, 30)
        self.button_logcat.clicked.connect(self.toggle_logcat)

        # Log viewer
        self.log_viewer = QTextEdit(self)
        self.log_viewer.setGeometry(50, 530, 700, 150)
        self.log_viewer.setReadOnly(True)

    def add_button(self, label, y_position, function):
        button = QPushButton(self)
        button.setText(label)
        button.setGeometry(50, y_position, 400, 30)
        button.clicked.connect(function)

    def root_with_encryption(self):
        DeviceManager.root_device(preserve_encryption=True)
        self.task_manager.update_tasks("Root with Encryption", "Completed")
        self.workflow_state['root_with_encryption'] = 'Completed'
        QtWidgets.QMessageBox.information(self, "Info", "Rooting completed with encryption preserved.")

    def root_without_encryption(self):
        DeviceManager.root_device(preserve_encryption=False)
        self.task_manager.update_tasks("Root without Encryption", "Completed")
        self.workflow_state['root_without_encryption'] = 'Completed'
        QtWidgets.QMessageBox.information(self, "Info", "Rooting completed with encryption disabled.")

    def install_custom_rom(self):
        rom_zip = QFileDialog.getOpenFileName(self, "Select Custom ROM ZIP", "", "Zip files (*.zip)")[0]
        if rom_zip:
            success = DeviceManager.flash_rom(rom_zip)
            self.task_manager.update_tasks("Install Custom ROM", "Success" if success else "Failed")
            self.workflow_state['install_custom_rom'] = "Success" if success else "Failed"
            if success:
                QtWidgets.QMessageBox.information(self, "Info", "Custom ROM installed successfully.")
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "Custom ROM installation failed. Check logs for details.")

    def save_workflow_state(self):
        """Save the current workflow state to a file."""
        save_file = QFileDialog.getSaveFileName(self, "Save Workflow State", "", "JSON Files (*.json)")[0]
        if save_file:
            with open(save_file, 'w') as f:
                json.dump(self.workflow_state, f, indent=4)
            QtWidgets.QMessageBox.information(self, "Info", "Workflow state saved successfully.")

    def load_workflow_state(self):
        """Load the workflow state from a file."""
        load_file = QFileDialog.getOpenFileName(self, "Load Workflow State", "", "JSON Files (*.json)")[0]
        if load_file:
            with open(load_file, 'r') as f:
                self.workflow_state = json.load(f)
            self.task_manager.task_list.clear()
            for task, status in self.workflow_state.items():
                self.task_manager.update_tasks(task, status)
            QtWidgets.QMessageBox.information(self, "Info", "Workflow state loaded successfully.")

    def open_task_manager(self):
        self.task_manager.show()