import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QLineEdit, QTabWidget, QTabBar,
                             QStackedLayout, QToolBar, QAction)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from PyQt5.QtNetwork import QNetworkProxyFactory, QNetworkRequest
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Web Browser"
        self.CreateWindow()

        # Set some default properties for the window
        self.setWindowTitle(self.title)
        self.setBaseSize(1366, 768)
        self.setMinimumSize(800, 540)


    def CreateWindow(self):
        # Main window layout
        self.layout = QVBoxLayout()

        # No margins around our main content
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.tabCount = 0

        # Create TabBar, movable and closable
        self.tabbar = QTabBar(movable=True, tabsClosable=True)

        # Hook into essential events
        self.tabbar.tabBarClicked.connect(self.SwitchTabs)
        self.tabbar.tabCloseRequested.connect(self.CloseTab)

        # Create list to house each tabs widget in
        self.tabs = []

        # Create New Tab
        self.AddTabButton = QPushButton("+")
        self.AddTabButton.clicked.connect(self.AddTab)

        # Add Back Button
        self.BackButton = QPushButton()
        self.back = QIcon("back.png")
        self.BackButton.setIcon(self.back)

        # Add Forward Button
        self.ForwardButton = QPushButton()
        self.forward = QIcon("forward.png")
        self.ForwardButton.setIcon(self.forward)

        # Create address bar.  Rig it to BrowseTo so we can actually load the sites
        self.AddressBar = QLineEdit()
        self.AddressBar.returnPressed.connect(self.BrowseTo)

        # This is teh main control bar
        self.tabControlWidget = QWidget()
        self.tabControls = QHBoxLayout()

        # Fill the control bar
        self.tabControls.addWidget(self.BackButton)
        self.tabControls.addWidget(self.ForwardButton)
        self.tabControls.addWidget(self.AddressBar)
        self.tabControls.addWidget(self.AddTabButton)
        self.tabControlWidget.setLayout(self.tabControls)

        # Create container that will hold the webviews:
        self.container = QWidget()
        self.container.layout = QStackedLayout()
        self.container.setLayout(self.container.layout)

        # Set the main window structure
        self.layout.addWidget(self.tabbar)
        self.layout.addWidget(self.tabControlWidget)
        self.layout.addWidget(self.container)
        self.layout.addStretch(0)

        # Set main windows layout = our top level QVBOX
        self.setLayout(self.layout)

        # Open one tab by default
        self.AddTab()

        # Show the window
        self.show()


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
        self.tabs[i].layout.addStretch(1)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    sys.exit(app.exec())