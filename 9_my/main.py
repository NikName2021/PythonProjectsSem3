import sys

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QBrush, QPainter, QPen, QColor, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QGraphicsScene,
    QGraphicsView,
    QWidget, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QPushButton, QVBoxLayout,

)

from other import AnotherWindow

N = 50
T = 5


class Text(QGraphicsTextItem):
    def __init__(self, parent):
        super().__init__(parent)

    def mouseMoveEvent(self, event):
        pass


class Line(QGraphicsLineItem):
    def __init__(self, coords):
        super().__init__()
        self.x_start, self.y_start, self.x_end, self.y_end = coords
        self.setLine(*coords)
        self.setPen(QPen(Qt.GlobalColor.white, T))
        self.check = False

    def edit_color(self):
        if self.check:
            brush = QPen(Qt.GlobalColor.white, T)
            self.setPen(brush)
        else:
            brush = QPen(Qt.GlobalColor.red, T)
            self.setPen(brush)

    def mouseMoveEvent(self, event):
        pass

    def mousePressEvent(self, event):
        self.check = not self.check
        self.edit_color()

    def edit_coords_two(self, x, y):
        self.x_end, self.y_end = x, y
        self.setLine(self.x_start, self.y_start, self.x_end, self.y_end)

    def edit_coords_one(self, x, y):
        self.x_start, self.y_start = x, y
        self.setLine(self.x_start, self.y_start, self.x_end, self.y_end)


class NewElipse(QGraphicsEllipseItem):
    def __init__(self, x, y, id, text, scene):
        super().__init__(0, 0, N, N)
        self.setPos(x, y)
        brush = QBrush(Qt.GlobalColor.white)
        self.setBrush(brush)
        self.id = id
        self.main_scene = scene
        self.check = False
        self.lines = []
        self.text = text

    def mousePressEvent(self, QMouseEvent):
        self.check = not self.check
        self.edit_color()
        self.main_scene.work_cache(self)

    def edit_color(self):
        if self.check:
            brush = QBrush(Qt.GlobalColor.red)
        else:
            brush = QBrush(Qt.GlobalColor.white)
        self.setBrush(brush)

        # mouse hover event

    def hoverEnterEvent(self, event):
        app.instance().setOverrideCursor(Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        app.instance().restoreOverrideCursor()

    def mouseMoveEvent(self, event):
        orig_cursor_position = event.lastScenePos()
        updated_cursor_position = event.scenePos()

        orig_position = self.scenePos()

        updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
        updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
        self.setPos(QPointF(updated_cursor_x, updated_cursor_y))
        self.text.setPos(QPointF(updated_cursor_x, updated_cursor_y))

        for item, i in self.lines:
            if i == 1:
                item.edit_coords_two(updated_cursor_x + N // 2, updated_cursor_y + N // 2)

            elif i == 0:
                item.edit_coords_one(updated_cursor_x + N // 2, updated_cursor_y + N // 2)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(0, 0, 800, 800)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.button = QPushButton("Напечатать граф")
        self.button.clicked.connect(self.view_dict)

        hbox = QVBoxLayout(self)
        hbox.addWidget(self.view)
        hbox.addWidget(self.button)

        self.setLayout(hbox)
        self.w = None
        self.pointers = []
        self.cache = []
        self.graf = {}

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            az = self.view.mapFrom(self, e.pos())
            dc = self.view.mapToScene(az)
            self.create_point(dc)

    def create_point(self, dc):
        text = Text(str(len(self.pointers)))
        text.setDefaultTextColor(QColor("black"))
        text.setPos(dc.x() - N // 2, dc.y() - N // 2, )
        text.setFont(QFont("Arial", 20))

        elipse = NewElipse(dc.x() - N // 2, dc.y() - N // 2, len(self.pointers), text, self)
        self.pointers.append(elipse)
        self.scene.addItem(elipse)
        self.scene.addItem(text)

        self.graf[elipse.id] = []

    def work_cache(self, item):
        for i, ob in enumerate(self.cache):
            if ob.id == item.id:
                self.cache.pop(i)
                return

        if not len(self.cache):
            self.cache.append(item)
        elif len(self.cache) == 1 and self.cache[0].id != item.id:
            self.cache.append(item)

        if len(self.cache) == 2:
            self.create_connection()
            self.cache = []

        elif len(self.cache) > 2:
            for i in self.cache:
                i.color = False
                i.edit_color()
            self.cache = []

    def create_connection(self):

        point_0 = self.cache[0]
        point_1 = self.cache[1]
        if point_1.id in self.graf[point_0.id] and point_0.id in self.graf[point_1.id]:
            return

        x, y = point_0.x(), point_0.y()
        x1, y1 = point_1.x(), point_1.y()
        line = Line((x + N // 2, y + N // 2, x1 + N // 2, y1 + N // 2))

        point_0.lines.append((line, 0))
        point_1.lines.append((line, 1))
        self.scene.addItem(line)

        self.graf[point_0.id].append(point_1.id)
        self.graf[point_1.id].append(point_0.id)

        for point in self.cache:
            point.check = False
            point.edit_color()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Backspace:
            for point in self.cache:

                for line in point.lines:
                    self.scene.removeItem(line[0])
                self.graf.pop(point.id)

                for t in self.graf.keys():
                    if point.id in self.graf[t]:
                        self.graf[t].remove(point.id)

                self.scene.removeItem(point)
                self.scene.removeItem(point.text)
                self.cache = []

    def view_dict(self):
        for point, vals in sorted(self.graf.items()):
            print(point, vals)
        print("Матрица смежности")
        keys = sorted(self.graf.keys())

        matrix = []
        for i in keys:
            row = []
            for j in keys:
                row.append(int(j in self.graf[i]))
            matrix.append(row)

        print("№ " + " ".join(map(str, keys)))
        for j, i in enumerate(keys):
            print(i, ' '.join(map(str, matrix[j])))
        if matrix:
            self.w = AnotherWindow(matrix, keys)
            self.w.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec()
