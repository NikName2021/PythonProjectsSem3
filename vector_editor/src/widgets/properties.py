from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QSpinBox, QDoubleSpinBox, QPushButton, QColorDialog)

from src.logic.commands import ChangeColorCommand, ChangeWidthCommand


class PropertiesPanel(QWidget):
    def __init__(self, scene, undo_stack):
        super().__init__()
        self.scene = scene
        self.undo_stack = undo_stack

        self._init_ui()

        self.scene.selectionChanged.connect(self.on_selection_changed)

    def _init_ui(self):
        self.setFixedWidth(200)
        self.setStyleSheet("background-color: #f0f0f0; border-left: 1px solid #ccc;")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("Свойства")
        title.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")
        layout.addWidget(title)

        self.lbl_type = QLabel("Ничего не выбрано")
        self.lbl_type.setStyleSheet("color: black; font-style: italic; border: none; margin-bottom: 10px;")
        layout.addWidget(self.lbl_type)

        lb_width = QLabel("Толщина обводки:")
        lb_width.setStyleSheet("color: black;")
        layout.addWidget(lb_width)
        self.spin_width = QSpinBox()
        self.spin_width.setRange(1, 50)
        self.spin_width.valueChanged.connect(self.on_width_changed)
        layout.addWidget(self.spin_width)

        lb_color = QLabel("Цвет линии:")
        lb_color.setStyleSheet("color: black;")
        layout.addWidget(lb_color)
        self.btn_color = QPushButton()
        self.btn_color.setFixedHeight(30)
        self.btn_color.clicked.connect(self.on_color_clicked)
        layout.addWidget(self.btn_color)

        lb_geo = QLabel("Геометрия (X / Y):")
        lb_geo.setStyleSheet("color: black;")
        layout.addWidget(lb_geo)
        geo_layout = QHBoxLayout()

        self.spin_x = QDoubleSpinBox()
        self.spin_x.setRange(-10000, 10000)
        self.spin_x.setPrefix("X: ")
        self.spin_x.valueChanged.connect(self.on_geo_changed)

        self.spin_y = QDoubleSpinBox()
        self.spin_y.setRange(-10000, 10000)
        self.spin_y.setPrefix("Y: ")
        self.spin_y.valueChanged.connect(self.on_geo_changed)

        geo_layout.addWidget(self.spin_x)
        geo_layout.addWidget(self.spin_y)
        layout.addLayout(geo_layout)

        layout.addStretch()

        self.setEnabled(False)

    def on_selection_changed(self):
        try:
            selected_items = self.scene.selectedItems()
        except RuntimeError:
            return

        if not selected_items:
            self.setEnabled(False)
            self.lbl_type.setText("Ничего не выбрано")
            self.spin_width.setValue(1)
            self.btn_color.setStyleSheet("background-color: transparent")
            return

        self.setEnabled(True)
        item = selected_items[0]

        if hasattr(item, "type_name"):
            type_text = item.type_name.capitalize()
        else:
            type_text = type(item).__name__

        if len(selected_items) > 1:
            type_text += f" (+{len(selected_items) - 1})"
        self.lbl_type.setText(type_text)

        current_width = 1
        current_color = "#000000"

        if hasattr(item, "pen") and item.pen() is not None:
            current_width = item.pen().width()
            current_color = item.pen().color().name()

        self.spin_width.blockSignals(True)
        self.spin_width.setValue(current_width)
        self.spin_width.blockSignals(False)

        self.btn_color.setStyleSheet(f"background-color: {current_color}; border: 1px solid gray;")

        self.spin_x.blockSignals(True)
        self.spin_y.blockSignals(True)
        self.spin_x.setValue(item.x())
        self.spin_y.setValue(item.y())
        self.spin_x.blockSignals(False)
        self.spin_y.blockSignals(False)

    def on_width_changed(self, value):
        selected_items = self.scene.selectedItems()
        if not selected_items:
            return

        self.undo_stack.beginMacro("Change Width All")

        for item in selected_items:
            cmd = ChangeWidthCommand(item, value)
            self.undo_stack.push(cmd)

        self.undo_stack.endMacro()
        self.scene.update()

    def on_color_clicked(self):
        color = QColorDialog.getColor(title="Выберите цвет линии")
        if color.isValid():
            hex_color = color.name()
            self.btn_color.setStyleSheet(f"background-color: {hex_color}; border: 1px solid gray;")

            selected_items = self.scene.selectedItems()
            if not selected_items:
                return

            self.undo_stack.beginMacro("Change Color All")

            for item in selected_items:
                cmd = ChangeColorCommand(item, hex_color)
                self.undo_stack.push(cmd)

            self.undo_stack.endMacro()
            self.scene.update()

    def on_geo_changed(self, value):
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            new_x = self.spin_x.value()
            new_y = self.spin_y.value()
            item.setPos(new_x, new_y)
        self.scene.update()
