#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QTabWidget
from PyQt5 import QtGui
from ui import Ui_MainWindow
from controllers import ConnectionController, ControlController, ImageController
from controllers.help_dialog import HelpDialog
import resources_rc  # Import compiled resources
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.connection_controller = ConnectionController(self.ui)
        self.control_controller = ControlController(self.ui)
        self.image_controller = ImageController(self.ui)
        
        # Connect Help button
        self.ui.actionHelp.triggered.connect(self.show_help)
        
        # Explicitly set window icon (fallback if setupUi didn't load it)
        icon = QtGui.QIcon(':/AppIcons/resources/icons/OSCOS_icon.png')
        if not icon.isNull():
            self.setWindowIcon(icon)
        else:
            print("Warning: Icon resource not loaded. Ensure resources_rc.py is up-to-date.")
        
        # Set window title
        self.setWindowTitle("OSCOS - Oscillation Control System")

    def show_help(self):
        """Show the help dialog"""
        help_dialog = HelpDialog(self)
        help_dialog.exec_()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

