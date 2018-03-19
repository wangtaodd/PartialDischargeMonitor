# -*- coding: utf-8 -*-
import sys
import os
import threading
import random
import csv
from Sensor import Sensor
from PlotCanvas import PlotCanvas
from PyQt5 import QtCore, QtGui, QtWidgets
from SetSensorDialog import SetSensorDialog
from NotifListener import NotifListener
from PdStyle import PdStyle
from WidgetSocket import WidgetSocket
from WidgetWiHaConnect import WidgetWiHaConnect
from WidgetMenuBar import WidgetMenuBar
from DataProcessor import DataProcessor
from StaticFunction import clear_layout
from csvHeaderCheck import checkHeader
from SmartMeshSDK.ApiDefinition import IpMgrDefinition,       \
                                        IpMoteDefinition,      \
                                        HartMgrDefinition,     \
                                        HartMoteDefinition
from SmartMeshSDK.HartMgrConnector import HartMgrConnector
from SmartMeshSDK.HartMoteConnector import HartMoteConnector
from SmartMeshSDK.ApiException import CommandError, \
                                      ConnectionError, \
                                      APIError,\
                                      QueueError

if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))


class ManagerUI(object):
    def __init__(self):
        self.sensor_counter = 0
        self.sensor = []
        self.dataProcessor = DataProcessor()
        self.PdLocation = None
        self.app = QtWidgets.QApplication(sys.argv)

        self.guiLock = threading.Lock()
        self.lastNotifLock = threading.Lock()

        self.notifTimer = QtCore.QTimer()
        self.is_connected = False
        self.lastNotif = None

        self.api_def = HartMgrDefinition.HartMgrDefinition()

        self.connector = None
        self.commandArray = []
        self.fields = {}
        self.last_state = 1

        self.mainWindow = QtWidgets.QMainWindow()
        self.mainWindow.setFixedSize(1300, 720)

        self.centralWidget = QtWidgets.QWidget(self.mainWindow)
        self.mainWindow.setCentralWidget(self.centralWidget)
        self.TopLayout = QtWidgets.QHBoxLayout(self.centralWidget)

        # initial dialog window
        self.dialogWindow = SetSensorDialog(self)
        self.bar = WidgetMenuBar(self)

        # initial main frame
        self.monitorWidget = QtWidgets.QWidget()
        self.monitorWidget.setFixedSize(900, 700)
        self.testWidget = QtWidgets.QWidget()
        self.testWidget.setFixedSize(380, 700)
        self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setFixedSize(10, 700)
        self.TopLayout.addWidget(self.monitorWidget)
        self.TopLayout.addWidget(self.line)
        self.TopLayout.addWidget(self.testWidget)

        # initial wave frame+ button frame
        self.upWidget = QtWidgets.QWidget()
        self.upWidget.setFixedSize(900, 340)
        self.downWidget = QtWidgets.QWidget()
        self.downWidget.setFixedSize(900, 340)
        self.monitorLayout = QtWidgets.QVBoxLayout(self.monitorWidget)
        self.monitorLayout.addWidget(self.upWidget)
        self.monitorLayout.addWidget(self.downWidget)

        # initial upFrame
        self.upLayout = QtWidgets.QHBoxLayout(self.upWidget)
        self.waveWidget = QtWidgets.QTabWidget()
        self.waveWidget.setFixedSize(680, 330)
        self.upLayout.addWidget(self.waveWidget)

        # initial wave Frame
        self.tab = QtWidgets.QWidget()
        self.waveWidget.addTab(self.tab, "")
        self.waveWidget.setTabText(self.waveWidget.indexOf(self.tab), "传感器布局及局放位置示意图")
        self.sensorMap = PlotCanvas(self.tab, 6, 3, 100)


        self.buttonWidget = QtWidgets.QWidget()
        self.buttonWidget.setFixedSize(200, 330)
        self.upLayout.addWidget(self.buttonWidget)



        self.init_sensor_map()

        # initial button frame
        self.buttonLayout = QtWidgets.QVBoxLayout(self.buttonWidget)
        self.buttonWidget1 = QtWidgets.QWidget()
        self.buttonWidget1.setFixedSize(180, 100)
        self.buttonWidget2 = QtWidgets.QWidget()
        self.buttonWidget2.setFixedSize(180, 80)
        self.buttonLayoutSpacer = QtWidgets.QSpacerItem(180, 100)
        self.buttonLayout.addWidget(self.buttonWidget1)
        self.buttonLayout.addItem(self.buttonLayoutSpacer)
        self.buttonLayout.addWidget(self.buttonWidget2)

        self.buttonLayout1 = QtWidgets.QVBoxLayout(self.buttonWidget1)
        self.buttonLayout2 = QtWidgets.QGridLayout(self.buttonWidget2)
        self.beginButton = QtWidgets.QPushButton("开始")
        self.beginButton.clicked.connect(self.saveData)
        self.pauseButton = QtWidgets.QPushButton("暂停")
        self.stopButton = QtWidgets.QPushButton("停止")
        self.buttonLayout1.addWidget(self.beginButton)
        self.buttonLayout1.addWidget(self.pauseButton)
        self.buttonLayout1.addWidget(self.stopButton)

        self.sampleTimeLabel = QtWidgets.QLabel("采样周期：")
        self.runTimeLabel = QtWidgets.QLabel("运行时长：")
        self.sampleTimeCombo = QtWidgets.QComboBox()
        self.sampleTimeCombo.addItem("0.5s")
        self.sampleTimeCombo.addItem("1s")
        self.sampleTimeCombo.addItem("3s")
        self.runTimeCombo = QtWidgets.QComboBox()
        self.runTimeCombo.addItem("5 min")
        self.runTimeCombo.addItem("10 min")
        self.runTimeCombo.addItem("15 min")
        self.buttonLayout2.addWidget(self.sampleTimeLabel, 0, 0, 1, 1)
        self.buttonLayout2.addWidget(self.sampleTimeCombo, 0, 1, 1, 1)
        self.buttonLayout2.addWidget(self.runTimeLabel, 1, 0, 1, 1)
        self.buttonLayout2.addWidget(self.runTimeCombo, 1, 1, 1, 1)

        # initial downFrame
        self.downLayout = QtWidgets.QHBoxLayout(self.downWidget)
        self.tableWidget = QtWidgets.QWidget()
        self.tableWidget.setFixedSize(680, 330)
        self.displayWidget = QtWidgets.QWidget()
        self.displayWidget.setFixedSize(200, 330)
        self.downLayout.addWidget(self.tableWidget)
        self.downLayout.addWidget(self.displayWidget)

        self.init_table()

        # initial display frame
        self.displayLayout_0 = QtWidgets.QVBoxLayout(self.displayWidget)
        self.displayLayout = QtWidgets.QGridLayout()
        self.displayLayout_0.addLayout(self.displayLayout)
        self.dataSizeLabel = QtWidgets.QLabel("已接受收据：")
        self.dataSizeNum = QtWidgets.QLabel("80/100 MB")
        self.dataProgressLabel = QtWidgets.QLabel("已接受收据：")
        self.dataProgress = QtWidgets.QProgressBar()
        self.dataProgress.setValue(80)
        self.pdNumLabel = QtWidgets.QLabel("局放次数：")
        self.pdNum = QtWidgets.QLabel("3 次")
        self.runStateLLabel = QtWidgets.QLabel("运行状态:")
        self.runState = QtWidgets.QLabel("准备就绪")
        self.pdReport = QtWidgets.QLabel("局放事件报告：\n1.")
        self.pdReport.setStyleSheet("background:" + PdStyle.COLOR_BG)
        self.pdReport.setAlignment(QtCore.Qt.AlignTop)
        self.pdReport.setFixedSize(180, 200)
        self.displaySpacer = QtWidgets.QSpacerItem(100, 30)

        self.displayLayout.addWidget(self.runStateLLabel, 0, 0, 1, 1)
        self.displayLayout.addWidget(self.runState, 0, 1, 1, 1)
        self.displayLayout.addWidget(self.dataSizeLabel, 1, 0, 1, 1)
        self.displayLayout.addWidget(self.dataSizeNum, 1, 1, 1, 1)
        self.displayLayout.addWidget(self.dataProgressLabel, 2, 0, 1, 1)
        self.displayLayout.addWidget(self.dataProgress, 2, 1, 1, 1)
        self.displayLayout.addWidget(self.pdNumLabel, 3, 0, 1, 1)
        self.displayLayout.addWidget(self.pdNum, 3, 1, 1, 1)
        # self.displayLayout.addWidget(self.pdReport, 4, 0, 1, 1)
        self.displayLayout_0.addWidget(self.pdReport)
        self.displayLayout_0.addItem(self.displaySpacer)

        # initial test frame
        self.testLayout = QtWidgets.QVBoxLayout(self.testWidget)
        self.WiHaConnectWidget = WidgetWiHaConnect(self.guiLock, self._connect_cb, self._disconnect_cb)
        self.WiHaConnectWidget.api_loaded(self.api_def)
        self.testLayout.addWidget(self.WiHaConnectWidget.TopLayoutWidget)
        self.SocketWidget = WidgetSocket()
        self.testLayout.addWidget(self.SocketWidget.TopWidget)

        # initial sendResponse(or command) frame
        self.CommandLayoutWidget = QtWidgets.QWidget()
        self.CommandLayoutWidget.setFixedSize(380, 120)
        self.testLayout.addWidget(self.CommandLayoutWidget)
        self.CommandLayout = QtWidgets.QVBoxLayout(self.CommandLayoutWidget)
        self.CommandLabel = QtWidgets.QLabel()
        self.CommandLabel.setText("SendResponse")
        self.CommandLineEdit = QtWidgets.QLineEdit()
        self.CommandButton = QtWidgets.QPushButton()
        self.CommandButton.setText("Send")
        self.CommandButton.clicked.connect(self.send_response)
        self.CommandLayout.addWidget(self.CommandLabel)
        self.CommandLayout.addWidget(self.CommandLineEdit)
        self.CommandLayout.addWidget(self.CommandButton)

        # initial notification widget
        self.NotifLayoutWidget = QtWidgets.QWidget()
        self.NotifLayoutWidget.setFixedSize(380, 200)
        self.testLayout.addWidget(self.NotifLayoutWidget)
        self.NotifLayout = QtWidgets.QVBoxLayout(self.NotifLayoutWidget)
        self.NotifLabel = QtWidgets.QLabel("Notification")
        self.NotifContentLabel = QtWidgets.QTextBrowser()
        self.NotifContentLabel.setStyleSheet("background:" + PdStyle.COLOR_BG)
        self.NotifLayout.addWidget(self.NotifLabel)
        self.NotifLayout.addWidget(self.NotifContentLabel)

        # timer
        self.joinTimer = QtCore.QTimer()

        self.mainWindow.show()
        sys.exit(self.app.exec_())

    def saveData(self):
        data = 'example'
        self.dataProcessor.save_data_by_sensor(self.sensor[0], data)

    def getPdLocation(self):
        data = 'this is the data for the calculation of partial discharge location'
        self.PdLocation = self.dataProcessor.getPdLocation(data)

    def init_sensor_map(self):


        self.sensor_counter, location = self.dataProcessor.read_sensor_location()
        location_trans = [[0 for col in range(int(self.sensor_counter))]for row in range(2)]
        for i in range(int(self.sensor_counter)):
            self.sensor.append(Sensor(0, i, [location[i][0], location[i][1]]))
            location_trans[0][i] = location[i][0]
            location_trans[1][i] = location[i][1]
        # draw an example
        self.getPdLocation()


        self.waveWidget.clear()

        # initial wave Frame
        # self.tempTab: solve the problem that when a TabWidget is cleared, the first tab is not blank
        # add a tempTab as the first Tab and then delete
        self.tempTab = QtWidgets.QWidget()
        self.waveWidget.addTab(self.tempTab, "")

        self.tab = QtWidgets.QWidget()
        self.waveWidget.addTab(self.tab, "")
        self.waveWidget.setTabText(self.waveWidget.indexOf(self.tab), "传感器布局及局放位置示意图")
        self.sensorMap = PlotCanvas(self.tab, 6, 3, 100)

        self.waveWidget.removeTab(self.waveWidget.indexOf(self.tempTab))

        self.sensorMap.ax.clear()
        self.sensorMap.ax.scatter(location_trans[0], location_trans[1])
        self.sensorMap.ax.scatter(self.PdLocation[0][0], self.PdLocation[0][1], 30, 'r')
        # self.sensorMap.ax.axis([0, 5, 0, 3])
        self.sensorMap.draw()

        # initial waveform display
        self.sensorWaveWidget = [None for row in range(self.sensor_counter)]
        self.sensorWave = [None for row in range(self.sensor_counter)]

        for i in range(self.sensor_counter):
            self.sensorWaveWidget[i] = QtWidgets.QWidget()
            self.waveWidget.addTab(self.sensorWaveWidget[i], "")
            self.waveWidget.setTabText(self.waveWidget.indexOf(self.sensorWaveWidget[i]), str(i+1)+"号波形")
            self.sensorWave[i] = PlotCanvas(self.sensorWaveWidget[i], 6, 3, 100)

        # example of removing a canvas tab
        # self.waveWidget.removeTab(self.waveWidget.indexOf(self.sensorWaveWidget[2]))
        # example of adding a canvas tab
        # self.waveWidget.addTab(self.sensorWaveWidget[2], "")

    def init_table(self):
        # initial table frame
        self.tableLayout = QtWidgets.QGridLayout(self.tableWidget)
        self.tableLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.tableLayout.setContentsMargins(0, 0, 0, 0)
        self.tableLayout.setSpacing(0)
        self.update_table()

    def update_table(self):
        clear_layout(self.tableLayout)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)

        self.tableTitle1 = QtWidgets.QLabel("编号")
        self.tableTitle1.setSizePolicy(sizePolicy)
        self.tableTitle1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tableTitle1.setAlignment(QtCore.Qt.AlignCenter)
        self.tableTitle2 = QtWidgets.QLabel("坐标")
        self.tableTitle2.setSizePolicy(sizePolicy)
        self.tableTitle2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tableTitle2.setAlignment(QtCore.Qt.AlignCenter)
        self.tableTitle3 = QtWidgets.QLabel("信号强度")
        self.tableTitle3.setSizePolicy(sizePolicy)
        self.tableTitle3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tableTitle3.setAlignment(QtCore.Qt.AlignCenter)
        self.tableTitle4 = QtWidgets.QLabel("采集时间")
        self.tableTitle4.setSizePolicy(sizePolicy)
        self.tableTitle4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tableTitle4.setAlignment(QtCore.Qt.AlignCenter)
        self.tableTitle5 = QtWidgets.QLabel("连接状态")
        self.tableTitle5.setSizePolicy(sizePolicy)
        self.tableTitle5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.tableTitle5.setAlignment(QtCore.Qt.AlignCenter)
        self.tableLayout.addWidget(self.tableTitle1, 0, 0, 1, 1)
        self.tableLayout.addWidget(self.tableTitle2, 0, 1, 1, 1)
        self.tableLayout.addWidget(self.tableTitle3, 0, 2, 1, 1)
        self.tableLayout.addWidget(self.tableTitle4, 0, 3, 1, 1)
        self.tableLayout.addWidget(self.tableTitle5, 0, 4, 1, 1)

        self.sensorTable = [[0 for col in range(5)] for row in range(self.sensor_counter)]
        for i in range(self.sensor_counter):
            self.sensorTable[i][0] = QtWidgets.QLabel(str(i+1))
            self.sensorTable[i][0].setSizePolicy(sizePolicy)
            self.sensorTable[i][0].setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.sensorTable[i][0].setAlignment(QtCore.Qt.AlignCenter)
            self.tableLayout.addWidget(self.sensorTable[i][0], i+1, 0, 1, 1)
            self.sensorTable[i][1] = QtWidgets.QLabel(str(self.sensor[i].location))
            self.sensorTable[i][1].setSizePolicy(sizePolicy)
            self.sensorTable[i][1].setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.sensorTable[i][1].setAlignment(QtCore.Qt.AlignCenter)
            self.tableLayout.addWidget(self.sensorTable[i][1], i+1, 1, 1, 1)
            self.sensorTable[i][2] = QtWidgets.QLabel(str(random.randint(1,100)))
            self.sensorTable[i][2].setSizePolicy(sizePolicy)
            self.sensorTable[i][2].setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.sensorTable[i][2].setAlignment(QtCore.Qt.AlignCenter)
            self.tableLayout.addWidget(self.sensorTable[i][2], i+1, 2, 1, 1)
            self.sensorTable[i][3] = QtWidgets.QLabel("2017-12-12")
            self.sensorTable[i][3].setSizePolicy(sizePolicy)
            self.sensorTable[i][3].setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.sensorTable[i][3].setAlignment(QtCore.Qt.AlignCenter)
            self.tableLayout.addWidget(self.sensorTable[i][3], i+1, 3, 1, 1)
            self.sensorTable[i][4] = QtWidgets.QLabel("未连接")
            self.sensorTable[i][4].setSizePolicy(sizePolicy)
            self.sensorTable[i][4].setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.sensorTable[i][4].setAlignment(QtCore.Qt.AlignCenter)
            self.tableLayout.addWidget(self.sensorTable[i][4], i+1, 4, 1, 1)
        self.tableSpacer = QtWidgets.QSpacerItem(20, 50)
        self.tableLayout.addItem(self.tableSpacer, self.sensor_counter+1, 0, 1, 1)

    def send_response(self):
        self.commandArray = ['sendRequest']
        self.fields = {'priority': 'high',
                       'domain': 'maintenance',
                       'macAddr': '00-17-0D-00-00-58-F3-12',
                       'data': [0, 0, 18, 252],
                       'reliable': False}
        self._handel_command()

    def _handel_command(self):
        try:
            self.response_fields = self.connector.send(self.commandArray, self.fields)
            print (self.commandArray, self.fields)
        except CommandError as err:
            self._response_error_cb(str(err))
        except AttributeError as err:
            self._response_error_cb('Not connected')
            print err
        except (ConnectionError, APIError) as err:
            self._response_error_cb(str(err))
        else:
            self._response_cb(self.response_fields)

    def _response_cb(self, fields):
        self.NotifContentLabel.setText(str(fields))
        print fields

    def _response_error_cb(self, param):
        self.NotifContentLabel.setText(" _responseErrorCb called with param="+str(param))
        print " _responseErrorCb called with param="+str(param)

    def _close_cb(self):
        self._close_cb()
        print "_closeCb called"

    def _notif_rx_callback(self, notif):
        with self.lastNotifLock:
            self.lastNotif = notif

    def _check_notif(self):
        # check if notification and update GUI
        with self.lastNotifLock:
            notif = self.lastNotif
            self.lastNotif = None
            self.display_notif(notif)

