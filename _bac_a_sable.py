from PyQt5.QtWidgets import (
    QApplication, QMainWindow
)
from PyQt5.QtCore import Qt

import sys


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # SIGNAL: The connected function will be called whenever the window
        # title is changed. The new title will be passed to the function.
        self.windowTitleChanged.connect(self.on_window_title_changed)

        # SIGNAL: The connected function will be called whenever the window
        # title is changed. The new title is discarded and the
        # function is called without parameters.
        self.windowTitleChanged.connect(lambda x: self.on_window_title_changed_no_params())

        # SIGNAL: The connected function will be called whenever the window
        # title is changed. The new title is discarded and the
        # function is called without parameters.
        # The function has default params.
        self.windowTitleChanged.connect(lambda x: self.my_custom_fn())

        # SIGNAL: The connected function will be called whenever the window
        # title is changed. The new title is passed to the function
        # and replaces the default parameter. Extra data is passed from
        # within the lambda.
        self.windowTitleChanged.connect(lambda x: self.my_custom_fn(x, 25))

        # This sets the window title which will trigger all the above signals
        # sending the new title to the attached functions or lambdas as the
        # first parameter.
        self.setWindowTitle("My Signals App")

    # SLOT: This accepts a string, e.g. the window title, and prints it
    def on_window_title_changed(self, s):
        print(s)

    # SLOT: This is called when the window title changes.
    def on_window_title_changed_no_params(self):
        print("Window title changed.")

    # SLOT: This has default parameters and can be called without a value
    def my_custom_fn(self, a="HELLLO!", b=5):
        print(a, b)


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()
