from PyQt6 import QtCore, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 650)

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setContentsMargins(0, 0, 0, 0)

        # Layout principal horizontal
        self.contentLayout = QtWidgets.QHBoxLayout()
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(0)

        self.centralLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.centralLayout.setContentsMargins(0, 0, 0, 0)
        self.centralLayout.setSpacing(0)
        self.centralLayout.addLayout(self.contentLayout)

        # --- Sidebar frame ---
        self.sidebar_frame = QtWidgets.QFrame(parent=self.centralwidget)
        self.sidebar_frame.setObjectName("sidebar_frame")
        self.sidebar_frame.setMinimumWidth(55)
        self.sidebar_frame.setMaximumWidth(200)
        

        self.sidebarLayout = QtWidgets.QVBoxLayout(self.sidebar_frame)
        self.sidebarLayout.setContentsMargins(0, 0, 0, 0)
        self.sidebarLayout.setSpacing(0)

        # --- Title frame (inside sidebar) ---
        self.title_frame = QtWidgets.QFrame(parent=self.sidebar_frame)
        self.title_frame.setObjectName("title_frame")
        self.titleLayout = QtWidgets.QHBoxLayout(self.title_frame)
        self.titleLayout.setContentsMargins(6, 6, 6, 6)
        self.titleLayout.setSpacing(6)

        self.title_icon = QtWidgets.QLabel(parent=self.title_frame)
        self.title_icon.setObjectName("title_icon")
        self.titleLayout.addWidget(self.title_icon)

        self.titleLayout.addStretch()

        self.menu_btn = QtWidgets.QPushButton(parent=self.title_frame)
        self.menu_btn.setObjectName("menu_btn")
        self.titleLayout.addWidget(self.menu_btn)

        self.sidebarLayout.addWidget(self.title_frame)

        # --- Sidebar menu stack ---
        self.sidebarStack = QtWidgets.QStackedLayout()
        self.sidebarStack.setObjectName("sidebarStack")

        self.listWidget_icon_only = QtWidgets.QListWidget()
        self.listWidget_icon_only.setObjectName("listWidget_icon_only")
        self.sidebarStack.addWidget(self.listWidget_icon_only)

        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setObjectName("listWidget")
        self.sidebarStack.addWidget(self.listWidget)

        self.sidebar_stack_container = QtWidgets.QWidget()
        self.sidebar_stack_container.setObjectName("sidebar_stack_container")
        self.sidebar_stack_container.setLayout(self.sidebarStack)
        self.sidebarLayout.addWidget(self.sidebar_stack_container)

        self.contentLayout.addWidget(self.sidebar_frame)

        # --- Main content area ---
        self.stackedWidget = QtWidgets.QStackedWidget(parent=self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.contentLayout.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)

        # Menubar & statusbar
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "JoularJx"))
        self.title_icon.setText(_translate("MainWindow", "Icon"))
