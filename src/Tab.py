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

class Tab(QWidget):
    def __init__(self, id):
        super().__init__()
        self.id = id

        # Set the tabs VBOx layout
        self.layout = QVBoxLayout()
        self.layout.setObjectName("TabView")

        # Create webview of our tab
        self.content = QWebEngineView()


        # Add VBox layout to our tab object, and add content into the tabs layout (VBOX)
        self.layout.addWidget(self.content)
        self.setLayout(self.layout)

        # Remove outer margins
        self.layout.setContentsMargins(0, 0, 0, 0)

        