# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets, QtCore, QtGui


if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

here = sys.path[0]


class WidgetMenuBar(object):
    def __init__(self, mainWindowHandle):
        self.handle = mainWindowHandle
        # initial menu bar
        self.menuBar = QtWidgets.QMenuBar(self.handle.mainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 600, 25))

        self.handle.mainWindow.setMenuBar(self.menuBar)
        self.menu_1 = QtWidgets.QMenu("文件", self.menuBar)
        self.menu_2 = QtWidgets.QMenu("编辑", self.menuBar)
        self.menu_3 = QtWidgets.QMenu("设置", self.menuBar)
        self.menu_4 = QtWidgets.QMenu("运行", self.menuBar)
        self.menu_5 = QtWidgets.QMenu("工具", self.menuBar)
        self.menu_6 = QtWidgets.QMenu("帮助", self.menuBar)

        self.action_1_1 = QtWidgets.QAction("新建", self.handle.mainWindow)
        self.action_1_2 = QtWidgets.QAction("打开", self.handle.mainWindow)
        self.action_1_2.triggered.connect(self.openfile)
        self.action_1_3 = QtWidgets.QAction("打开最近", self.handle.mainWindow)
        self.action_1_4 = QtWidgets.QAction("保存", self.handle.mainWindow)
        self.action_1_5 = QtWidgets.QAction("另存为", self.handle.mainWindow)
        self.action_1_6 = QtWidgets.QAction("退出", self.handle.mainWindow)
        self.menu_1.addAction(self.action_1_1)
        self.menu_1.addAction(self.action_1_2)
        self.menu_1.addAction(self.action_1_3)
        self.menu_1.addSeparator()
        self.menu_1.addAction(self.action_1_4)
        self.menu_1.addAction(self.action_1_5)
        self.menu_1.addSeparator()
        self.menu_1.addAction(self.action_1_6)

        self.action_2_1 = QtWidgets.QAction("撤销", self.handle.mainWindow)
        self.action_2_2 = QtWidgets.QAction("剪切", self.handle.mainWindow)
        self.action_2_3 = QtWidgets.QAction("复制", self.handle.mainWindow)
        self.action_2_4 = QtWidgets.QAction("粘贴", self.handle.mainWindow)
        self.action_2_5 = QtWidgets.QAction("未命名_1", self.handle.mainWindow)
        self.action_2_6 = QtWidgets.QAction("未命名_2", self.handle.mainWindow)
        self.menu_2.addAction(self.action_2_1)
        self.menu_2.addSeparator()
        self.menu_2.addAction(self.action_2_2)
        self.menu_2.addAction(self.action_2_3)
        self.menu_2.addAction(self.action_2_4)
        self.menu_2.addSeparator()
        # self.menu_2.addAction(self.action_2_5)
        # self.menu_2.addAction(self.action_2_6)

        self.action_3_1 = QtWidgets.QAction("单位", self.handle.mainWindow)
        self.action_3_2 = QtWidgets.QAction("采样周期", self.handle.mainWindow)
        self.action_3_3 = QtWidgets.QAction("运行时长", self.handle.mainWindow)
        self.action_3_4 = QtWidgets.QAction("主机IP", self.handle.mainWindow)
        self.action_3_5 = QtWidgets.QAction("传感器坐标", self.handle.mainWindow)
        self.action_3_5.triggered.connect(self.input_sensor_location)
        self.action_3_6 = QtWidgets.QAction("配色样式", self.handle.mainWindow)
        self.menu_3.addAction(self.action_3_1)
        self.menu_3.addAction(self.action_3_2)
        self.menu_3.addAction(self.action_3_3)
        self.menu_3.addSeparator()
        self.menu_3.addAction(self.action_3_4)
        self.menu_3.addAction(self.action_3_5)
        self.menu_3.addSeparator()
        self.menu_3.addAction(self.action_3_6)

        self.action_4_1 = QtWidgets.QAction("开始", self.handle.mainWindow)
        self.action_4_2 = QtWidgets.QAction("暂停", self.handle.mainWindow)
        self.action_4_3 = QtWidgets.QAction("停止", self.handle.mainWindow)
        self.action_4_4 = QtWidgets.QAction("未命名_1", self.handle.mainWindow)
        self.action_4_5 = QtWidgets.QAction("未命名_2", self.handle.mainWindow)
        self.action_4_6 = QtWidgets.QAction("未命名_3", self.handle.mainWindow)
        self.menu_4.addAction(self.action_4_1)
        self.menu_4.addAction(self.action_4_2)
        self.menu_4.addAction(self.action_4_3)
        self.menu_4.addSeparator()
        # self.menu_4.addAction(self.action_4_4)
        # self.menu_4.addAction(self.action_4_5)
        self.menu_4.addSeparator()
        # self.menu_4.addAction(self.action_4_6)

        self.action_5_1 = QtWidgets.QAction("调试窗口", self.handle.mainWindow)
        self.action_5_2 = QtWidgets.QAction("Mote模式", self.handle.mainWindow)
        self.action_5_3 = QtWidgets.QAction("未命名_0", self.handle.mainWindow)
        self.action_5_4 = QtWidgets.QAction("未命名_1", self.handle.mainWindow)
        self.action_5_5 = QtWidgets.QAction("未命名_2", self.handle.mainWindow)
        self.action_5_6 = QtWidgets.QAction("未命名_3", self.handle.mainWindow)
        self.menu_5.addAction(self.action_5_1)
        self.isDebug = True
        self.action_5_1.triggered.connect(self.change_mode)
        self.menu_5.addAction(self.action_5_2)
        self.menu_5.addSeparator()
        # self.menu_5.addAction(self.action_5_3)
        # self.menu_5.addAction(self.action_5_4)
        # self.menu_5.addAction(self.action_5_5)
        # self.menu_5.addAction(self.action_5_6)

        self.action_6_1 = QtWidgets.QAction("帮助", self.handle.mainWindow)
        self.action_6_2 = QtWidgets.QAction("关于", self.handle.mainWindow)
        self.action_6_3 = QtWidgets.QAction("更新", self.handle.mainWindow)
        self.action_6_4 = QtWidgets.QAction("未命名_1", self.handle.mainWindow)
        self.action_6_5 = QtWidgets.QAction("未命名_2", self.handle.mainWindow)
        self.action_6_6 = QtWidgets.QAction("未命名_3", self.handle.mainWindow)
        self.menu_6.addAction(self.action_6_1)
        self.menu_6.addAction(self.action_6_2)
        self.action_6_2.triggered.connect(self.dialog_about)
        self.menu_6.addSeparator()
        self.menu_6.addAction(self.action_6_3)
        # self.menu_6.addAction(self.action_6_4)
        # self.menu_6.addAction(self.action_6_5)
        # self.menu_6.addAction(self.action_6_6)

        self.menuBar.addAction(self.menu_1.menuAction())
        self.menuBar.addAction(self.menu_2.menuAction())
        self.menuBar.addAction(self.menu_3.menuAction())
        self.menuBar.addAction(self.menu_4.menuAction())
        self.menuBar.addAction(self.menu_5.menuAction())
        self.menuBar.addAction(self.menu_6.menuAction())

        # initial status bar
        self.statusBar = QtWidgets.QStatusBar(self.handle.mainWindow)
        self.statusBar.setFixedSize(600, 25)
        self.handle.mainWindow.setStatusBar(self.statusBar)
        self.versionLabel = QtWidgets.QLabel("PD Monitor System v 0.1")
        self.connectStateLabel = QtWidgets.QLabel("No connection")
        self.statusBar.addWidget(self.versionLabel)
        self.statusBar.addWidget(self.connectStateLabel)

    def openfile(self):
        # directory1 = QtWidgets.QFileDialog.getExistingDirectory(self.centralWidget, "选取文件夹", "C:/")
        # print(directory1)

        # 设置文件扩展名过滤,注意用双分号间隔
        file_name, file_type = QtWidgets.QFileDialog.getOpenFileName(self.handle.centralWidget, "选取文件", here,
                                                                     "All Files (*);;Text Files (*.txt)")
        print(file_name, file_type)
        """
        files, ok1 = QtWidgets.QFileDialog.getOpenFileNames(self.centralWidget,
        "多文件选择", "C:/", "All Files (*);;Text Files (*.txt)")
        print(files, ok1)

        fileName2, ok2 = QtWidgets.QFileDialog.getSaveFileName(self.centralWidget,
        "文件保存", "C:/", "All Files (*);;Text Files (*.txt)")
        """

    def input_sensor_location(self):
        self.handle.dialogWindow.show()

    # change mode: debug/normal
    def change_mode(self):
        if self.isDebug:
            self.isDebug = False
            self.handle.testWidget.setVisible = False
            self.handle.testWidget.setFixedSize(0, 700)
            self.handle.mainWindow.setFixedSize(920, 700)
            self.action_5_1.setText("切换至调试模式")
        else:
            self.isDebug = True
            self.handle.testWidget.setVisible = True
            self.handle.testWidget.setFixedSize(380, 700)
            self.handle.mainWindow.setFixedSize(1300, 700)
            self.action_5_1.setText("切换至普通模式")

    # 消息：关于
    def dialog_about(self):
        app_name = "Partial Discharge Monitor System 1.0"
        app_rights = unichr(169)+'2017-2020 GEIRI Europe CPS All rights reserved'
        QtWidgets.QMessageBox.about(self.handle.mainWindow, "About", app_name+'\n'+app_rights)
