#! /usr/bin/python3

import sys

from PyQt5 import QtCore, QtGui, QtWidgets

import Glob
import Gui
import Game
import Slots


def main():
    Glob.app = QtWidgets.QApplication(sys.argv)
    Glob.MainWindow = QtWidgets.QMainWindow()
    Glob.ui = Gui.Ui_MainWindow()
    Glob.ui.setupUi(Glob.MainWindow)
    Glob.MainWindow.show()
    sys.exit(Glob.app.exec_())


if __name__ == "__main__":
    main()
