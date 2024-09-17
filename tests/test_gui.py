import pytest
from PyQt5.QtWidgets import QApplication
from main import FlashTool

# Required for running PyQt app tests
@pytest.fixture(scope='module')
def app():
    app = QApplication([])
    return app

def test_initial_ui_state(qtbot):
    """Test the initial state of the FlashTool UI."""
    window = FlashTool()
    
    # Using qtbot to add the window for interaction
    qtbot.addWidget(window)
    
    # Check window properties
    assert window.windowTitle() == "Rooting & Rescue Tool"
    assert window.device_dropdown.count() == 2  # Check if two devices are listed
    assert window.progressBar.value() == 0  # Progress bar should start at 0

def test_device_selection(qtbot):
    """Test the device dropdown interaction."""
    window = FlashTool()
    qtbot.addWidget(window)
    
    # Select the second device in the dropdown
    window.device_dropdown.setCurrentIndex(1)
    assert window.device_dropdown.currentText() == "Pixel 5"

def test_rom_installation(qtbot, monkeypatch):
    """Test ROM installation by simulating the ROM selection."""
    window = FlashTool()
    qtbot.addWidget(window)
    
    # Mock the QFileDialog to return a fixed file path
    monkeypatch.setattr('PyQt5.QtWidgets.QFileDialog.getOpenFileName', lambda *args: ("test_rom.zip", ""))
    
    # Simulate the click on the "Install Custom ROM" button
    qtbot.mouseClick(window.findChild(QtWidgets.QPushButton, "Install Custom ROM"), QtCore.Qt.LeftButton)
    
    # You would assert whatever behavior occurs after the ROM is installed (e.g., log, message box, etc.)
    # For simplicity, let's assume it logs the success
    assert "Custom ROM installed successfully." in window.statusBar().currentMessage()