"""Combined threshold and color editor widget."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QSpinBox, QGroupBox, QSizePolicy, QPushButton, QColorDialog, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor


class ThresholdEditor(QWidget):
    """Widget for editing attribute rating thresholds and colors in a row-based layout."""
    
    thresholdsChanged = pyqtSignal(list)
    colorsChanged = pyqtSignal()
    rowAdded = pyqtSignal()
    rowRemoved = pyqtSignal(int)
    rowCountChanged = pyqtSignal()
    
    def __init__(self, thresholds: list, style_classes: list, colors: list = None, parent=None):
        super().__init__(parent)
        self.thresholds = thresholds.copy()
        self.style_classes = style_classes.copy()
        self.colors = colors.copy() if colors else []
        self.min_labels = []
        self.max_spinboxes = []
        self.color_editors = []
        self.row_widgets = []
        self.remove_buttons = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI with row-based layout: Label - Min - Max - Preview - Edit Colour."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.thresholds_group = QGroupBox("Attributes", self)
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(10, 5, 10, 5)
        group_layout.setSpacing(5)
        
        desc = QLabel("Set the range and colour for each rating level.", self.thresholds_group)
        desc.setWordWrap(True)
        desc.setContentsMargins(0, 0, 0, 0)
        group_layout.addWidget(desc)
        
        self.rows_container = QWidget(self.thresholds_group)
        self.rows_layout = QVBoxLayout()
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(0)
        self.rows_container.setLayout(self.rows_layout)
        group_layout.addWidget(self.rows_container)
        
        self.add_row_button = QPushButton("Add Range", self.thresholds_group)
        self.add_row_button.clicked.connect(self._on_add_row_clicked)
        group_layout.addWidget(self.add_row_button)
        
        if hasattr(self, 'thresholds'):
            self._update_add_button_visibility()
        
        self.thresholds_group.setLayout(group_layout)
        layout.addWidget(self.thresholds_group)
        
        if len(self.thresholds) > 0:
            self._create_row_editors()
            self._update_add_button_visibility()
        
        layout.addStretch()
        self.setLayout(layout)
    
    def _create_row_editors(self):
        """Create row editors: Label - Min - Max - Preview - Edit Colour for each threshold."""
        if not isinstance(self.thresholds, list):
            raise TypeError(f"self.thresholds must be a list, got {type(self.thresholds)}")
        if not isinstance(self.style_classes, list):
            raise TypeError(f"self.style_classes must be a list, got {type(self.style_classes)}")
        
        if len(self.thresholds) != len(self.style_classes):
            raise ValueError(f"Thresholds ({len(self.thresholds)}) and style_classes ({len(self.style_classes)}) must have the same length")
        
        if len(self.thresholds) == 0:
            return
        
        for i, (threshold, style_class) in enumerate(zip(self.thresholds, self.style_classes)):
            if not isinstance(threshold, (int, float)):
                raise TypeError(f"Threshold at index {i} must be a number, got {type(threshold)}: {threshold}")
            if not isinstance(style_class, str):
                raise TypeError(f"Style class at index {i} must be a string, got {type(style_class)}: {style_class}")
            if i == 0:
                min_val = 1
            else:
                min_val = int(self.thresholds[i-1]) + 1
            max_val = int(threshold)
            is_last = (i == len(self.thresholds) - 1)
            if is_last:
                max_val = 20
                self.thresholds[i] = 20
            range_text = f"{min_val}-{max_val}"
            
            row_widget = QWidget(self.rows_container)
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(5, 8, 5, 8)
            row_layout.setSpacing(10)
            
            range_number = i + 1
            label = QLabel(f"Range {range_number}", row_widget)
            label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            row_layout.addWidget(label)
            
            removable_count = len(self.thresholds) - 4
            can_remove_this_row = not is_last and i < removable_count
            
            remove_button = None
            if can_remove_this_row:
                remove_button = QPushButton("×", row_widget)
                remove_button.setMinimumWidth(20)
                remove_button.setMaximumWidth(20)
                remove_button.setMinimumHeight(20)
                remove_button.setMaximumHeight(20)
                remove_button.setToolTip("Remove this range")
                remove_button.setStyleSheet(
                    "QPushButton {"
                    "background-color: #3a3a3a; "
                    "border: 1px solid #555; "
                    "border-radius: 2px; "
                    "color: #fff; "
                    "font-size: 12px; "
                    "font-weight: bold; "
                    "padding: 0px; "
                    "}"
                    "QPushButton:hover {"
                    "background-color: #cc0000; "
                    "border-color: #ff0000; "
                    "}"
                    "QPushButton:pressed {"
                    "background-color: #990000; "
                    "}"
                )
                remove_button.clicked.connect(lambda checked, idx=i: self._on_remove_row_clicked(idx))
                self.remove_buttons.append(remove_button)
                row_layout.addWidget(remove_button)
            else:
                self.remove_buttons.append(None)
            
            row_layout.addStretch()
            
            min_label = QLabel(f"{min_val} - ", row_widget)
            min_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            min_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            min_label.setStyleSheet(
                "QLabel {"
                "color: #ccc; "
                "background-color: transparent; "
                "border: none; "
                "padding: 0px; "
                "}"
            )
            self.min_labels.append(min_label)
            row_layout.addWidget(min_label)
            
            max_spin = QSpinBox(row_widget)
            max_spin.setMinimum(1)
            max_spin.setMaximum(20)
            max_spin.setValue(max_val)
            max_spin.setMinimumWidth(60)
            max_spin.setMaximumWidth(60)
            max_spin.setMinimumHeight(32)
            max_spin.setMaximumHeight(32)
            max_spin.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            is_last = (i == len(self.thresholds) - 1)
            if is_last:
                max_spin.setValue(20)
                max_spin.setEnabled(False)
            max_spin.valueChanged.connect(lambda val, idx=i: self._on_max_changed(idx, val))
            self.max_spinboxes.append(max_spin)
            row_layout.addWidget(max_spin)
            
            color_preview = QLabel(row_widget)
            color_preview.setMinimumSize(45, 32)
            color_preview.setMaximumSize(45, 32)
            color_preview.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            color_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            color_hex = self.colors[i] if i < len(self.colors) else "#FFFFFF"
            color_preview.setText(range_text)
            rgba = self._hex_to_rgba_css(color_hex)
            color_preview.setStyleSheet(
                f"background-color: #0a0f1e; "
                f"color: rgba({rgba}); "
                f"border: none; "
                f"border-radius: 4px; "
                f"font-weight: bold; "
                f"font-size: 13px;"
            )
            row_layout.addWidget(color_preview)
            
            pick_button = QPushButton("Edit Colour", row_widget)
            pick_button.setMinimumWidth(90)
            pick_button.setMinimumHeight(32)
            pick_button.setMaximumHeight(32)
            pick_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            pick_button.clicked.connect(lambda checked, idx=i, preview=color_preview: self._open_color_picker(idx, preview))
            row_layout.addWidget(pick_button)
            
            self.color_editors.append({
                'preview': color_preview,
                'button': pick_button,
                'color': color_hex,
                'range_text': range_text
            })
            
            row_widget.setLayout(row_layout)
            self.rows_layout.addWidget(row_widget)
            self.row_widgets.append(row_widget)
            
            if i < len(self.thresholds) - 1:
                divider = QFrame(self.rows_container)
                divider.setFrameShape(QFrame.Shape.HLine)
                divider.setFrameShadow(QFrame.Shadow.Sunken)
                divider.setFixedHeight(1)
                divider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                divider.setStyleSheet("background-color: #333; border: none; max-height: 1px; min-height: 1px; margin: 0px; padding: 0px;")
                self.rows_layout.addWidget(divider)
    
    def _open_color_picker(self, index: int, preview: QLabel):
        """Open color picker dialog for the given index."""
        current_color_hex = self.color_editors[index]['color']
        current_color = QColor(current_color_hex)
        if len(current_color_hex) == 9:
            hex_str = current_color_hex.lstrip('#')
            a = int(hex_str[6:8], 16)
            current_color.setAlpha(a)
        
        color = QColorDialog.getColor(
            current_color, 
            self, 
            "Edit Colour",
            QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        if color.isValid():
            r = color.red()
            g = color.green()
            b = color.blue()
            a = color.alpha()
            color_hex = f"#{r:02X}{g:02X}{b:02X}{a:02X}"
            self.set_color(index, color_hex)
    
    def set_color(self, index: int, hex_color: str):
        """Set color for a specific threshold index."""
        if index < len(self.color_editors):
            self.color_editors[index]['color'] = hex_color
            preview = self.color_editors[index]['preview']
            range_text = self.color_editors[index]['range_text']
            preview.setText(range_text)
            
            rgba = self._hex_to_rgba_css(hex_color)
            preview.setStyleSheet(
                f"background-color: #0a0f1e; "
                f"color: rgba({rgba}); "
                f"border: none; "
                f"border-radius: 4px; "
                f"font-weight: bold; "
                f"font-size: 13px;"
            )
            while len(self.colors) <= index:
                self.colors.append("#FFFFFF")
            self.colors[index] = hex_color
            self.colorsChanged.emit()
    
    def _hex_to_rgba_css(self, hex_color: str) -> str:
        """Convert hex color to CSS rgba() string."""
        hex_str = hex_color.lstrip('#')
        if len(hex_str) == 6:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return f"{r}, {g}, {b}, 1.0"
        elif len(hex_str) == 8:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            a = int(hex_str[6:8], 16) / 255.0
            return f"{r}, {g}, {b}, {a}"
        return "255, 255, 255, 1.0"
    
    def get_colors(self) -> list:
        """Get list of colors as hex strings."""
        return [editor['color'] for editor in self.color_editors]
    
    def set_colors(self, colors: list):
        """Set colors from a list of hex strings."""
        for i, color_hex in enumerate(colors):
            if i < len(self.color_editors):
                self.set_color(i, color_hex)
    
    def set_ranges(self, ranges: list):
        """Update range text in preview boxes when thresholds change."""
        for i, (min_val, max_val) in enumerate(ranges):
            if i < len(self.color_editors):
                range_text = f"{min_val}-{max_val}"
                self.color_editors[i]['range_text'] = range_text
                preview = self.color_editors[i]['preview']
                color_hex = self.color_editors[i]['color']
                preview.setText(range_text)
                rgba = self._hex_to_rgba_css(color_hex)
                preview.setStyleSheet(
                    f"background-color: #0a0f1e; "
                    f"color: rgba({rgba}); "
                    f"border: none; "
                    f"border-radius: 4px; "
                    f"font-weight: bold; "
                    f"font-size: 13px;"
                )
    
    def _calculate_min_value(self, index: int) -> int:
        """Calculate the min value for a threshold based on previous threshold's max."""
        if index == 0:
            return 1
        else:
            return self.thresholds[index - 1] + 1
    
    def _update_min_labels(self):
        """Update all min labels based on current max values."""
        for i in range(len(self.min_labels)):
            min_val = self._calculate_min_value(i)
            self.min_labels[i].setText(f"{min_val} - ")

    def _on_max_changed(self, index: int, value: int):
        """Handle maximum value change."""
        if index < len(self.thresholds):
            is_last = (index == len(self.thresholds) - 1)
            if is_last:
                if value != 20:
                    self.max_spinboxes[index].blockSignals(True)
                    self.max_spinboxes[index].setValue(20)
                    self.max_spinboxes[index].blockSignals(False)
                self.thresholds[index] = 20
                self._update_ranges()
                self.thresholdsChanged.emit(self.thresholds)
                return
            
            old_value = self.thresholds[index]

            min_value = self._calculate_min_value(index)
            
            if index < len(self.thresholds) - 1:
                next_min = self._calculate_min_value(index + 1)
                if value >= next_min:
                    required_min = value + 1
                    for i in range(index + 1, len(self.thresholds)):
                        if i < len(self.max_spinboxes):
                            current_max_spin = self.max_spinboxes[i]
                            current_max_value = current_max_spin.value()
                            
                            if i == index + 1:
                                required_min_for_this = value + 1
                            else:
                                required_min_for_this = self.thresholds[i - 1] + 1
                            
                            if current_max_value < required_min_for_this:
                                current_max_spin.blockSignals(True)
                                current_max_spin.setValue(required_min_for_this)
                                self.thresholds[i] = required_min_for_this
                                current_max_spin.blockSignals(False)
                                
                                self._update_min_labels()
                                
                                calculated_min = self._calculate_min_value(i)
                                if calculated_min == required_min_for_this:
                                    self._cascade_threshold_adjustment(i)
                            
                            required_min = self.thresholds[i] + 1
            
            if value < old_value:
                self.thresholds[index] = value
                
                for i in range(index - 1, -1, -1):
                    if i < len(self.max_spinboxes):
                        next_threshold_max = self.thresholds[i + 1]
                        new_max = next_threshold_max - 1
                        
                        if new_max >= 1:
                            current_max_spin = self.max_spinboxes[i]
                            current_max_value = current_max_spin.value()
                            
                            if current_max_value > new_max:
                                current_max_spin.blockSignals(True)
                                current_max_spin.setValue(new_max)
                                self.thresholds[i] = new_max
                                current_max_spin.blockSignals(False)
                                
                                calculated_min = self._calculate_min_value(i)
                                
                                if calculated_min == new_max:
                                    pass
                            else:
                                self.thresholds[i] = current_max_value
                
                for i in range(index + 1, len(self.thresholds)):
                    if i < len(self.max_spinboxes):
                        calculated_min = self._calculate_min_value(i)
                        
                        current_max_spin = self.max_spinboxes[i]
                        current_max_value = current_max_spin.value()
                        
                        new_max = current_max_value
                        
                        if current_max_value < calculated_min:
                            new_max = calculated_min
                        
                        if new_max != current_max_value:
                            current_max_spin.blockSignals(True)
                            current_max_spin.setValue(new_max)
                            self.thresholds[i] = new_max
                            current_max_spin.blockSignals(False)
                            
                            calculated_min = self._calculate_min_value(i)
                            
                            if calculated_min == new_max:
                                self._cascade_threshold_adjustment(i)
                        else:
                            self.thresholds[i] = current_max_value
                
                self._update_min_labels()
                self._update_ranges()
                self.thresholdsChanged.emit(self.thresholds)
                return
            
            self.thresholds[index] = value
            self._update_min_labels()
            self._update_ranges()
            self.thresholdsChanged.emit(self.thresholds)
    
    def _cascade_threshold_adjustment(self, index: int):
        """Cascade adjustment when a threshold's min and max become the same."""
        if index > 0 and index < len(self.max_spinboxes):
            current_min = self._calculate_min_value(index)
            current_max = self.max_spinboxes[index].value()
            
            if current_min == current_max:
                prev_max = current_max - 1
                if prev_max >= 1 and index - 1 < len(self.max_spinboxes):
                    prev_max_spin = self.max_spinboxes[index - 1]
                    prev_max_spin.blockSignals(True)
                    if prev_max_spin.value() > prev_max:
                        prev_max_spin.setValue(prev_max)
                        self.thresholds[index - 1] = prev_max
                        self._update_min_labels()
                        prev_min_calc = self._calculate_min_value(index - 1)
                        if prev_min_calc == prev_max:
                            self._cascade_threshold_adjustment(index - 1)
                    prev_max_spin.blockSignals(False)
    
    def _update_ranges(self):
        """Update the range text in color previews based on current threshold values."""
        for i in range(len(self.min_labels)):
            if i < len(self.max_spinboxes):
                min_val = self._calculate_min_value(i)
                max_val = self.max_spinboxes[i].value()
                range_text = f"{min_val}-{max_val}"
                
                if i < len(self.color_editors):
                    color_data = self.color_editors[i]
                    if 'preview' in color_data:
                        color_data['preview'].setText(range_text)
                        color_hex = color_data.get('color', '#FFFFFF')
                        rgba = self._hex_to_rgba_css(color_hex)
                        color_data['preview'].setStyleSheet(
                            f"background-color: #0a0f1e; "
                            f"color: rgba({rgba}); "
                            f"border: none; "
                            f"border-radius: 4px; "
                            f"font-weight: bold; "
                            f"font-size: 13px;"
                        )
    
    def set_thresholds(self, thresholds: list):
        """Set thresholds from a list."""
        self.thresholds = thresholds.copy()
        self._clear_editors()
        
        if len(self.thresholds) != len(self.style_classes):
            return
        
        if len(self.thresholds) > 0:
            self._create_row_editors()
            self._update_min_labels()
    
    def _clear_editors(self):
        """Clear all row editors."""
        self.color_editors.clear()
        
        if hasattr(self, 'rows_layout') and self.rows_layout:
            while self.rows_layout.count() > 0:
                item = self.rows_layout.takeAt(0)
                if item:
                    widget = item.widget()
                    if widget:
                        widget.hide()
                        widget.setParent(None)
                        widget.deleteLater()
        
        self.min_labels.clear()
        self.max_spinboxes.clear()
        self.row_widgets.clear()
        self.remove_buttons.clear()
    
    def get_thresholds(self) -> list:
        """Get current thresholds."""
        return self.thresholds.copy()
    
    def get_style_classes(self) -> list:
        """Get style classes."""
        return self.style_classes.copy()
    
    def get_ranges(self) -> list:
        """Get current ranges as list of (min, max) tuples."""
        ranges = []
        for i, threshold in enumerate(self.thresholds):
            if i < 2:
                continue
            min_val = 1 if i == 2 else self.thresholds[i-1]
            max_val = threshold - 1 if i < len(self.thresholds) else 20
            ranges.append((min_val, max_val))
        return ranges
    
    def _on_add_row_clicked(self):
        """Handle Add Row button click - add a new row before the last row."""
        if len(self.thresholds) >= 18:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Maximum Rows Reached",
                "You can have a maximum of 20 rows total (18 editable ranges)."
            )
            return
        
        self.rowAdded.emit()
    
    def _on_remove_row_clicked(self, index: int):
        """Handle Remove button click - remove a row at the given index."""
        if len(self.thresholds) <= 4:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Minimum Rows Required",
                "You must have at least 4 ranges."
            )
            return
        
        if index == len(self.thresholds) - 1:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Cannot Remove Last Row",
                "The last range cannot be removed."
            )
            return
        
        self.rowRemoved.emit(index)
    
    def add_row_at_index(self, index: int, threshold: int, style_class: str, color: str):
        """Add a new row at the specified index. Called by MainWindow."""
        threshold = min(threshold, 19)
        if index >= len(self.thresholds):
            index = len(self.thresholds) - 1 if len(self.thresholds) > 0 else 0
        elif index < 0:
            index = 0
        
        self.thresholds.insert(index, threshold)
        self.style_classes.insert(index, style_class)
        self.colors.insert(index, color)
        
        if len(self.thresholds) > 0:
            self.thresholds[-1] = 20
        
        self._clear_editors()
        self._create_row_editors()
        self._update_min_labels()
        self._update_ranges()
        
        if index < len(self.max_spinboxes):
            current_value = self.thresholds[index]
            self.max_spinboxes[index].blockSignals(True)
            self.max_spinboxes[index].setValue(current_value)
            self.max_spinboxes[index].blockSignals(False)
            
            self._on_max_changed(index, current_value)
        
        self._update_add_button_visibility()
        self._update_remove_buttons_visibility()
        
        self.thresholdsChanged.emit(self.thresholds)
        self.colorsChanged.emit()
        
        self.rowCountChanged.emit()
    
    def _validate_all_rows_after_insertion(self, start_index: int):
        """Validate and fix all rows after inserting a new row, working backwards from the last row."""
        if start_index < len(self.thresholds) and start_index < len(self.max_spinboxes):
            current_max = self.thresholds[start_index]
            if current_max > 19:
                current_max = 19
                self.max_spinboxes[start_index].blockSignals(True)
                self.max_spinboxes[start_index].setValue(19)
                self.max_spinboxes[start_index].blockSignals(False)
                self.thresholds[start_index] = 19
        
        for i in range(len(self.thresholds) - 1, start_index - 1, -1):
            if i < len(self.max_spinboxes):
                calculated_min = self._calculate_min_value(i)
                current_max = self.thresholds[i]
                
                if i == len(self.thresholds) - 1:
                    if current_max != 20:
                        self.max_spinboxes[i].blockSignals(True)
                        self.max_spinboxes[i].setValue(20)
                        self.max_spinboxes[i].setEnabled(False)
                        self.max_spinboxes[i].blockSignals(False)
                        self.thresholds[i] = 20
                else:
                    next_min = self._calculate_min_value(i + 1)
                    max_allowed = next_min - 1
                    
                    new_max = max(calculated_min, current_max)
                    new_max = min(new_max, max_allowed)
                    new_max = min(new_max, 19)
                    
                    if calculated_min > max_allowed:
                        new_max = max_allowed
                        new_max = max(1, new_max)
                    
                    if new_max != current_max:
                        self.max_spinboxes[i].blockSignals(True)
                        self.max_spinboxes[i].setValue(new_max)
                        self.thresholds[i] = new_max
                        self.max_spinboxes[i].blockSignals(False)
        
        for i in range(start_index, len(self.thresholds)):
            if i < len(self.max_spinboxes):
                calculated_min = self._calculate_min_value(i)
                current_max = self.thresholds[i]
                
                if i == len(self.thresholds) - 1:
                    if current_max != 20:
                        self.max_spinboxes[i].blockSignals(True)
                        self.max_spinboxes[i].setValue(20)
                        self.max_spinboxes[i].setEnabled(False)
                        self.max_spinboxes[i].blockSignals(False)
                        self.thresholds[i] = 20
                else:
                    if current_max < calculated_min:
                        new_max = calculated_min
                        new_max = min(new_max, 19)
                        
                        self.max_spinboxes[i].blockSignals(True)
                        self.max_spinboxes[i].setValue(new_max)
                        self.thresholds[i] = new_max
                        self.max_spinboxes[i].blockSignals(False)
        
        if len(self.thresholds) > 0:
            last_index = len(self.thresholds) - 1
            self.thresholds[last_index] = 20
            if last_index < len(self.max_spinboxes):
                self.max_spinboxes[last_index].blockSignals(True)
                self.max_spinboxes[last_index].setValue(20)
                self.max_spinboxes[last_index].setEnabled(False)
                self.max_spinboxes[last_index].blockSignals(False)
        
        self._update_min_labels()
        self._update_ranges()
    
    def remove_row_at_index(self, index: int):
        """Remove a row at the specified index. Called by MainWindow."""
        self.thresholds.pop(index)
        self.style_classes.pop(index)
        self.colors.pop(index)
        
        self._clear_editors()
        self._create_row_editors()
        self._update_min_labels()
        self._update_ranges()
        
        self._update_add_button_visibility()
        self._update_remove_buttons_visibility()
        
        self.thresholdsChanged.emit(self.thresholds)
        self.colorsChanged.emit()
        
        self.rowCountChanged.emit()
    
    def _update_add_button_visibility(self):
        """Update visibility of Add Row button based on row count."""
        if hasattr(self, 'add_row_button'):
            self.add_row_button.setEnabled(len(self.thresholds) < 18)
    
    def _update_remove_buttons_visibility(self):
        """Update visibility of remove buttons based on row count."""
        removable_count = len(self.thresholds) - 4
        for i, button in enumerate(self.remove_buttons):
            if button is not None:
                is_last = (i == len(self.thresholds) - 1)
                can_remove_this_row = not is_last and i < removable_count
                button.setVisible(can_remove_this_row)