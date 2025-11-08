"""Main application window."""
from pathlib import Path
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFileDialog, QTabWidget, QSplitter,
                             QMessageBox, QStatusBar, QLabel, QGroupBox, QTextEdit, QDialog, QDialogButtonBox,
                             QGridLayout, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from bundle_manager import BundleManager
from data_parser import DataParser
from backup_manager import BackupManager
from gui.threshold_editor import ThresholdEditor


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.fm_install_dir: Optional[str] = None
        self.bundle_manager: Optional[BundleManager] = None
        self.backup_manager: Optional[BackupManager] = None
        self.data_parser = DataParser()
        
        # Data storage
        self.attribute_data: Optional[Dict[str, Any]] = None
        self.thresholds: list = []
        self.style_classes: list = []
        self.all_thresholds: list = []  # Full thresholds including Unset/Low
        self.all_style_classes: list = []  # Full style classes including Unset/Low
        self.colors: list = []  # Colors for Default preset
        self.highlight_data_collection: Optional[Dict[str, Any]] = None
        self.highlight_no_border_collection: Optional[Dict[str, Any]] = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("FM26 Attribute Customizer - by MW90")
        self.setMinimumSize(460, 180)
        self.resize(460, 180)
        
        icon_path = Path(__file__).parent.parent / "icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        else:
            icon_path = Path(__file__).parent.parent / "icon.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid #555;
                border-radius: 3px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        dir_group = QGroupBox("FM Installation Directory")
        dir_group.setMaximumHeight(60)
        dir_layout = QHBoxLayout()
        dir_layout.setContentsMargins(10, 5, 10, 5)
        
        self.dir_label = QLabel("No directory selected")
        self.dir_label.setWordWrap(True)
        dir_layout.addWidget(self.dir_label, 1)
        
        self.select_dir_button = QPushButton("Browse")
        self.select_dir_button.clicked.connect(self._select_directory)
        dir_layout.addWidget(self.select_dir_button)
        
        dir_group.setLayout(dir_layout)
        main_layout.addWidget(dir_group)
        
        self.content_widget = QWidget()
        content_layout = QVBoxLayout()
        
        self.threshold_editor = ThresholdEditor([], [], [])
        self.threshold_editor.thresholdsChanged.connect(self._on_thresholds_changed)
        self.threshold_editor.colorsChanged.connect(self._on_colors_changed)
        self.threshold_editor.rowAdded.connect(self._on_add_row_requested)
        self.threshold_editor.rowRemoved.connect(self._on_remove_row_requested)
        self.threshold_editor.rowCountChanged.connect(self._on_row_count_changed)
        content_layout.addWidget(self.threshold_editor)
        
        highlight_group = QGroupBox("Attribute Highlighting")
        highlight_layout = QVBoxLayout()
        highlight_layout.setContentsMargins(10, 5, 10, 5)
        self.highlight_checkbox = QCheckBox("Highlight Attributes for Tactical Roles")
        self.highlight_checkbox.setToolTip("Enable/disable highlighting of attributes for tactical roles in the Player Profile and Popups")
        highlight_layout.addWidget(self.highlight_checkbox)
        highlight_group.setLayout(highlight_layout)
        content_layout.addWidget(highlight_group)
        
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 15, 0, 0)
        self.button_layout.setSpacing(10)
        
        self.restore_button = QPushButton("Restore Backup")
        self.restore_button.setEnabled(False)
        self.restore_button.clicked.connect(self._restore_backup)
        self.restore_button.hide()
        self.button_layout.addWidget(self.restore_button)
        
        self.button_layout.addStretch()
        
        self.save_button = QPushButton("Save Changes")
        self.save_button.setEnabled(False)
        self.save_button.setMinimumHeight(36)
        self.save_button.setMinimumWidth(120)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 13px;
                padding: 6px 14px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #666;
                color: #999;
            }
        """)
        self.save_button.clicked.connect(self._save_changes)
        self.save_button.hide()
        self.button_layout.addWidget(self.save_button)
        
        content_layout.addLayout(self.button_layout)
        
        self.content_widget.setLayout(content_layout)
        self.content_widget.setEnabled(False)
        self.content_widget.hide()
        main_layout.addWidget(self.content_widget)
        
        self.statusBar().showMessage("Ready - Select FM installation directory to begin")
    
    def _select_directory(self):
        """Open directory selection dialog."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select FM26 Installation Directory",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.fm_install_dir = directory
            self.dir_label.setText(directory)
            self._load_data()
    
    def _load_data(self):
        """Load data from bundle files."""
        if not self.fm_install_dir:
            return
        
        try:
            self.statusBar().showMessage("Loading bundle files...")
            self.bundle_manager = BundleManager(self.fm_install_dir)
            self.backup_manager = BackupManager(self.bundle_manager.bundle_dir)
            
            if not self.bundle_manager.bundle_dir.exists():
                QMessageBox.warning(
                    self,
                    "Directory Not Found",
                    f"Bundle directory not found:\n{self.bundle_manager.bundle_dir}\n\n"
                    "Please ensure you selected the correct FM installation directory."
                )
                return
            
            data_bundle_name = self.bundle_manager.get_data_collection_bundle_name()
            if not self.bundle_manager.bundle_exists(data_bundle_name):
                QMessageBox.warning(
                    self,
                    "Bundle Not Found",
                    f"Data bundle not found: {data_bundle_name}"
                )
                return
            
            attr_data_obj = self.bundle_manager.get_object_from_bundle(
                data_bundle_name,
                "AttributeDataCollection"
            )
            
            if attr_data_obj is None:
                QMessageBox.warning(
                    self,
                    "Data Not Found",
                    "AttributeDataCollection not found in bundle"
                )
                return
            
            self.statusBar().showMessage("Checking backups...")
            data_bundle_name = self.bundle_manager.get_data_collection_bundle_name()
            style_bundle_name = self.bundle_manager.get_style_bundle_name()
            
            data_bundle_path = self.bundle_manager.get_bundle_path(data_bundle_name)
            style_bundle_path = self.bundle_manager.get_bundle_path(style_bundle_name)
            
            backup_paths, created = self.backup_manager.create_backups([data_bundle_path, style_bundle_path], original=True)
            if created:
                self.statusBar().showMessage("Original backups created, loading data...")
            else:
                self.statusBar().showMessage("Loading data...")
            
            self.attribute_data = attr_data_obj
            
            parsed = self.data_parser.parse_attribute_data_collection(attr_data_obj)
            all_thresholds = parsed['thresholds']
            all_style_classes = parsed['style_classes']
            
            self.all_thresholds = all_thresholds
            self.all_style_classes = all_style_classes
            
            if len(all_style_classes) >= 2:
                self.thresholds = all_thresholds[2:]
                self.style_classes = all_style_classes[2:]
            else:
                self.thresholds = all_thresholds
                self.style_classes = all_style_classes
            
            style_bundle_name = self.bundle_manager.get_style_bundle_name()
            default_preset_obj = self.bundle_manager.get_object_from_bundle(
                style_bundle_name,
                "AttributeColoursDefault"
            )
            
            if default_preset_obj:
                colors_rgba = self.data_parser.extract_colors_from_rules(default_preset_obj)
                
                colors_hex = []
                for rgba in colors_rgba:
                    if len(rgba) >= 3:
                        hex_color = self.data_parser.rgba_to_hex(*rgba)
                        colors_hex.append(hex_color)
                    else:
                        colors_hex.append("#FFFFFF")
                
                if len(colors_hex) >= 2:
                    display_colors_hex = colors_hex[2:]
                else:
                    display_colors_hex = colors_hex
                
                while len(display_colors_hex) < len(self.style_classes):
                    display_colors_hex.append("#FFFFFF")
                
                self.colors = display_colors_hex[:len(self.style_classes)]
            else:
                self.colors = ["#FFFFFF"] * len(self.style_classes)
            data_bundle_name = self.bundle_manager.get_data_collection_bundle_name()
            self.highlight_data_collection = self.bundle_manager.get_object_from_bundle(
                data_bundle_name,
                "AttributeHighlightTypeDataCollection"
            )
            self.highlight_no_border_collection = self.bundle_manager.get_object_from_bundle(
                data_bundle_name,
                "AttributeHighlightTypeNoBorderDataCollection"
            )
            
            if self.highlight_data_collection:
                style_classes = self.data_parser.parse_attribute_highlight_collection(self.highlight_data_collection)
                if len(style_classes) >= 3:
                    if style_classes[0] == style_classes[1] == style_classes[2] == "attributes-row-number":
                        self.highlight_checkbox.setChecked(False)
                    else:
                        self.highlight_checkbox.setChecked(True)
                else:
                    self.highlight_checkbox.setChecked(True)
            else:
                self.highlight_checkbox.setChecked(True)
            
            if self.threshold_editor:
                try:
                    self.threshold_editor.thresholdsChanged.disconnect()
                    self.threshold_editor.colorsChanged.disconnect()
                    self.threshold_editor.rowAdded.disconnect()
                    self.threshold_editor.rowRemoved.disconnect()
                    self.threshold_editor.rowCountChanged.disconnect()
                except:
                    pass
                self.threshold_editor.thresholdsChanged.connect(self._on_thresholds_changed)
                self.threshold_editor.colorsChanged.connect(self._on_colors_changed)
                self.threshold_editor.rowAdded.connect(self._on_add_row_requested)
                self.threshold_editor.rowRemoved.connect(self._on_remove_row_requested)
                self.threshold_editor.rowCountChanged.connect(self._on_row_count_changed)
                self.threshold_editor.thresholds = self.thresholds.copy()
                self.threshold_editor.style_classes = self.style_classes.copy()
                self.threshold_editor.colors = self.colors.copy()
                self.threshold_editor.set_thresholds(self.thresholds)
                self.threshold_editor.set_colors(self.colors)
            
            self.content_widget.show()
            self.content_widget.setEnabled(True)
            self.save_button.show()
            self.save_button.setEnabled(True)
            self.restore_button.show()
            self.restore_button.setEnabled(True)
            
            self.setMinimumSize(460, 540)
            self._adjust_window_size()
            
            self.statusBar().showMessage("Data loaded successfully")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load data:\n{str(e)}"
            )
            self.statusBar().showMessage("Error loading data")
    
    def _on_thresholds_changed(self, thresholds: list):
        """Handle threshold changes."""
        self.thresholds = thresholds
        # Update full thresholds (preserve first 2 for Unset/Low)
        if len(self.all_thresholds) >= 2:
            self.all_thresholds = self.all_thresholds[:2] + thresholds
        else:
            self.all_thresholds = thresholds
        
        # Update style classes to match (preserve first 2 for Unset/Low)
        if len(self.all_style_classes) >= 2:
            self.all_style_classes = self.all_style_classes[:2] + self.style_classes
        else:
            self.all_style_classes = self.style_classes
        
        self.statusBar().showMessage("Thresholds updated")
    
    def _on_colors_changed(self):
        """Handle colour changes."""
        # Update colors from threshold editor
        if self.threshold_editor:
            self.colors = self.threshold_editor.get_colors()
        self.statusBar().showMessage("Colours updated")
    
    def _on_add_row_requested(self):
        """Handle request to add a new row before the last row."""
        if len(self.thresholds) >= 18:
            return  # Already checked in ThresholdEditor, but double-check
        
        # Calculate index (before last row)
        insert_index = len(self.thresholds) - 1
        
        # The new row's max value should always be (last row value - 1) = 19
        # This will cascade other rows if needed
        new_threshold = 19
        
        # Generate style class name
        # Find the highest custom number or start from 1
        max_custom_num = 0
        for style_class in self.style_classes:
            if style_class.startswith("attribute-colour-custom-"):
                try:
                    num = int(style_class.split("-")[-1])
                    max_custom_num = max(max_custom_num, num)
                except:
                    pass
        
        new_style_class = f"attribute-colour-custom-{max_custom_num + 1}"
        
        # Get color from adjacent row (previous row, or next row if no previous)
        if insert_index > 0 and insert_index - 1 < len(self.colors):
            new_color = self.colors[insert_index - 1]
        elif insert_index < len(self.colors):
            new_color = self.colors[insert_index]
        else:
            new_color = "#FFFFFF"  # Default white
        
        # Update threshold editor - it will handle the insertion
        # Insert after the first 3 fixed rows (Range 1, 2, 3), but before the last row
        # So new rows will appear as Range 4, 5, 6, etc., pushing the last row further down
        num_rows = len(self.threshold_editor.thresholds)
        
        # Insert at index 3 (after the first 3 fixed rows: Range 1, 2, 3)
        # This ensures new rows appear after Range 3 but before the last row
        editor_insert_index = 3
        
        # But make sure we don't insert at or after the last row
        # If we have 4 or fewer rows, insert before the last one
        if num_rows <= 4:
            editor_insert_index = num_rows - 1
        elif editor_insert_index >= num_rows - 1:
            # If index 3 would be at or after the last row, insert before the last row instead
            editor_insert_index = num_rows - 1
        
        # Ensure we have a valid index
        if editor_insert_index < 0:
            editor_insert_index = 0
        
        # Insert the row at the calculated index
        self.threshold_editor.add_row_at_index(editor_insert_index, new_threshold, new_style_class, new_color)
        
        # Sync our arrays with the editor's arrays after insertion
        # The editor has already inserted the row, so we just need to sync
        self.thresholds = self.threshold_editor.thresholds.copy()
        self.style_classes = self.threshold_editor.style_classes.copy()
        self.colors = self.threshold_editor.colors.copy()
        
        # Update all_thresholds and all_style_classes (includes Unset/Low)
        # The insert index in all_ arrays is editor_insert_index + 2 (for Unset/Low)
        # But we need to insert at the same relative position
        all_insert_index = editor_insert_index + 2
        # Only insert if not already present (editor already handled it in its arrays)
        # Actually, we need to sync all_ arrays to match the editor's state
        if len(self.all_thresholds) >= 2:
            # Remove the old editable thresholds (everything after index 1)
            self.all_thresholds = self.all_thresholds[:2] + self.thresholds
            self.all_style_classes = self.all_style_classes[:2] + self.style_classes
        else:
            self.all_thresholds = self.thresholds.copy()
            self.all_style_classes = self.style_classes.copy()
    
    def _on_remove_row_requested(self, index: int):
        """Handle request to remove a row at the given index."""
        if len(self.thresholds) <= 4:
            return
        
        if index == len(self.thresholds) - 1:
            return
        
        self.thresholds.pop(index)
        self.style_classes.pop(index)
        self.colors.pop(index)
        
        all_index = index + 2
        self.all_thresholds.pop(all_index)
        self.all_style_classes.pop(all_index)
        
        self.threshold_editor.remove_row_at_index(index)
        self.threshold_editor.set_colors(self.colors)
        self.threshold_editor.style_classes = self.style_classes.copy()
    
    def _adjust_window_size(self):
        """Adjust window size to accommodate content."""
        if not self.content_widget.isVisible():
            return
        
        base_height = 540
        row_height = 50
        num_rows = len(self.thresholds) if self.thresholds else 5
        
        new_height = base_height + (row_height * max(0, num_rows - 5))
        
        current_height = self.height()
        if new_height > current_height:
            self.resize(self.width(), new_height)
        self.setMinimumHeight(min(new_height, 800))
    
    def _on_row_count_changed(self):
        """Handle row count change - resize window to accommodate rows."""
        self._adjust_window_size()
    
    def _save_changes(self):
        """Save changes to bundle files."""
        if not self.bundle_manager or not self.backup_manager:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Save",
            "This will modify your FM26 game files.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            self.statusBar().showMessage("Saving changes...")
            
            # Get bundle paths
            data_bundle_name = self.bundle_manager.get_data_collection_bundle_name()
            style_bundle_name = self.bundle_manager.get_style_bundle_name()
            
            data_bundle_path = self.bundle_manager.get_bundle_path(data_bundle_name)
            style_bundle_path = self.bundle_manager.get_bundle_path(style_bundle_name)
            
            # Update attribute data collection
            # Use full thresholds and style classes (including Unset/Low) for saving
            updated_attr_data = self.data_parser.update_attribute_data_collection(
                self.attribute_data if self.attribute_data else {},
                self.all_thresholds,
                self.all_style_classes
            )
            
            # Prepare objects to write
            data_objects = {
                "AttributeDataCollection": updated_attr_data
            }
            
            # Update only AttributeColoursDefault
            default_preset_obj = self.bundle_manager.get_object_from_bundle(
                style_bundle_name,
                "AttributeColoursDefault"
            )
            
            style_objects = {}
            if default_preset_obj:
                # Get colors from threshold editor (only editable ones, without Unset/Low)
                editable_colors_hex = self.colors
                # Convert hex to RGBA
                editable_colors_rgba = []
                for hex_color in editable_colors_hex:
                    rgba = self.data_parser.hex_to_rgba(hex_color)
                    editable_colors_rgba.append(rgba)
                
                # Get original colors to preserve Unset and Low
                original_colors_rgba = self.data_parser.extract_colors_from_rules(default_preset_obj)
                
                # Combine: original first 2 colors (Unset/Low) + editable colors
                if len(original_colors_rgba) >= 2:
                    # Preserve first 2 colors (Unset/Low), then add editable ones
                    full_colors_rgba = original_colors_rgba[:2] + editable_colors_rgba
                else:
                    # Fallback if original doesn't have 2 colors
                    full_colors_rgba = editable_colors_rgba
                
                # Use full style classes (including Unset/Low) for saving
                updated_preset = self.data_parser.update_color_preset(
                    default_preset_obj,
                    full_colors_rgba,
                    self.all_style_classes
                )
                
                style_objects["AttributeColoursDefault"] = updated_preset
            
            # Update highlight collections
            if self.highlight_data_collection:
                highlight_enabled = self.highlight_checkbox.isChecked()
                updated_highlight_data = self.data_parser.update_attribute_highlight_collection(
                    self.highlight_data_collection,
                    highlight_enabled,
                    is_no_border=False
                )
                data_objects["AttributeHighlightTypeDataCollection"] = updated_highlight_data
            
            if self.highlight_no_border_collection:
                highlight_enabled = self.highlight_checkbox.isChecked()
                updated_highlight_no_border = self.data_parser.update_attribute_highlight_collection(
                    self.highlight_no_border_collection,
                    highlight_enabled,
                    is_no_border=True
                )
                data_objects["AttributeHighlightTypeNoBorderDataCollection"] = updated_highlight_no_border
            
            # Write bundles
            self.bundle_manager.write_bundle(data_bundle_name, data_objects)
            if style_objects:
                self.bundle_manager.write_bundle(style_bundle_name, style_objects)
            
            QMessageBox.information(
                self,
                "Save Complete",
                "Changes saved successfully!"
            )
            
            self.statusBar().showMessage("Changes saved successfully")
            
        except Exception as e:
            # Create a custom dialog with scrollable text for long error messages
            error_dialog = QDialog(self)
            error_dialog.setWindowTitle("Save Error")
            error_dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout(error_dialog)
            
            label = QLabel("Failed to save changes:")
            layout.addWidget(label)
            
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setPlainText(str(e))
            text_edit.setFontFamily("Courier")
            layout.addWidget(text_edit)
            
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            button_box.accepted.connect(error_dialog.accept)
            layout.addWidget(button_box)
            
            error_dialog.exec()
            self.statusBar().showMessage("Error saving changes")
    
    def _restore_backup(self):
        """Restore from original backup."""
        if not self.backup_manager:
            return
        
        data_bundle_name = self.bundle_manager.get_data_collection_bundle_name()
        style_bundle_name = self.bundle_manager.get_style_bundle_name()
        
        # Get original backups
        data_original = self.backup_manager.get_original_backup(data_bundle_name)
        style_original = self.backup_manager.get_original_backup(style_bundle_name)
        
        if not data_original and not style_original:
            QMessageBox.information(
                self,
                "No Original Backups",
                "No original backup files found. Original backups are created automatically on first load."
            )
            return
        
        # Confirm restore
        reply = QMessageBox.question(
            self,
            "Restore Original Files",
            "This will restore the original game files, discarding any changes you've made.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                data_bundle_path = self.bundle_manager.get_bundle_path(data_bundle_name)
                style_bundle_path = self.bundle_manager.get_bundle_path(style_bundle_name)
                
                # Restore original backups
                restored = False
                if data_original:
                    if self.backup_manager.restore_backup(data_original, data_bundle_path):
                        restored = True
                if style_original:
                    if self.backup_manager.restore_backup(style_original, style_bundle_path):
                        restored = True
                
                if restored:
                    QMessageBox.information(
                        self,
                        "Restore Complete",
                        "Original files restored successfully.\n\nReloading data..."
                    )
                    self.statusBar().showMessage("Original files restored, reloading data...")
                    # Reload data from the restored files
                    self._load_data()
                else:
                    QMessageBox.warning(
                        self,
                        "Restore Failed",
                        "Failed to restore one or more files."
                    )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Restore Error",
                    f"Failed to restore backup:\n{str(e)}"
                )

