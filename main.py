"""Main entry point for FM26 Attribute Customizer."""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui.main_window import MainWindow


def get_icon_path():
    """Get the path to the icon file, handling both development and PyInstaller builds."""
    if getattr(sys, 'frozen', False):
        # Running from PyInstaller executable
        # Try to find icon in the same directory as the executable
        base_path = Path(sys.executable).parent
    else:
        # Running from source
        base_path = Path(__file__).parent
    
    # Try .ico first (Windows)
    icon_path = base_path / "icon.ico"
    if icon_path.exists():
        return str(icon_path)
    
    # Try .png as fallback
    icon_path = base_path / "icon.png"
    if icon_path.exists():
        return str(icon_path)
    
    return None


def main():
    """Launch the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("FM26 Attribute Customizer - by MW90")
    
    # Set application icon if available
    icon_path = get_icon_path()
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

