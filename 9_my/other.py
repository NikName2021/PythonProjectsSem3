from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, header):
        super().__init__()
        self._data = data
        self._headers = header

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._headers[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._headers[section])


class AnotherWindow(QtWidgets.QMainWindow):
    def __init__(self, data, header):
        super().__init__()
        # self.setStyleSheet("background-color: grey;")

        self.table = QtWidgets.QTableView()
        self.setGeometry(300, 300, 500, 500)

        self.model = TableModel(data, header)
        self.table.setModel(self.model)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # self.table.resizeColumnsToContents()
        self.setCentralWidget(self.table)
