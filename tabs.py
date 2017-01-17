import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QPushButton, QLabel, QLineEdit, QTabWidget, QTabBar,
                             QStackedLayout, QToolBar, QAction)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = "Web Browser"
        self.CreateWindow()
        self.setWindowTitle(self.title)
        self.setBaseSize(1366, 768)
        self.setMinimumSize(800, 540)


    def CreateWindow(self):
        # Main window layout
        self.layout = QVBoxLayout()
        self.layout.alignment()
        self.tabCount = 0

        # Create TabBar, movable and closable
        self.tabbar = QTabBar(movable=True, tabsClosable=True)

        # Create list to house each tabs widget in
        self.tabs = []

        # Create New Tab
        self.AddTabButton = QPushButton("+")
        self.AddTabButton.clicked.connect(self.AddTab)

        self.toolbar = QToolBar()
        self.toolbar.addWidget(QLineEdit())

        self.tabControlWidget = QWidget()
        self.tabControls = QHBoxLayout()
        self.tabControls.addStretch(0)
        self.tabControls.addWidget(self.AddTabButton)


        self.tabControlWidget.setLayout(self.tabControls)


        self.tabbar.tabBarClicked.connect(self.printTabs)
        self.tabbar.currentChanged.connect(self.printTabs)

        self.tabbar.tabCloseRequested.connect(self.CloseTab)
        self.layout.addWidget(self.tabControlWidget)
        self.layout.addWidget(self.tabbar)
        self.layout.addWidget(self.toolbar)

        self.container = QWidget()
        self.container.layout = QStackedLayout()
        self.container.setLayout(self.container.layout)

        self.layout.addWidget(self.container)
        self.layout.addStretch(0)


        self.setLayout(self.layout)

        self.AddTab()

        self.show()

    def printTabs(self, i):
        self.container.layout.setCurrentWidget(self.tabs[i])

    def CloseTab(self, i):

        self.tabbar.removeTab(i)



    def AddTab(self):
        if len(self.tabs):
            self.tabCount += 1

        i = self.tabCount
        print("i is", i)
        self.tabs.append(QWidget())
        self.tabs[i].count = 1
        self.tabs[i].layout = QVBoxLayout()
        self.tabs[i].layout.addStretch(1)
        self.tabs[i].content = QPushButton("New Tab" + str(i))
        self.tabs[i].layout.addWidget(self.tabs[i].content)
        self.tabs[i].setLayout(self.tabs[i].layout)
        self.container.layout.addWidget(self.tabs[i])

        self.tabbar.addTab("New Tab")

        self.tabbar.setCurrentIndex(i)
        self.container.layout.setCurrentWidget(self.tabs[i])

    def changeTabText(self):
        TabIndex = self.tabs.currentIndex()
        self.tabs.setTabText(TabIndex, "Change this label")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    sys.exit(app.exec())