from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QUndoStack
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene

from src.logic.tools import SelectionTool, CreationTool
from src.logic.shapes import Group
from src.logic.commands import DeleteCommand


class EditorCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setSceneRect(0, 0, 800, 600)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setAlignment(Qt.AlignCenter)
        
        self.setMouseTracking(True)
        
        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(50)

        self.tools = {
            "select": SelectionTool(self, self.undo_stack),
            "rect": CreationTool(self, "rect", self.undo_stack),
            "line": CreationTool(self, "line", self.undo_stack),
            "ellipse": CreationTool(self, "ellipse", self.undo_stack)
        }
        
        self.current_tool = self.tools["select"]

    def set_tool(self, tool_name: str):
        if tool_name in self.tools:
            self.current_tool = self.tools[tool_name]
            if tool_name == "select":
                self.setCursor(Qt.ArrowCursor)
            else:
                self.setCursor(Qt.CrossCursor)

    def group_selection(self):
        selected_items = self.scene.selectedItems()

        if not selected_items:
            return

        group = Group()

        self.scene.addItem(group)

        for item in selected_items:
            item.setSelected(False)

            group.addToGroup(item)

        group.setSelected(True)
        print("Группа создана")

    def ungroup_selection(self):
        selected_items = self.scene.selectedItems()

        for item in selected_items:

            if isinstance(item, Group):
                self.scene.destroyItemGroup(item)
                print("Группа расформирована")

    def delete_selected(self):
        selected = self.scene.selectedItems()
        if not selected:
            return

        self.undo_stack.beginMacro("Delete Selection")
        
        for item in selected:
            cmd = DeleteCommand(self.scene, item)
            self.undo_stack.push(cmd)
            
        self.undo_stack.endMacro()

    def mousePressEvent(self, event):
        self.current_tool.mouse_press(event)

    def mouseMoveEvent(self, event):
        self.current_tool.mouse_move(event)

    def mouseReleaseEvent(self, event):
        self.current_tool.mouse_release(event)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
