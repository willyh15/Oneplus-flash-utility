import logging
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                             QComboBox, QProgressBar)
import sys
from device_manager import DeviceManager
import warnings
import subprocess
from config_loader import load_config

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

    def run(self):
        self.process = subprocess.Popen(["/usr/bin/adb", "logcat"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while self.running:
            log_line = self.process.stdout.readline().decode('utf-8')
            if log_line:
                self.new_log.emit(log_line.strip())

    def stop(self):
        self.running = False
        self.process.terminate()
        self.wait()

class FlashTool(QMainWindow):
    def __init__(self):
        super(FlashTool, self).__init__()
        self.config = load_config()
        self.device_profile = None
        self.logcat_thread = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Rooting & Rescue Tool")
        self.setGeometry(300, 300, 800, 600)

        # UI components (buttons, dropdowns, progress bar, etc.)
        self.device_dropdown = QComboBox(self)
        self.device_dropdown.setGeometry(50, 50, 400, 30)
        self.device_dropdown.addItem("OnePlus 7 Pro")
        self.device_dropdown.addItem("Pixel 5")

        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(50, 400, 400, 30)
        self.progressBar.setValue(0)

        self.add_button("Root Device (Preserve Encryption)", 90, self.root_with_encryption)
        self.add_button("Root Device (Disable Encryption)", 130, self.root_without_encryption)

    def add_button(self, label, y_position, function):
        button = QPushButton(self)
        button.setText(label)
        button.setGeometry(50, y_position, 400, 30)
        button.clicked.connect(function)

    def root_with_encryption(self):
        DeviceManager.root_device(preserve_encryption=True)
        QtWidgets.QMessageBox.information(self, "Info", "Rooting completed with encryption preserved.")

    def root_without_encryption(self):
        DeviceManager.root_device(preserve_encryption=False)
        QtWidgets.QMessageBox.information(self, "Info", "Rooting completed with encryption disabled.")

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

def application():
    app = QApplication(sys.argv)
    window = FlashTool()
    window.show()
    try:
        sys.exit(app.exec_())
    except Exception as e:
        logging.exception("An unexpected error occurred.")

if __name__ == "__main__":
    try:
        application()
    except Exception as e:
        logging.exception("An unexpected error occurred.")