#!/usr/bin/env python3

from PySide6 import QtCore, QtWidgets, QtGui
from math import floor
from threading import Event
import numpy as np
import csv
import sys


class SudokuEngineGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.stoprequest = Event()

        self.text = QtWidgets.QLabel("Sudoku resolving engine")
        self.text.setAlignment(QtCore.Qt.AlignCenter)

        self.button = QtWidgets.QPushButton("Resolve")
        self.button_stop = QtWidgets.QPushButton("Stop")
        self.button_open = QtWidgets.QPushButton('Open')
        self.button_save = QtWidgets.QPushButton('Save')
        self.button.clicked.connect(self.magic)
        self.button_stop.clicked.connect(lambda: self.stoprequest.set())
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
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.button_stop)
        self.layout.addWidget(self.button_open)
        self.layout.addWidget(self.button_save)

        self.resize(580, 645)

    @QtCore.Slot()
    def cell_changed(self):
        cell = self.table.currentItem()
        if cell is not None:
            data = cell.text()
            pos = cell.row(), cell.column()
            try:
                if data != '':
                    self.data[pos] = int(data)
                    print(self.data)
            except ValueError:
                cell.setText('')
                self.data[pos] = np.nan
                print(f'bad value {data}')

    def _set_value(self, x, y, value):
        self.table.setItem(y, x, QtWidgets.QTableWidgetItem(str(int(value))))
        self.table.item(y, x).setBackground(QtGui.QColor(100, 100, 150))

    @QtCore.Slot()
    def magic(self):
        self.stoprequest.clear()
        # self.text.setText(random.choice(self.hello))
        found_matrix = self.data.copy()
        possibility_matrix = np.full((9, 9, 9), np.nan)
        for i in range(9):
            possibility_matrix[i, :, :][np.isnan(self.data)] = i+1

        while not self.stoprequest.is_set() and np.isnan(found_matrix).any():
            for y in range(9):
                square_y0 = floor(y / 3) * 3
                for x in range(9):
                    square_x0 = floor(x / 3) * 3
                    if not np.isnan(found_matrix[y, x]):
                        continue
                    square_known_values = found_matrix[square_y0:square_y0+3, square_x0:square_x0+3]
                    column_known_values = found_matrix[:, x]
                    row_known_values = found_matrix[y, :]
                    cell_possibilities = possibility_matrix[:, y, x]
                    # by known values
                    cell_possibilities[np.in1d(cell_possibilities, square_known_values)] = np.nan
                    cell_possibilities[np.in1d(cell_possibilities, column_known_values)] = np.nan
                    cell_possibilities[np.in1d(cell_possibilities, row_known_values)] = np.nan
                    cell_possibilities = cell_possibilities[~np.isnan(cell_possibilities)]

                    # by possibilities in dependencies
                    column_dependency_possibilities = possibility_matrix[:, :, x].ravel()
                    row_dependency_possibilities = possibility_matrix[:, y, :].ravel()
                    square_dependency_possibilities = possibility_matrix[:, square_x0:square_x0+3, square_y0:square_y0+3].ravel()
                    possibilities_in_dependencies = np.concatenate((column_dependency_possibilities,
                                                                   row_dependency_possibilities,
                                                                   square_dependency_possibilities))
                    possibilities_not_in_dependencies = cell_possibilities[~np.in1d(cell_possibilities, possibilities_in_dependencies)]
                    possibilities_not_in_dependencies = possibilities_not_in_dependencies[~np.isnan(possibilities_not_in_dependencies)]

                    # check if cell solution is found
                    print(x, y, cell_possibilities)

                    if len(cell_possibilities) == 1:
                        found_matrix[y, x] = cell_possibilities[0]
                        self._set_value(x, y, found_matrix[y, x])
                        continue

                    if len(possibilities_not_in_dependencies) == 1:
                        if possibilities_not_in_dependencies[0] not in cell_possibilities:
                            raise Exception(f'Oops, cell {x, y}: the only possible value based on'
                                            f' possibilities in dependencies does not belong to cell possibilities')
                        found_matrix[y, x] = cell_possibilities[0]
                        self._set_value(x, y, found_matrix[y, x])

                    if len(cell_possibilities) == 0:
                        raise Exception(f'Oops, cell {x, y} has no possible values')
                    # time.sleep(0.01)

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
                                print(self.data)
                        except ValueError:
                            print(f'bad value {data}')


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = SudokuEngineGUI()
    widget.show()

    sys.exit(app.exec())
