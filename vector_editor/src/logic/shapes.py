from abc import ABC, abstractmethod

from PySide6.QtGui import QPen, QColor, QPainterPath
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsItemGroup, QGraphicsItem


class ShapeMeta(type(QGraphicsItem), type(ABC)):
    pass


# Shape теперь наследуется от QGraphicsItem (как абстракция), но не QGraphicsPathItem.
# Или просто от ABC, но мы хотим type hinting.
# Лучше всего сделать его Mixin-ом, но так как мы используем методы QGraphicsItem (setFlag),
# то наследование от QGraphicsItem логично.
# Однако QGraphicsPathItem и QGraphicsItemGroup ОБА наследуются от QGraphicsItem.
# Python MRO справится с ромбовидным наследованием QGraphicsItem.

class Shape(QGraphicsItem, ABC, metaclass=ShapeMeta):
    def __init__(self, color: str = "black", stroke_width: int = 2):
        # ВАЖНО: Мы не вызываем super().__init__() здесь, так как Shape - это Mixin
        # и реальный __init__ будет вызван в QGraphicsPathItem/Group.
        # Но нам нужно инициализировать свои свойства.
        # Однако QGraphicsItem.__init__ нужно вызвать?
        # В PySide, если мы наследуемся от QGraphicsItem, мы должны вызывать super().__init__().
        # Но если Rectangle(QGraphicsPathItem, Shape), то QGraphicsPathItem.__init__ вызовет QGraphicsItem.__init__.
        # Если Shape вызовет super().__init__(), он может вызвать QGraphicsItem.__init__ второй раз?
        # Нет, MRO разрулит.
        #
        # НО! Group(QGraphicsItemGroup, Shape). QGraphicsItemGroup.__init__ вызывает QGraphicsItem.__init__.
        # Если Shape тоже вызывает super().__init__()...
        # Проще всего: Shape НЕ наследует QGraphicsItem явно в коде, но использует его методы.
        # Но для тайп-хинтинга это плохо.
        # Давайте попробуем сделать Shape(ABC) и использовать self как duck-typed.
        pass

    def _init_shape_properties(self, color: str, stroke_width: int):
        """Хелпер для инициализации свойств, который вызывает потомок"""
        self.color = color
        self.stroke_width = stroke_width
        self._setup_pen_if_possible()
        self._setup_flags()

    def _setup_pen_if_possible(self):
        # Group не имеет setPen. Rectangle имеет.
        if hasattr(self, "setPen"):
            pen = QPen(QColor(self.color))
            pen.setWidth(self.stroke_width)
            self.setPen(pen)

    def _setup_flags(self):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

    @property
    @abstractmethod
    def type_name(self) -> str:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @abstractmethod
    def set_geometry(self, start_point, end_point):
        pass

    def set_active_color(self, color: str):
        self.color = color
        self._setup_pen_if_possible()

    def set_stroke_width(self, width: int):
        self.stroke_width = width
        self._setup_pen_if_possible()


class Group(QGraphicsItemGroup, Shape):
    def __init__(self):
        super().__init__()
        # Инициализация флагов вручную, так как мы не вызываем специфичный init Shape
        # Или можно вызвать _init_shape_properties, но Group не имеет пера.
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItemGroup.GraphicsItemFlag.ItemIsMovable, True)
        self.setHandlesChildEvents(True)

    @property
    def type_name(self) -> str:
        return "group"

    def set_geometry(self, start, end):
        pass

    def set_active_color(self, color: str):
        for child in self.childItems():
            if isinstance(child, Shape):
                child.set_active_color(color)

    def set_stroke_width(self, width: int):
        for child in self.childItems():
            if isinstance(child, Shape):
                child.set_stroke_width(width)

    def to_dict(self) -> dict:
        children_data = []
        for child in self.childItems():
            if isinstance(child, Shape):
                children_data.append(child.to_dict())
        
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "children": children_data
        }


# Примитивы теперь наследуются от QGraphicsPathItem И Shape
class Rectangle(QGraphicsPathItem, Shape):
    def __init__(self, x, y, w, h, color="black", stroke_width=2):
        super().__init__() # QGraphicsPathItem init
        self._init_shape_properties(color, stroke_width)
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._create_geometry()

    def set_geometry(self, start_point, end_point):
        self._x = min(start_point.x(), end_point.x())
        self._y = min(start_point.y(), end_point.y())
        self._w = abs(end_point.x() - start_point.x())
        self._h = abs(end_point.y() - start_point.y())
        self._create_geometry()

    def _create_geometry(self):
        path = QPainterPath()
        path.addRect(self._x, self._y, self._w, self._h)
        self.setPath(path)

    @property
    def type_name(self) -> str:
        return "rect"

    def to_dict(self) -> dict:
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "props": {
                "x": self._x, "y": self._y,
                "w": self._w, "h": self._h,
                "color": self.pen().color().name(),
                "stroke_width": self.pen().width()
            }
        }


class Line(QGraphicsPathItem, Shape):
    def __init__(self, x1, y1, x2, y2, color="black", stroke_width=2):
        super().__init__()
        self._init_shape_properties(color, stroke_width)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self._create_geometry()

    def set_geometry(self, start_point, end_point):
        self.x1 = start_point.x()
        self.y1 = start_point.y()
        self.x2 = end_point.x()
        self.y2 = end_point.y()
        self._create_geometry()

    def _create_geometry(self):
        path = QPainterPath()
        path.moveTo(self.x1, self.y1)
        path.lineTo(self.x2, self.y2)
        self.setPath(path)

    @property
    def type_name(self) -> str:
        return "line"

    def to_dict(self) -> dict:
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "props": {
                "x1": self.x1, "y1": self.y1,
                "x2": self.x2, "y2": self.y2,
                "color": self.pen().color().name(),
                "stroke_width": self.pen().width()
            }
        }


class Ellipse(QGraphicsPathItem, Shape):
    def __init__(self, x, y, w, h, color="black", stroke_width=2):
        super().__init__()
        self._init_shape_properties(color, stroke_width)
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._create_geometry()

    def set_geometry(self, start_point, end_point):
        self._x = min(start_point.x(), end_point.x())
        self._y = min(start_point.y(), end_point.y())
        self._w = abs(end_point.x() - start_point.x())
        self._h = abs(end_point.y() - start_point.y())
        self._create_geometry()

    def _create_geometry(self):
        path = QPainterPath()
        path.addEllipse(self._x, self._y, self._w, self._h)
        self.setPath(path)

    @property
    def type_name(self) -> str:
        return "ellipse"

    def to_dict(self) -> dict:
        return {
            "type": self.type_name,
            "pos": [self.x(), self.y()],
            "props": {
                "x": self._x, "y": self._y,
                "w": self._w, "h": self._h,
                "color": self.pen().color().name(),
                "stroke_width": self.pen().width()
            }
        }
