"""Color editor widget with color picker."""
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, 
                             QColorDialog, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette


class ColorEditor(QWidget):
    """Widget for editing a single color with color picker."""
    
    colorChanged = pyqtSignal(str)  # Emits hex color string
    
    def __init__(self, label: str = "", range_text: str = "", parent=None):
        super().__init__(parent)
        self._current_color = QColor(255, 255, 255)
        self._range_text = range_text  # Store range text (e.g., "1-5")
        self._updating = False
        self._init_ui(label)
    
    def _init_ui(self, label: str):
        """Initialize the UI components."""
        from PyQt6.QtWidgets import QSizePolicy
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)  # Add small spacing between elements
        
        # Set minimum height for the editor to prevent squishing
        self.setMinimumHeight(35)
        
        # Label (always create, even if empty initially)
        self.label_widget = QLabel(label if label else "")
        self.label_widget.setMinimumWidth(120)  # Fixed width for label
        self.label_widget.setMaximumWidth(120)
        self.label_widget.setMinimumHeight(25)  # Ensure label has minimum height
        self.label_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.label_widget)
        
        # Color preview box - dark background with colored text showing range
        # Match button height (32px)
        self.color_preview = QLabel()
        self.color_preview.setMinimumSize(45, 32)  # Match button height
        self.color_preview.setMaximumSize(45, 32)
        self.color_preview.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.color_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the text
        self._update_preview()  # Initialize preview with range text
        layout.addWidget(self.color_preview)
        
        # Color picker button
        self.picker_button = QPushButton("Edit Colour")
        self.picker_button.setMinimumWidth(90)  # Wider for "Edit Colour" text
        self.picker_button.setMinimumHeight(32)  # Increased height
        self.picker_button.setMaximumHeight(32)  # Fixed height
        self.picker_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Fixed to match preview
        self.picker_button.clicked.connect(self._open_color_picker)
        layout.addWidget(self.picker_button)
        
        # No stretch - let the ColorGrid handle spacing
        self.setLayout(layout)
    
    
    def _open_color_picker(self):
        """Open colour picker dialog."""
        color = QColorDialog.getColor(self._current_color, self, "Edit Colour")
        if color.isValid():
            self.set_color(color.name())
    
    def _update_preview(self):
        """Update color preview box with dark background and colored range text."""
        # Set text to range (e.g., "1-5") or empty if no range
        display_text = self._range_text if self._range_text else ""
        self.color_preview.setText(display_text)
        
        # Style: dark background (#0a0f1e) with colored text (selected color)
        # No border, 4px border-radius
        color_hex = self._current_color.name()
        self.color_preview.setStyleSheet(
            f"background-color: #0a0f1e; "
            f"color: {color_hex}; "
            f"border: none; "
            f"border-radius: 4px; "
            f"font-weight: bold; "
            f"font-size: 13px;"  # Increased from 11px
        )
    
    
    def set_color(self, hex_color: str):
        """
        Set the color from a hex string.
        
        Args:
            hex_color: Hex color string (e.g., "#FF0000")
        """
        color = QColor(hex_color)
        if color.isValid():
            self._current_color = color
            self._update_preview()
            self.colorChanged.emit(hex_color)
    
    def get_color(self) -> str:
        """Get current color as hex string."""
        return self._current_color.name().upper()
    
    def get_color_rgba(self) -> tuple:
        """Get current color as RGBA tuple (0.0-1.0)."""
        r = self._current_color.red() / 255.0
        g = self._current_color.green() / 255.0
        b = self._current_color.blue() / 255.0
        a = self._current_color.alpha() / 255.0
        return (r, g, b, a)
    
    def set_label(self, label: str):
        """Update the label text."""
        if self.label_widget:
            self.label_widget.setText(label)
    
    def set_range_text(self, range_text: str):
        """Set the range text to display in the preview (e.g., '1-5')."""
        self._range_text = range_text
        self._update_preview()  # Update preview to show new range text


class ColorGrid(QWidget):
    """Grid of color editors for all attribute scales."""
    
    colorsChanged = pyqtSignal()
    
    def __init__(self, style_classes: list, ranges: list = None, parent=None):
        super().__init__(parent)
        self.style_classes = style_classes
        self.ranges = ranges if ranges is not None else []
        self.color_editors = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI with color editors for each scale."""
        from PyQt6.QtWidgets import QVBoxLayout, QGridLayout, QLabel, QSizePolicy
        
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)  # Add some padding
        layout.setSpacing(8)  # Add spacing between rows
        
        # Grid layout (removed header)
        grid = QGridLayout()
        grid.setColumnStretch(0, 0)  # Don't stretch the column - let editors size themselves
        grid.setSpacing(8)  # Add spacing between rows
        
        # Create color editor for each style class
        for i, style_class in enumerate(self.style_classes):
            # Clean up style class name for display (without range numbers)
            base_name = style_class.replace('attribute-colour-', '').replace('-', ' ').title()
            
            # Get range text for preview (e.g., "1-5")
            range_text = ""
            if i < len(self.ranges):
                min_val, max_val = self.ranges[i]
                range_text = f"{min_val}-{max_val}"
            
            # Display name without range numbers (just the base name)
            display_name = base_name
            
            editor = ColorEditor(display_name, range_text)
            editor.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
            editor.colorChanged.connect(self._on_color_changed)
            self.color_editors.append(editor)
            
            grid.addWidget(editor, i, 0)
        
        layout.addLayout(grid)
        # No stretch - let the parent grid layout handle spacing
        self.setLayout(layout)
    
    def _on_color_changed(self):
        """Handle color change in any editor."""
        self.colorsChanged.emit()
    
    def set_colors(self, colors: list):
        """
        Set colors from a list of hex strings.
        
        Args:
            colors: List of hex color strings
        """
        for editor, color in zip(self.color_editors, colors):
            if color:
                editor.set_color(color)
    
    def set_ranges(self, ranges: list):
        """
        Set ranges and update preview text only (not labels).
        
        Args:
            ranges: List of (min, max) tuples
        """
        self.ranges = ranges
        # Update only the range text in preview boxes, not the labels
        for i, editor in enumerate(self.color_editors):
            if i < len(self.ranges):
                min_val, max_val = self.ranges[i]
                range_text = f"{min_val}-{max_val}"
            else:
                range_text = ""
            editor.set_range_text(range_text)
    
    def get_colors(self) -> list:
        """Get all colors as hex strings."""
        return [editor.get_color() for editor in self.color_editors]
    
    def get_colors_rgba(self) -> list:
        """Get all colors as RGBA tuples."""
        return [editor.get_color_rgba() for editor in self.color_editors]

