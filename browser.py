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
myappid = 'rapidware.eden.browser.1' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class App(QFrame):
    def __init__(self):
        super().__init__()
        self.title = "Eden Browser"
        self.CreateWindow()

        # Set some default properties for the window
        self.setWindowTitle(self.title)
        self.setBaseSize(1366, 768)
        self.setMinimumSize(1366, 768)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon('resources/icons/icon.png'))

    def CreateWindow(self):

        # Main window layout
        self.layout = QVBoxLayout()
        self.setObjectName("BrowserWindow")



        # No margins around our main content
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        # Shortcuts
        self.shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcut.activated.connect(self.AddTab)

        self.tabCount = 0

        # Create TabBar, movable and closable
        self.tabbar = QTabBar(movable=True, tabsClosable=True)
        self.tabbar.setObjectName("TabBar")
        self.tabbar.setExpanding(False)
        self.tabbar.setDrawBase(False)

        self.windowBorder = QWidget()
        self.windowBorderLayout = QHBoxLayout()
        self.windowBorder.setLayout(self.windowBorderLayout)

        # Close button
        self.CloseBrowserButton = QPushButton()
        self.CloseBrowserButton.setIcon(QIcon('resources/icons/ic_clear_black_24px.svg'))
        self.CloseBrowserButton.setFixedWidth(48)

        # Maximize Button
        self.MaximizeBrowserButton = QPushButton()
        self.MaximizeBrowserButton.setIcon(QIcon('resources/icons/ic_aspect_ratio_black_24px.svg'))
        self.MaximizeBrowserButton.setFixedWidth(48)

        # Minimize button
        self.MinimizeBrowserButton = QPushButton()
        self.MinimizeBrowserButton.setIcon(QIcon('resources/icons/ic_remove_black_24px.svg'))
        self.MinimizeBrowserButton.setFixedWidth(48)

        self.MinimizeBrowserButton.clicked.connect(self.min)
        self.MaximizeBrowserButton.clicked.connect(self.maximize)
        self.CloseBrowserButton.clicked.connect(self.quit)

        self.windowBorderLayout.addWidget(self.tabbar)

        # So that we can drag the window on non-tab areas
        self.windowBorderLayout.addStretch()

        # Add Window controls
        self.windowBorderLayout.addWidget(self.MinimizeBrowserButton)
        self.windowBorderLayout.addWidget(self.MaximizeBrowserButton)
        self.windowBorderLayout.addWidget(self.CloseBrowserButton)
        self.windowBorderLayout.setSpacing(0)
        self.windowBorderLayout.setContentsMargins(0, 0, 0, 0)

        # Hook into essential events
        self.tabbar.tabBarClicked.connect(self.SwitchTabs)
        self.tabbar.tabCloseRequested.connect(self.CloseTab)


        # Create list to house each tabs widget in
        self.tabs = []

        # Create New Tab
        self.AddTabButton = QPushButton()
        self.AddTabButton.setIcon(QIcon("resources/icons/ic_add_black_24px.svg"))
        self.AddTabButton.clicked.connect(self.AddTab)

        # Add Back Button
        self.BackButton = QPushButton()
        self.back = QIcon("resources/icons/ic_keyboard_arrow_left_black_24px.svg")
        self.BackButton.setIcon(self.back)

        # Add Forward Button
        self.ForwardButton = QPushButton()
        self.forward = QIcon("resources/icons/ic_keyboard_arrow_right_black_24px.svg")
        self.ForwardButton.setIcon(self.forward)

        # Add Menu Button
        self.MenuButton = QPushButton()
        self.MenuButton.setIcon(QIcon("resources/icons/ic_more_vert_black_24px.svg"))

        # Create address bar.  Rig it to BrowseTo so we can actually load the sites
        self.AddressBar = QLineEdit()
        self.AddressBar.returnPressed.connect(self.BrowseTo)

        # This is teh main control bar
        self.tabControlWidget = QWidget()
        self.tabControls = QHBoxLayout()
        self.tabControlWidget.setObjectName("toolbar")

        # Fill the control bar
        self.tabControls.addWidget(self.BackButton)
        self.tabControls.addWidget(self.ForwardButton)
        self.tabControls.addWidget(self.AddressBar)
        self.tabControls.addWidget(self.AddTabButton)
        self.tabControls.addWidget(self.MenuButton)
        self.tabControlWidget.setLayout(self.tabControls)
        self.tabControlWidget.setObjectName("TabControls")

        # Create container that will hold the webviews:
        self.container = QWidget()
        self.container.layout = QStackedLayout()
        self.container.setLayout(self.container.layout)

        # Set the main window structure
        self.layout.addWidget(self.windowBorder)
        self.layout.addWidget(self.tabControlWidget)
        self.layout.addWidget(self.container)

        # Set main windows layout = our top level QVBOX
        self.setLayout(self.layout)

        # Open one tab by default
        self.AddTab()

        # Show the window
        # self.showMaximized()

        # Show in windowed mode:
        # self.show()


    def CloseTab(self, i):
        # Remove tab from tab bar, also delete [tab<i>]
        self.tabbar.removeTab(i)
        del self.tabs[i]


    def AddTab(self):
        # If there aren't tabs, keep at 0, otherwise increase by 1
        if len(self.tabs):
            self.tabCount += 1
        i = self.tabCount

        # Add our tab object to self.tabs which is []
        self.tabs.append(QWidget())
        self.tabs[i].count = 1

        # Set the tabs VBOx layout
        self.tabs[i].layout = QVBoxLayout()
        self.tabs[i].layout.setObjectName("TabView")

        # Create webview of our tab
        self.tabs[i].content = QWebEngineView()

        # On tab creation load google
        url = QUrl("http://google.com")
        self.tabs[i].content.load(url)

        # Add VBox layout to our tab object, and add content into the tabs layout (VBOX)
        self.tabs[i].layout.addWidget(self.tabs[i].content)
        self.tabs[i].setLayout(self.tabs[i].layout)
        self.container.layout.addWidget(self.tabs[i])

        # When the URL changes, set the address bar accordingly
        self.tabs[i].content.urlChanged.connect(self.SetAddressBar)
        self.tabs[i].content.titleChanged.connect(lambda: self.setTabTitle(i))

        # Remove outer margins
        self.tabs[i].layout.setContentsMargins(0,0,0,0)

        # Add the tab to the top tab bar
        self.tabbar.addTab(self.tabs[i].content.title())

        # On load finished, set the tabs title
        self.tabs[i].content.loadFinished.connect(lambda: self.setTabTitle(i))

        # Make this new tab the current (active) one
        self.tabbar.setCurrentIndex(i)
        self.container.layout.setCurrentWidget(self.tabs[i])

    def SwitchTabs(self, i):
        # Set the current tab to the container stacked widget.
        # container = current tab (from our tab list) []
        self.container.layout.setCurrentWidget(self.tabs[i])

    def SetAddressBar(self):
        # Get the current tabs index, and set the address bar to its title.toString()
        i = self.tabbar.currentIndex()
        url = QUrl(self.tabs[i].content.url()).toString()
        self.AddressBar.setText(url)

    def BrowseTo(self):
        # Get url from address bar
        url = self.AddressBar.text()

        # Format correctly because were all lazy
        if "http" not in url:
            FormattedUrl = "http://"
            OldUrl = url
            url = FormattedUrl + OldUrl

        # Get current tab and load the webpage from the url
        currentTab = self.tabbar.currentIndex()
        self.tabs[currentTab].content.load(QUrl.fromUserInput(url))

    def setTabTitle(self, i):
        # Get current tabs webviews title, and set the actual tab item
        # on the tabbar to the correct title
        title = self.tabs[i].content.title()
        self.tabbar.setTabText(i, title)

        # center

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        # print(delta)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def quit(self):
        self.destroy()

    def maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def min(self):
        self.showMinimized()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open("material.css", "r") as style:
        app.setStyleSheet(style.read())

    window = App()
    window.show()

    sys.exit(app.exec())