# -*- coding: utf-8 -*-
import sys
import os
import threading
import random

from NotifListener import NotifListener
from WidgetWiHaConnect import WidgetWiHaConnect
from PdStyle import PdStyle
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
from PyQt5 import QtCore, QtGui, QtWidgets

if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))


class MoteUI(object):
    def __init__(self, gui_lock):
        self.guiLock = gui_lock
        self.connector = None
        self.commandArray = []
        self.fields = {}
        self.last_state = 1

        self.TopLayoutWidget = QtWidgets.QWidget()
        self.TopLayout = QtWidgets.QVBoxLayout(self.TopLayoutWidget)
        # initial join frame
        self.JoinLayoutWidget = QtWidgets.QWidget()
        self.JoinLayoutWidget.setFixedSize(380, 40)
        self.TopLayout.addWidget(self.JoinLayoutWidget)
        self.JoinLayout = QtWidgets.QHBoxLayout(self.JoinLayoutWidget)
        self.NwStatusLabel = QtWidgets.QLabel(self.JoinLayoutWidget)
        self.NwStatusLabel.setText("NetworkStatus:")
        self.NwStatusResultLabel = QtWidgets.QLabel()
        self.NwStatusResultLabel.setStyleSheet("background:" + PdStyle.COLOR_BG)
        self.JoinButton = QtWidgets.QPushButton()
        self.JoinButton.setText("join")
        self.JoinButton.clicked.connect(self.join)
        self.JoinLayout.addWidget(self.NwStatusLabel)
        self.JoinLayout.addWidget(self.NwStatusResultLabel)
        self.JoinLayout.addWidget(self.JoinButton)

        # initial sendResponse(or command) frame
        self.CommandLayoutWidget = QtWidgets.QWidget()
        self.CommandLayoutWidget.setFixedSize(380, 120)
        self.TopLayout.addWidget(self.CommandLayoutWidget)
        self.CommandLayout = QtWidgets.QVBoxLayout(self.CommandLayoutWidget)
        self.CommandLabel = QtWidgets.QLabel()
        self.CommandLabel.setText("SendResponse")
        self.CommandLineEdit = QtWidgets.QLineEdit()
        self.CommandButton = QtWidgets.QPushButton()
        self.CommandButton.setText("Send")

        # self.CommandButton.clicked.connect(self.send_response)
        self.CommandLayout.addWidget(self.CommandLabel)
        self.CommandLayout.addWidget(self.CommandLineEdit)
        self.CommandLayout.addWidget(self.CommandButton)

        self.sampleLayout = QtWidgets.QHBoxLayout()
        self.CommandLayout.addLayout(self.sampleLayout)
        self.samplebutton1 = QtWidgets.QPushButton("5s")
        self.samplebutton2 = QtWidgets.QPushButton("1s")
        self.samplebutton3 = QtWidgets.QPushButton("开始")
        self.sampleLayout.addWidget(self.samplebutton1)
        self.sampleLayout.addWidget(self.samplebutton2)
        self.sampleLayout.addWidget(self.samplebutton3)
        self.samplebutton1.clicked.connect(self._sample_button_1)
        self.samplebutton2.clicked.connect(self._sample_button_2)
        self.samplebutton3.clicked.connect(self._sample_button_3)


        # initial notification widget
        self.NotifLayoutWidget = QtWidgets.QWidget()
        self.NotifLayoutWidget.setFixedSize(380, 300)
        self.TopLayout.addWidget(self.NotifLayoutWidget)
        self.NotifLayout = QtWidgets.QVBoxLayout(self.NotifLayoutWidget)
        self.NotifLabel = QtWidgets.QLabel("Notification")
        self.NotifContentLabel = QtWidgets.QTextBrowser()
        self.NotifContentLabel.setStyleSheet("background:" + PdStyle.COLOR_BG)
        self.NotifLayout.addWidget(self.NotifLabel)
        self.NotifLayout.addWidget(self.NotifContentLabel)

        # timer
        self.joinTimer = QtCore.QTimer()
        self.reportTimer = QtCore.QTimer()
        self.reportTimer.timeout.connect(self.data_report)

    # send ['getParameter', 'moteStatus']
    # update network status
    def get_network_status(self):
        if self.connector:
            self.commandArray = ['getParameter', 'moteStatus']
            self.fields = {}
            self._handel_command()

            state = self.response_fields['state']

            if state == 1:
                self.NwStatusResultLabel.setText("idle")
                if self.JoinButton.text() == "disconnect":
                    self.JoinButton.clicked.disconnect(self.unjoin)
                    self.JoinButton.setText("join")
                    self.JoinButton.clicked.connect(self.join)
                    self.JoinButton.Enabled = True
                if self.last_state == 5 and self.joinTimer.isActive():
                    # self.joinTimer.timeout.disconnect(self.get_network_status)
                    self.joinTimer.stop()
            elif state == 2:
                self.NwStatusResultLabel.setText("searching")
                self.JoinButton.Enabled = False
            elif state == 3:
                self.NwStatusResultLabel.setText("negotiating")
                self.JoinButton.Enabled = False
            elif state == 4:
                self.NwStatusResultLabel.setText("connected")
                self.JoinButton.Enabled = False
            elif state == 5:
                self.NwStatusResultLabel.setText("operational")
                if self.JoinButton.text() == "join":
                    self.JoinButton.clicked.disconnect(self.join)
                    self.JoinButton.setText("disconnect")
                    self.JoinButton.clicked.connect(self.unjoin)
                    self.JoinButton.Enabled = True
                if self.last_state == 1 and self.joinTimer.isActive():
                    # self.joinTimer.timeout.disconnect(self.get_network_status)
                    self.joinTimer.stop()

    # ask the mote to join in Manager Network
    def join(self):
        self.commandArray = ['join']
        self.fields = {}
        self._handel_command()
        self.last_state = 1
        self.joinTimer.timeout.connect(self.get_network_status)
        self.joinTimer.start(2000)

    # disconnect the mote from the Manager Network
    def unjoin(self):
        self.commandArray = ['disconnect']
        self.fields = {}
        self._handel_command()
        self.last_state = 5
        self.joinTimer.timeout.connect(self.get_network_status)
        self.joinTimer.start(2000)

    # send "payload" to the Manager([249.129])
    def send_response(self,  payload):
        self.commandArray = ['send']
        self.fields = {'tranDir': False,
                       'reserved': 0,
                       'seqNum': 1,
                       'appDomain': 0,
                       'payloadLen': 6,
                       'priority': 2,
                       'serviceId': 1,
                       'destAddr': [249, 129],
                       'payload': payload,
                       'tranType': False}
        self._handel_command()

    # sample interval: 5000 ms
    def _sample_button_1(self):
        self.reportTimer.setInterval(5000)

    # sample interval: 1000 ms
    def _sample_button_2(self):
        self.reportTimer.setInterval(1000)

    # start to send data
    def _sample_button_3(self):
        self.reportTimer.start(1000)

    # send sample to Manager
    def data_report(self):
        payload = []
        # generate random integral to simulate sampling
        for i in range(70):
            payload.append(random.randint(0, 255))
        self.send_response(payload)

    # Internal command: send [commandArray,fields] to Mote
    def _handel_command(self):
        # print self.commandArray, self.fields
        # print self.connector
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

    # update NotifContent with Response
    def _response_cb(self, fields):
        self.NotifContentLabel.setText(str(fields))
        print fields

    def _response_error_cb(self, param):
        self.NotifContentLabel.setText(" _responseErrorCb called with param="+str(param))
        print " _responseErrorCb called with param="+str(param)

    # eliminate "static function" warning
    def _is_not_used(self):
        pass


