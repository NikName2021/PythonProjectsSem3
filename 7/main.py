import sys

from PyQt6 import QtWidgets
from PyQt6 import uic
from PyQt6.QtWidgets import QButtonGroup


def get_text_19(answer):
    return f"""============================================================
ЗАДАЧА 19
============================================================
Найти минимальное S, при котором первый игрок может
выиграть первым ходом (за 2 хода от начала игры).
------------------------------------------------------------
Ответ 19: {answer}"""


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("main_window.ui", self)

        self.pushButton.clicked.connect(self.authenticate)
        self.group = QButtonGroup(self)
        self.group.addButton(self.radioButton)
        self.group.addButton(self.radioButton_2)

        self.show()

    def parse_move(self, move_str: str):
        move_str = move_str.strip()
        if not move_str:
            return None

        if move_str[0] == '+':
            value = int(move_str[1:])
            return lambda s: s + value
        elif move_str[0] == '*':
            value = int(move_str[1:])
            return lambda s: s * value
        elif move_str[0] == '-':
            value = int(move_str[1:])
            return lambda s: s - value
        elif move_str[0] == '/':
            value = int(move_str[1:])
            return lambda s: s // value
        return None

    def main_game(self, s, m, target, moves, use_any):
        if s >= target: return m % 2 == 0
        if m == 0: return False
        h = []
        for move in moves:
            h.append(self.main_game(move(s), m - 1, target, moves, use_any))
        if not use_any:
            return any(h) if m % 2 else all(h)
        return all(h) if m % 2 else any(h)

    def get_functions(self):
        functions = []
        for i, text in enumerate([self.lineEdit.text(), self.lineEdit_1.text(), self.lineEdit_2.text()]):
            func = self.parse_move(text)
            if func:
                functions.append(func)
        return functions

    def authenticate(self):
        target_val = self.spinBox.value()
        start = self.spinBox_1.value()
        end = self.spinBox_2.value()
        try:
            functions = self.get_functions()
        except Exception as e:
            self.text_edit.setPlainText("ERROR IN INPUT FUNCTIONS")
            return

        if not functions:
            self.text_edit.setPlainText("No functions found")
            return
        use_any = 0

        for j, button in enumerate(self.group.buttons()):
            if button.isChecked():
                use_any = j

        answer_19 = None
        for s in range(start, end + 1):
            if self.main_game(s, 2, target_val, functions, use_any):
                answer_19 = s
                break
        self.text_edit.setPlainText(get_text_19(answer_19))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
