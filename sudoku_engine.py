#!/usr/bin/env python3

from PySide6 import QtCore, QtWidgets, QtGui
from threading import Event
import numpy as np
import csv
import sys

from engine import resolve


class SudokuEngineGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.stoprequest = Event()

        self.text = QtWidgets.QLabel("Sudoku resolving engine")
        self.text.setAlignment(QtCore.Qt.AlignCenter)

        self.button = QtWidgets.QPushButton("Resolve")
        # self.button_stop = QtWidgets.QPushButton("Stop")
        self.button_open = QtWidgets.QPushButton('Open')
        self.button_save = QtWidgets.QPushButton('Save')
        self.button.clicked.connect(self.resolve)
        # self.button_stop.clicked.connect(lambda: self.stoprequest.set())
        self.button_open.clicked.connect(self.handle_open)
        self.button_save.clicked.connect(self.handle_save)

        self.data = np.full((9, 9), np.nan)
        self.table = QtWidgets.QTableWidget(9, 9)
        # self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.cellChanged.connect(self.cell_changed)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.table)
        # self.layout.addWidget(self.button_stop)
        self.layout.addWidget(self.button_open)
        self.layout.addWidget(self.button_save)
        self.layout.addWidget(self.button)

        self.resize(405, 540)

    @QtCore.Slot()
    def cell_changed(self):
        cell = self.table.currentItem()
        if cell is not None:
            data = cell.text()
            pos = cell.row(), cell.column()
            try:
                if data != '':
                    self.data[pos] = int(data)
                    # print(self.data)
            except ValueError:
                cell.setText('')
                self.data[pos] = np.nan
                print(f'bad value {data}')

    def _set_value(self, x, y, value):
        self.table.setItem(y, x, QtWidgets.QTableWidgetItem(str(int(value))))
        self.table.item(y, x).setBackground(QtGui.QColor(100, 100, 150))

    @QtCore.Slot()
    def resolve(self):
        self.stoprequest.clear()
        ret_status, ret_matrix = resolve(self.data)
        for x in range(9):
            for y in range(9):
                if np.isnan(self.data[y, x]) and not np.isnan(ret_matrix[y, x]):
                    self._set_value(x, y, ret_matrix[y, x])

    def handle_save(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save File', '', 'CSV(*.csv)')
        if path != '':
            with open(path, 'w') as stream:
                writer = csv.writer(stream)
                for row in range(self.table.rowCount()):
                    rowdata = []
                    for column in range(self.table.columnCount()):
                        item = self.table.item(row, column)
                        if item is not None:
                            rowdata.append(
                                item.text())
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)

    def handle_open(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Open File', '', 'CSV(*.csv)')
        if path != '':
            with open(path, 'r') as stream:
                self.table.setRowCount(0)
                self.table.setColumnCount(0)
                for rowdata in csv.reader(stream):
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    self.table.setColumnCount(len(rowdata))
                    for column, data in enumerate(rowdata):
                        item = QtWidgets.QTableWidgetItem(data)
                        self.table.setItem(row, column, item)
                        try:
                            if data != '':
                                self.data[row, column] = int(data)
                                # print(self.data)
                        except ValueError:
                            print(f'bad value {data}')


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = SudokuEngineGUI()
    widget.show()

    sys.exit(app.exec())
