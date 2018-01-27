#! /usr/bin/python3

import sys

from PyQt5 import QtCore, QtGui, QtWidgets

import Gui
import Game
import Slots


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Slots.UiAndSlots()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
