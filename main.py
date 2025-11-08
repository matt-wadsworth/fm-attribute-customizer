"""Main entry point for FM26 Attribute Customizer."""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from gui.main_window import MainWindow


def main():
    """Launch the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("FM26 Attribute Customizer - by MW90")
    
    # Set application icon if available
    icon_path = Path(__file__).parent / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    else:
        # Try PNG as fallback
        icon_path = Path(__file__).parent / "icon.png"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

