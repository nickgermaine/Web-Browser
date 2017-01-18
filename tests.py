import sys
import simplejson as json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QLineEdit, QTabWidget, QTabBar,
                             QStackedLayout, QToolBar, QAction, QMainWindow, QDesktopWidget, QFrame, QGraphicsDropShadowEffect, QShortcut,
                             QKeySequenceEdit)
from PyQt5.QtGui import QIcon, QColor, QKeySequence, QWindow
from PyQt5.QtCore import *
from PyQt5.QtNetwork import QNetworkProxyFactory, QNetworkRequest
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from PyQt5.QtWinExtras import QWinTaskbarButton
import ctypes
myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Web Browser"
        self.CreateWindow()


    def CreateWindow(self):
        self.frame = QFrame()

        self.top = QWidget()

        # Main window layout
        self.layout = QVBoxLayout()
        self.setObjectName("BrowserWindow")

        self.layout.addWidget(QPushButton("test"))
        self.top.setLayout(self.layout)

        self.setCentralWidget(self.top)
        self.show()

        self.setWindowIcon(QIcon('resources/icons/icon.png'))






if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    sys.exit(app.exec())