import sys
import os
import json
from io import BytesIO
from PIL import Image
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QLineEdit, QTabWidget, QTabBar,
                             QStackedLayout, QToolBar, QAction, QMainWindow, QDesktopWidget, QFrame, QGraphicsDropShadowEffect, QShortcut,
                             QKeySequenceEdit, QSplitter, QSplitterHandle)
from PyQt5.QtGui import QIcon, QColor, QKeySequence, QWindow, QPainter, QPixmap, QImage, QImageReader
from PyQt5.QtCore import *
from PyQt5.QtNetwork import QNetworkProxyFactory, QNetworkRequest
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWinExtras import QWinTaskbarButton


# So Windows can set taskbar icon correctly...
import ctypes
myappid = 'rapidware.eden.browser.1' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class AddressBar(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, e):
        # Select all on focusIn
        self.selectAll()


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

        # AddressBar searches go through:
        self.SearchProvider = "https://www.google.ca/?gfe_rd=cr&ei=rnd_WPvfEqnM8AeSk4Ng#q="

        self.center()
        QWebEngineSettings.LocalContentCanAccessFileUrls = True

    def CreateWindow(self):
        # Load javascripts:
        file = QFile()
        file.setFileName("resources/scripts/jquery.min.js")
        file.open(QIODevice.ReadOnly)
        self.jquery = file.readAll()
        self.jquery.append("\nvar qt = { 'jQuery': jQuery.noConflict(true) };")
        file.close()

        file = QFile()
        file.setFileName("resources/scripts/inspector.js")
        file.open(QIODevice.ReadOnly)
        self.inspector = file.readAll()
        file.close()

        # Main window layout
        self.layout = QVBoxLayout()
        self.setObjectName("BrowserWindow")

        # No margins around our main content
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        # Shortcuts
        # NEw tab
        self.shortcutNewTab = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcutNewTab.activated.connect(self.AddTab)

        # Refresh
        self.shortcutRefresh = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcutRefresh.activated.connect(self.refresh)
        self.shortcutRefresh2 = QShortcut(QKeySequence("F5"), self)
        self.shortcutRefresh2.activated.connect(self.refresh)
        self.shortcutRefresh3 = QShortcut(QKeySequence("Ctrl+F5"), self)
        self.shortcutRefresh3.activated.connect(self.refreshNoCache)

        # Open Devtools
        self.shortcutDevTools = QShortcut(QKeySequence("Ctrl+Shift+I"), self)
        self.shortcutDevTools.activated.connect(self.openDevTools)

        # Tabcount
        self.tabCount = 0

        # Create New Tab
        self.AddTabButton = QPushButton()
        self.AddTabButton.setIcon(QIcon("resources/icons/ic_add_black_24px.svg"))
        self.AddTabButton.clicked.connect(self.AddTab)

        # Create TabBar, movable and closable
        self.tabbar = QTabBar(movable=True, tabsClosable=True)
        self.tabbar.setObjectName("TabBar")
        self.tabbar.setExpanding(False)
        self.tabbar.setDrawBase(False)
        self.tabbar.setElideMode(Qt.ElideLeft)

        # Create custom WindowBorder
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

        # WindowControl buttons signal->slot()
        self.MinimizeBrowserButton.clicked.connect(self.min)
        self.MaximizeBrowserButton.clicked.connect(self.maximize)
        self.CloseBrowserButton.clicked.connect(self.quit)

        # Add TabBar to top of Window
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



        # Add Back Button
        self.BackButton = QPushButton()
        self.back = QIcon("resources/icons/ic_keyboard_arrow_left_black_24px.svg")
        self.BackButton.setIcon(self.back)
        self.BackButton.setEnabled(False)
        self.BackButton.clicked.connect(self.goBack)

        # Add Forward Button
        self.ForwardButton = QPushButton()
        self.forward = QIcon("resources/icons/ic_keyboard_arrow_right_black_24px.svg")
        self.ForwardButton.setIcon(self.forward)
        self.ForwardButton.setEnabled(False)
        self.ForwardButton.clicked.connect(self.goForward)

        # Add Refresh Button
        self.RefreshButton = QPushButton()
        self.refreshIcon = QIcon("resources/icons/ic_refresh_black_24px.svg")
        self.RefreshButton.setIcon(self.refreshIcon)
        self.RefreshButton.clicked.connect(self.refresh)

        # Add Menu Button
        self.MenuButton = QPushButton()
        self.MenuButton.setIcon(QIcon("resources/icons/ic_more_vert_black_24px.svg"))

        # Create address bar.  Rig it to BrowseTo so we can actually load the sites
        self.AddressBar = AddressBar()
        self.AddressBar.returnPressed.connect(self.BrowseTo)

        # This is teh main control bar
        self.tabControlWidget = QWidget()
        self.tabControls = QHBoxLayout()
        self.tabControlWidget.setObjectName("toolbar")

        # Fill the control bar
        self.tabControls.addWidget(self.BackButton)
        self.tabControls.addWidget(self.ForwardButton)
        self.tabControls.addWidget(self.RefreshButton)
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

    def CloseTab(self, i):
        # Remove tab from tab bar, also delete [tab<i>]
        self.tabbar.removeTab(i)
        del self.tabs[i]
        if len(self.tabs) == 0:
            self.AddTab()


    def AddTab(self):
        # If there aren't tabs, keep at 0, otherwise increase by 1
        if len(self.tabs):
            self.tabCount += 1
        i = self.tabCount

        # Add our tab object to self.tabs which is []
        self.tabs.append(QWidget())
        self.tabs[i].count = self.tabCount

        # Set the tabs VBOx layout
        self.tabs[i].layout = QVBoxLayout()
        self.tabs[i].layout.setObjectName("TabView")

        # Create webview of our tab
        self.tabs[i].content = QWebEngineView()
        self.tabs[i].page = self.tabs[i].content.page()
        self.tabs[i].content.setAccessibleName("tab")
        self.tabs[i].content.setObjectName("tab1")

        # On tab creation load google
        #url = QUrl("eden://")
        url = os.getcwd() + r'\resources\pages' + '\\new-tab.html'
        self.tabs[i].content.load(QUrl.fromUserInput(url))


        self.tabs[i].splitView = QSplitter()
        self.tabs[i].splitView.setOrientation(Qt.Vertical)
        self.tabs[i].splitView.addWidget(self.tabs[i].content)


        # Add VBox layout to our tab object, and add content into the tabs layout (VBOX)
        self.tabs[i].layout.addWidget(self.tabs[i].splitView)
        self.tabs[i].setLayout(self.tabs[i].layout)
        self.container.layout.addWidget(self.tabs[i])

        # When the URL changes, set the address bar accordingly
        self.tabs[i].content.urlChanged.connect(lambda: self.SetAddressBar(i))
        self.tabs[i].content.titleChanged.connect(lambda: self.setTabTitle(i))
        self.tabs[i].content.iconChanged.connect(lambda: self.setTabIcon(i))

        self.tabs[i].connected = True
        self.tabs[i].history = []

        # Remove outer margins
        self.tabs[i].layout.setContentsMargins(0,0,0,0)

        # Add the tab to the top tab bar
        self.tabbar.addTab(self.tabs[i].content.title())
        self.tabbar.setTabData(i, "tab"+str(i))
        self.tabs[i].setObjectName("tab"+str(i))

        # On load finished, set the tabs title
        self.tabs[i].content.loadFinished.connect(lambda: self.setTabTitle(i))
        self.tabs[i].content.loadFinished.connect(lambda: self.RunScripts(i))

        # Make this new tab the current (active) one
        self.tabbar.setCurrentIndex(i)
        self.container.layout.setCurrentWidget(self.tabs[i])
        #print("back?", self.tabs[i].content.canGoBack)

        self.AddressBar.selectAll()

    def SwitchTabs(self, i):
        # Set the current tab to the container stacked widget.
        # container = current tab (from our tab list) []
        tab = self.tabbar.tabData(i)
        self.container.layout.setCurrentWidget(self.findChild(QWidget, tab))
        self.SetAddressBar(i)
        print(self.tabs[i].content.nativeParentWidget())

    def goBack(self):
        # Go back in history
        i = self.tabbar.currentIndex()
        self.tabs[i].content.back()
        self.ForwardButton.setEnabled(True)

    def goForward(self):
        # Go forward in history if possible
        i = self.tabbar.currentIndex()
        self.tabs[i].content.forward()

    def refresh(self):
        # Reload current webview
        i = self.tabbar.currentIndex()
        self.tabs[i].content.reload()

    def refreshNoCache(self):
        i = self.tabbar.currentIndex()
        self.tabs[i].content.reloadAndBypassCache()

    def getDevToolsList(self, data):
        dev = data
        dev_list = json.loads(dev)


        count = 0
        name = self.tabbar.tabData(self.tabbar.currentIndex())

        for item in reversed(dev_list):
            print(self.findChild(QWidget, name).page.url().toString())
            if item["url"] == self.findChild(QWidget, name).page.url().toString():
                print("yes")
                devUrl = item["devtoolsFrontendUrl"]
                self.findChild(QWidget, name).devtools.load(QUrl.fromUserInput("http://localhost:667" + devUrl))



    def printHtml(self, result):
        result.toPlainText(self.getDevToolsList)

    def openDevTools(self):
        i = self.tabbar.currentIndex()
        name = self.tabbar.tabData(self.tabbar.currentIndex())
        self.findChild(QWidget, name).devtoolsContainer = QWidget()
        self.findChild(QWidget, name).devtoolsLayout = QVBoxLayout()
        self.findChild(QWidget, name).devtools = QWebEngineView()
        self.findChild(QWidget, name).devtools.load(QUrl.fromUserInput("http://localhost:667"))
        self.findChild(QWidget, name).devtoolsQuit = QPushButton()
        self.findChild(QWidget, name).devtoolsQuit.setIcon(QIcon('resources/icons/ic_clear_black_24px.svg'))
        self.findChild(QWidget, name).devtoolsQuit.setFixedWidth(24)
        self.findChild(QWidget, name).devtoolsQuit.setFixedHeight(24)


        current_page = QWebEngineView()
        current_page.load(QUrl.fromUserInput("http://localhost:667/json/list"))
        current_page.loadFinished.connect(lambda: self.printHtml(current_page.page()))


        self.findChild(QWidget, name).devtoolsLayout.setContentsMargins(0,0,0,0)
        self.findChild(QWidget, name).content.page().runJavaScript(str(self.jquery))
        title = self.findChild(QWidget, name).content.page().title()
        durl = self.findChild(QWidget, name).content.page().url().toString()


        self.findChild(QWidget, name).devtoolsQuit.clicked.connect(self.quitDevtools)

        self.findChild(QWidget, name).devtoolsContainer.setLayout(self.findChild(QWidget, name).devtoolsLayout)
        self.findChild(QWidget, name).devtoolsLayout.addWidget(self.findChild(QWidget, name).devtoolsQuit)
        self.findChild(QWidget, name).devtoolsLayout.addWidget(self.findChild(QWidget, name).devtools)
        self.findChild(QWidget, name).splitView.addWidget(self.findChild(QWidget, name).devtoolsContainer)

    def quitDevtools(self):
        i = self.tabbar.currentIndex()
        activeTab = self.findChild(QWidget, self.tabbar.tabData(i))
        activeTab.devtoolsContainer.setParent(None)
        activeTab.devtoolsContainer.destroy()


    def SetAddressBar(self, i):
        # Get the current tabs index, and set the address bar to its title.toString()
        tab = self.tabbar.tabData(i)
        if self.findChild(QWidget, tab).connected == True:
            url = QUrl(self.findChild(QWidget, tab).content.url()).toString()
            self.AddressBar.setText(url)


        if len(self.tabs[i].history):
            self.BackButton.setEnabled(True)
        self.tabs[i].history.append(url)

    def setTabIcon(self, i):
        tab = self.tabbar.tabData(i)
        icon = self.findChild(QWidget, tab).content.page().icon()
        self.tabbar.setTabIcon(i, icon)

    def BrowseTo(self):
        # Get url from address bar
        url = self.AddressBar.text()
        name = self.tabbar.tabData(self.tabbar.currentIndex())
        activeTab = self.findChild(QWidget, name)
        currentTab = self.tabbar.currentIndex()

        if "eden://" in url:
            pages = "pages"
            page = url.split("://")[1]

            url = os.getcwd() + r'\resources\pages' + '\\' + page + ".html"

            file = QFile(url)
            local_page = file.open(QIODevice.ReadOnly)
            page_content = QTextStream(file)
            activeTab.connected = False

            activeTab.content.urlChanged.disconnect()
            activeTab.content.load(QUrl.fromUserInput(url))

        elif " " in url:
            url = QUrl.fromUserInput(self.SearchProvider + url)

            # Format correctly because were all lazy
            if activeTab.connected == False:
                activeTab.content.urlChanged.connect(lambda: self.SetAddressBar(currentTab))
        elif "http" not in url or "file://" not in url:
            FormattedUrl = "http://"
            OldUrl = url
            url = QUrl.fromUserInput(FormattedUrl + OldUrl)
            if activeTab.connected == False:
                activeTab.content.urlChanged.connect(lambda: self.SetAddressBar(currentTab))
            try:
                activeTab.content.load(url)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise

    def RunScripts(self, i):
        addFB = "$('head').prepend('<script type=\"text/javascript\" \
            src=\"https://getfirebug.com/firebug-lite.js\"> \
            {overrideConsole: false,\
            startInNewWindow: true,\
            startOpened: true}\
            </script>');"
        self.tabs[i].content.page().runJavaScript(str(self.jquery))
        self.tabs[i].content.page().runJavaScript(addFB)


    def setTabTitle(self, i):
        # Get current tabs webviews title, and set the actual tab item
        # on the tabbar to the correct title


        tab = self.tabbar.tabData(i)
        icon = self.findChild(QWidget, tab).content.page().title()
        self.tabbar.setTabText(i, icon)

    def getFavicon(self, i):
        url = self.tabs[i].content.url().toString()
        faviconUrl = "http://www.google.com/s2/favicons?domain=" + url
        return faviconUrl

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

    with open("resources/stylesheets/material.css", "r") as style:
        app.setStyleSheet(style.read())

    os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = "667"

    window = App()
    window.show()

    sys.exit(app.exec())