class MoteApp(object):
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.mainWindow = QtWidgets.QMainWindow()
        self.mainWindow.setFixedSize(400, 600)
        self.guiLock = threading.Lock()
        self.lastNotifLock = threading.Lock()
        self.notifTimer = QtCore.QTimer()
        self.is_connected = False
        self.lastNotif = None
        self.centralWidget = QtWidgets.QWidget(self.mainWindow)
        self.centralWidget.setGeometry(QtCore.QRect(0, 0, 400, 600))
        self.centralLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.connectUI = WidgetWiHaConnect(self.guiLock, self._connect_cb, self._disconnect_cb)
        self.api_def = HartMoteDefinition.HartMoteDefinition()
        self.connectUI.api_loaded(self.api_def)
        self.MoteUI = MoteUI(self.guiLock)
        self.centralLayout.addWidget(self.connectUI.TopLayoutWidget)
        self.centralLayout.addWidget(self.MoteUI.TopLayoutWidget)

        self.mainWindow.show()

        sys.exit(self.app.exec_())

    def _close_cb(self):
        self._close_cb()
        print " _closeCb called"

    def _connect_cb(self, params):
        self.is_connected = True
        self.MoteUI.connector = self.connectUI.connector
        print " _connectCb called with param="+str(params)

        # add notification listener
        self.notifListener = NotifListener(self.connectUI.connector,
                                           self._notif_rx_callback,
                                           self._disconnect_cb)
        self.notifListener.start()
        self.notifTimer.timeout.connect(self._checkNotif)
        self.notifTimer.start(1000)
        print "NotifListener Started"

    def _notif_rx_callback(self, notif):
        with self.lastNotifLock:
            self.lastNotif = notif

    def _getLastNotif(self):
        # print("checking")
        with self.lastNotifLock:
            returnVal = self.lastNotif
            self.lastNotif = None
            return returnVal

    def _checkNotif(self):
        # check if notification and update GUI
        notif = self._getLastNotif()
        if notif:
            print "notif received"
            # this is the place to handle with the data received.
            # the example sends back the same data once it receives
            if notif[0] == ['dataReceived']:
                print notif[1]['data']
                self.MoteUI.send_response(notif[1]['data'])

    def _disconnect_cb(self):
        self.is_connected = False
        self.connectUI.connector = None
        self.MoteUI.connector = None
        self.notifTimer.stop()
        print "disconnect cb called"

    def _is_not_used(self):
        pass


if __name__ == "__main__":
    import sys
    MoteApp()
# End of pdMote
