import json

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QFileDialog, QMessageBox)
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QFrame)

from src.logic.factory import ShapeFactory
from src.logic.strategies import JsonSaveStrategy, ImageSaveStrategy
from src.widgets.canvas import EditorCanvas
from src.widgets.properties import PropertiesPanel


class VectorEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vector Editor")
        self.resize(1000, 700)

        self._init_ui()

    def _init_ui(self):
        self.statusBar().showMessage("Ready")

        self.canvas = EditorCanvas()

        self.btn_select = QPushButton("Select")
        self.btn_line = QPushButton("Line")
        self.btn_rect = QPushButton("Rect")
        self.btn_ellipse = QPushButton("Ellipse")

        self.btn_select.setCheckable(True)
        self.btn_line.setCheckable(True)
        self.btn_rect.setCheckable(True)
        self.btn_ellipse.setCheckable(True)

        self.btn_select.setChecked(True)
        self.current_tool = "select"
        self.btn_rect.setChecked(False)

        self.btn_select.clicked.connect(lambda: self.on_change_tool("select"))
        self.btn_line.clicked.connect(lambda: self.on_change_tool("line"))
        self.btn_rect.clicked.connect(lambda: self.on_change_tool("rect"))
        self.btn_ellipse.clicked.connect(lambda: self.on_change_tool("ellipse"))

        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.on_open_clicked)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save_clicked)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Close the application")
        exit_action.triggered.connect(self.close)

        file_menu.addAction(exit_action)

        edit_menu = menubar.addMenu("&Edit")

        group_action = QAction("Group", self)
        group_action.setShortcut(QKeySequence("Ctrl+G"))
        group_action.triggered.connect(self.canvas.group_selection)

        ungroup_action = QAction("Ungroup", self)
        ungroup_action.setShortcut(QKeySequence("Ctrl+U"))
        ungroup_action.triggered.connect(self.canvas.ungroup_selection)

        edit_menu.addAction(group_action)
        edit_menu.addAction(ungroup_action)
        edit_menu.addSeparator()

        undo_stack = self.canvas.undo_stack
        undo_action = undo_stack.createUndoAction(self, "&Undo")
        undo_action.setShortcut(QKeySequence.Undo)

        redo_action = undo_stack.createRedoAction(self, "&Redo")
        redo_action.setShortcut(QKeySequence.Redo)

        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

        delete_action = QAction("Delete", self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.canvas.delete_selected)
        edit_menu.addAction(delete_action)
        self.addAction(delete_action)

        toolbar = self.addToolBar("Main Toolbar")
        toolbar.addAction(exit_action)
        toolbar.addAction(undo_action)
        toolbar.addAction(redo_action)

        self._setup_layout()

    def _setup_layout(self):
        container = QWidget()
        self.setCentralWidget(container)

        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)

        tools_panel = QFrame()
        tools_panel.setFixedWidth(120)
        tools_panel.setStyleSheet("background-color: #f0f0f0;")

        button_style = """
            QPushButton {
                background-color: #e0e0e0;
                color: black;
                border: 1px solid #c0c0c0;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:checked {
                background-color: #a0a0a0;
                border: 1px solid #808080;
                font-weight: bold;
            }
        """
        self.btn_select.setStyleSheet(button_style)
        self.btn_line.setStyleSheet(button_style)
        self.btn_rect.setStyleSheet(button_style)
        self.btn_ellipse.setStyleSheet(button_style)

        tools_layout = QVBoxLayout(tools_panel)
        tools_layout.addWidget(self.btn_select)
        tools_layout.addWidget(self.btn_line)
        tools_layout.addWidget(self.btn_rect)
        tools_layout.addWidget(self.btn_ellipse)
        tools_layout.addStretch()

        self.props_panel = PropertiesPanel(self.canvas.scene, self.canvas.undo_stack)

        main_layout.addWidget(tools_panel)
        main_layout.addWidget(self.canvas)
        main_layout.addWidget(self.props_panel)

    def reset_workspace(self):
        # 1. Clear Undo Stack FIRST
        self.canvas.undo_stack.clear()

        # 2. Clear Scene
        self.canvas.scene.clear()

    def on_save_clicked(self):
        filters = "Vector Project (*.json);;PNG Image (*.png);;JPEG Image (*.jpg)"
        filename, selected_filter = QFileDialog.getSaveFileName(
            self, "Save File", "", filters
        )

        if not filename:
            return

        strategy = None
        if filename.lower().endswith(".png"):
            strategy = ImageSaveStrategy("PNG", background_color="transparent")
        elif filename.lower().endswith(".jpg"):
            strategy = ImageSaveStrategy("JPG", background_color="white")
        else:
            strategy = JsonSaveStrategy()

        try:
            strategy.save(filename, self.canvas.scene)
            self.statusBar().showMessage(f"Successfully saved to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{str(e)}")

    def on_open_clicked(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "Vector Project (*.json *.vec)"
        )
        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not read file:\n{e}")
            return

        self.reset_workspace()

        scene_info = data.get("scene", {})
        width = scene_info.get("width", 800)
        height = scene_info.get("height", 600)
        self.canvas.scene.setSceneRect(0, 0, width, height)

        shapes_data = data.get("shapes", [])
        errors_count = 0

        self.canvas.scene.blockSignals(True)
        for shape_dict in shapes_data:
            try:
                shape_obj = ShapeFactory.from_dict(shape_dict)
                self.canvas.scene.addItem(shape_obj)
            except Exception as e:
                print(f"Error loading shape: {e}")
                errors_count += 1
        self.canvas.scene.blockSignals(False)
        self.canvas.scene.update()

        if errors_count > 0:
            self.statusBar().showMessage(f"Loaded with errors ({errors_count} skipped)")
        else:
            self.statusBar().showMessage(f"Project loaded: {path}")

    def on_change_tool(self, tool_name):
        self.current_tool = tool_name

        self.btn_select.setChecked(False)
        self.btn_line.setChecked(False)
        self.btn_rect.setChecked(False)
        self.btn_ellipse.setChecked(False)

        if tool_name == "select":
            self.btn_select.setChecked(True)
        elif tool_name == "line":
            self.btn_line.setChecked(True)
        elif tool_name == "rect":
            self.btn_rect.setChecked(True)
        elif tool_name == "ellipse":
            self.btn_ellipse.setChecked(True)

        self.canvas.set_tool(tool_name)
