from abc import ABC, abstractmethod

from PySide6.QtCore import Qt

from src.logic.commands import AddShapeCommand, MoveCommand
from src.logic.factory import ShapeFactory


class Tool(ABC):
    def __init__(self, view):
        self.view = view
        self.scene = view.scene

    @abstractmethod
    def mouse_press(self, event):
        pass

    @abstractmethod
    def mouse_move(self, event):
        pass

    @abstractmethod
    def mouse_release(self, event):
        pass


class SelectionTool(Tool):
    def __init__(self, view, undo_stack):
        super().__init__(view)
        self.undo_stack = undo_stack
        self.item_positions = {}

    def mouse_press(self, event):
        super(type(self.view), self.view).mousePressEvent(event)

        self.item_positions.clear()
        for item in self.scene.selectedItems():
            self.item_positions[item] = item.pos()

    def mouse_move(self, event):
        super(type(self.view), self.view).mouseMoveEvent(event)

        # Cursor logic
        item = self.view.itemAt(event.pos())
        if item:
            self.view.setCursor(Qt.ClosedHandCursor if event.buttons() & Qt.LeftButton else Qt.OpenHandCursor)
        else:
            self.view.setCursor(Qt.ArrowCursor)

    def mouse_release(self, event):
        super(type(self.view), self.view).mouseReleaseEvent(event)

        moved_items = []
        for item, old_pos in self.item_positions.items():
            new_pos = item.pos()
            if new_pos != old_pos:
                moved_items.append((item, old_pos, new_pos))

        if moved_items:
            self.undo_stack.beginMacro("Move Items")
            for item, old_pos, new_pos in moved_items:
                cmd = MoveCommand(item, old_pos, new_pos)
                self.undo_stack.push(cmd)
            self.undo_stack.endMacro()

        self.item_positions.clear()


class CreationTool(Tool):
    def __init__(self, view, shape_type, undo_stack):
        super().__init__(view)
        self.shape_type = shape_type
        self.undo_stack = undo_stack
        self.start_pos = None
        self.temp_shape = None

    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = self.view.mapToScene(event.pos())
            try:
                # Create a temporary shape for preview
                self.temp_shape = ShapeFactory.create_shape(
                    self.shape_type,
                    self.start_pos,
                    self.start_pos,
                    "#F2C94C"
                )
                self.scene.addItem(self.temp_shape)
            except ValueError:
                self.temp_shape = None

    def mouse_move(self, event):
        if self.start_pos and self.temp_shape:
            current_pos = self.view.mapToScene(event.pos())
            # Rubber banding: update geometry directly for preview
            self.temp_shape.set_geometry(self.start_pos, current_pos)

    def mouse_release(self, event):
        if self.start_pos and event.button() == Qt.LeftButton:
            if self.temp_shape:
                self.scene.removeItem(self.temp_shape)
                self.temp_shape = None

                end_pos = self.view.mapToScene(event.pos())
                try:
                    final_shape = ShapeFactory.create_shape(
                        self.shape_type,
                        self.start_pos,
                        end_pos,
                        "#F2C94C"
                    )

                    cmd = AddShapeCommand(self.scene, final_shape)
                    self.undo_stack.push(cmd)

                except ValueError:
                    pass

            self.start_pos = None