# TODO: decouple the file process with notif
    def display_notif(self, notif):
        if notif:
            print "notif received"
            self.NotifContentLabel.setText(str(notif))
            if notif[0] == ['data']:
                checkHeader('data.csv', notif[1].keys())
                with open('data.csv', 'a') as csvFile:
                    fieldnames = notif[1].keys()
                    writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
                    writer.writerow(notif[1])
            fileName = 'data.csv'
            self.updateWave(0, fileName)


    def updateWave(self, num, fileName):
        with open(fileName, 'r') as csvFile:
            reader = csv.DictReader(csvFile)
            for row in reader:
                pass
            self.sensorWave[num].ax.clear()
            self.sensorWave[num].ax.plot([float(x) for x in row['payload'].strip('[]').split(',')])
            self.sensorWave[num].draw()

    def _connect_cb(self, params):
        self.is_connected = True
        print " _connectCb called with param="+str(params)
        self.connector = self.WiHaConnectWidget.connector
        # add notification listener
        self.notifListener = NotifListener(self.connector,
                                           self._notif_rx_callback,
                                           self._disconnect_cb)
        self.notifListener.start()
        self.notifTimer.timeout.connect(self._check_notif)
        self.notifTimer.start(1000)
        print "NotifListener Started"

        # subscribe 'data' notification
        self.commandArray = ['subscribe']
        self.fields = {'filter': 'data'}
        self._handel_command()

    def _disconnect_cb(self):
        self.is_connected = False
        self.connector = None
        self.notifTimer.stop()

    # method to remove the static method warning
    def _is_not_used(self):
        pass


if __name__ == "__main__":
    import sys
    ManagerUI()
