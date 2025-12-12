import sys
import re

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QFont
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QLineEdit, QPushButton, QLabel)


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.p = []
        self.q = []
        self.a = []
        self.min_x = 0
        self.max_x = 100

    def set_data(self, p, q, a):
        self.p = p
        self.q = q
        self.a = a
        all_vals = p + q + a
        if all_vals:
            self.min_x = min(all_vals) - 5
            self.max_x = max(all_vals) + 5
        self.update()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        range_len = self.max_x - self.min_x
        if range_len == 0:
            range_len = 1

        def to_x(val):
            return int((val - self.min_x) / range_len * (w - 20)) + 10

        self.draw_seg(qp, self.p, 50, Qt.GlobalColor.blue, "P", to_x)
        self.draw_seg(qp, self.q, 100, Qt.GlobalColor.darkGreen, "Q", to_x)
        self.draw_seg(qp, self.a, 150, Qt.GlobalColor.red, "A", to_x)

    def draw_seg(self, qp, coords, y, color, label, map_f):
        if not coords:
            return
        qp.setPen(QPen(color, 6))
        x1 = map_f(coords[0])
        x2 = map_f(coords[1])
        qp.drawLine(x1, y, x2, y)

        qp.setPen(QPen(Qt.GlobalColor.black, 1))
        qp.setFont(QFont("Arial", 10))
        qp.drawText(x1, y - 10, str(coords[0]))
        qp.drawText(x2, y - 10, str(coords[1]))
        qp.drawText(10, y + 5, label)


def сonvert(expr):

    depth = 0
    i = len(expr) - 1

    while i >= 1:
        if expr[i] == ')':
            depth += 1
        elif expr[i] == '(':
            depth -= 1
        elif depth == 0 and expr[i - 1:i + 1] == '->':
            left = expr[:i - 1].strip()
            right = expr[i + 1:].strip()
            left = сonvert(left)
            right = сonvert(right)
            return f"(not ({left}) or ({right}))"
        i -= 1

    result = ""
    i = 0
    while i < len(expr):
        if expr[i] == '(':
            depth = 1
            j = i + 1
            while j < len(expr) and depth > 0:
                if expr[j] == '(':
                    depth += 1
                elif expr[j] == ')':
                    depth -= 1
                j += 1
            inner = expr[i + 1:j - 1]
            inner_converted = сonvert(inner)
            result += '(' + inner_converted + ')'
            i = j
        else:
            result += expr[i]
            i += 1

    return result


class SolverApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EGE 15 Solver")
        self.resize(600, 400)

        lay = QVBoxLayout()

        self.in_p = QLineEdit()
        self.in_p.setPlaceholderText("P (например: 25 64)")
        lay.addWidget(self.in_p)

        self.in_q = QLineEdit()
        self.in_q.setPlaceholderText("Q (например: 40 115)")
        lay.addWidget(self.in_q)

        self.in_ex = QLineEdit()
        self.in_ex.setPlaceholderText("Условие")
        self.in_ex.setText("(x ∈ P) → (((x ∈ Q) ∧ ¬(x ∈ A)) → ¬(x ∈ P))")
        lay.addWidget(self.in_ex)

        btn = QPushButton("Найти A")
        btn.clicked.connect(self.calc)
        lay.addWidget(btn)

        self.res_lbl = QLabel("Результат: ")
        lay.addWidget(self.res_lbl)

        self.debug_lbl = QLabel("Формула: ")
        self.debug_lbl.setWordWrap(True)
        lay.addWidget(self.debug_lbl)

        self.canv = Canvas()
        lay.addWidget(self.canv)

        self.setLayout(lay)

    def calc(self):
        try:
            p_raw = list(map(float, self.in_p.text().split()))
            q_raw = list(map(float, self.in_q.text().split()))
            p1, p2 = p_raw[0], p_raw[1]
            q1, q2 = q_raw[0], q_raw[1]

            ex = self.in_ex.text()
            ex = ex.replace("∈", " in ")
            ex = ex.replace("¬", " not ")
            ex = ex.replace("∧", " and ")
            ex = ex.replace("∨", " or ")
            ex = ex.replace("/\\", " and ")
            ex = ex.replace("\\/", " or ")

            ex = ex.replace("→", "->")
            while "  " in ex:
                ex = ex.replace("  ", " ")

            ex = ex.replace("x in P", "(p1<=x<=p2)")
            ex = ex.replace("x in Q", "(q1<=x<=q2)")
            ex = ex.replace("x in A", "in_a")

            ex = сonvert(ex)

            self.debug_lbl.setText(f"Формула: {ex}")

            best_a1, best_a2 = None, None
            best_len = float('inf')

            min_bound = min(p1, q1) - 50
            max_bound = max(p2, q2) + 50
            step = 0.5

            candidates = [x * step + min_bound for x in range(int((max_bound - min_bound) / step) + 1)]

            for a1 in candidates:
                for a2 in candidates:
                    if a2 < a1:
                        continue

                    valid = True
                    for x in candidates:
                        try:
                            result = eval(ex)
                            if not result:
                                valid = False
                                break
                        except:
                            valid = False
                            break

                    if valid:
                        length = a2 - a1
                        if length < best_len:
                            best_len = length
                            best_a1, best_a2 = a1, a2

            if best_a1 is not None:
                self.res_lbl.setText(f"A: [{best_a1:.1f}; {best_a2:.1f}]  Длина: {best_len:.1f}")
                self.canv.set_data([p1, p2], [q1, q2], [best_a1, best_a2])
            else:
                self.res_lbl.setText("A не найдено")
                self.canv.set_data([p1, p2], [q1, q2], [])

        except Exception as e:
            self.res_lbl.setText(f"Ошибка: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SolverApp()
    win.show()
    sys.exit(app.exec())