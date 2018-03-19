# -*- coding: utf-8 -*-
import sys
import os
import threading
from PdStyle import PdStyle
from SmartMeshSDK.ApiDefinition import IpMgrDefinition,       \
                                        IpMoteDefinition,      \
                                        HartMgrDefinition,     \
                                        HartMoteDefinition
from SmartMeshSDK.HartMgrConnector import HartMgrConnector
from SmartMeshSDK.HartMoteConnector import HartMoteConnector
from SmartMeshSDK.ApiException import CommandError, \
                                      ConnectionError
from PyQt5 import QtCore, QtGui, QtWidgets

if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))


class WidgetWiHaConnect(object):
    def __init__(self, gui_lock, connect_cb, disconnect_cb):
        self.connect_cb = connect_cb
        self.disconnect_cb = disconnect_cb
        self.guiLock = gui_lock
        self.apiDef = None
        self.connector = None

        self.TopLayoutWidget = QtWidgets.QWidget()
        self.TopLayoutWidget.setFixedSize(400, 80)
        self.TopLayoutWidget.setObjectName("TopLayoutWidget")

        self.TopLayout = QtWidgets.QVBoxLayout(self.TopLayoutWidget)
        self.TopLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.TopLayout.setContentsMargins(0, 0, 0, 0)
        self.TopLayout.setSpacing(0)
        self.TopLayout.setObjectName("TopLayout")

        size_minimum = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        size_minimum.setHorizontalStretch(0)
        size_minimum.setVerticalStretch(0)
        size_minimum.setHorizontalStretch(0)
        size_minimum.setVerticalStretch(0)

        self.SerialLayoutWidget = QtWidgets.QWidget()
        self.SerialLayoutWidget.setFixedSize(380, 40)
        self.TopLayout.addWidget(self.SerialLayoutWidget)
        self.XmlLayoutWidget = QtWidgets.QWidget()
        self.XmlLayoutWidget.setFixedSize(380, 40)
        self.TopLayout.addWidget(self.XmlLayoutWidget)

        self.serial_layout = QtWidgets.QHBoxLayout(self.SerialLayoutWidget)
        self.serial_label = QtWidgets.QLabel()
        self.serial_label.setText("COM端口:")
        self.SerialCOMLabel = QtWidgets.QLineEdit()
        self.SerialCOMLabel.setText("COM11")
        self.SerialConnect = QtWidgets.QPushButton()
        self.SerialConnect.setText("连接")
        self.SerialConnect.clicked.connect(self._connect_serial)
        self.serial_layout.addWidget(self.serial_label)
        self.serial_layout.addWidget(self.SerialCOMLabel)
        self.serial_layout.addWidget(self.SerialConnect)

        self.XmlLayout = QtWidgets.QHBoxLayout(self.XmlLayoutWidget)
        self.XmlIpLabel = QtWidgets.QLabel()
        self.XmlIpLabel.setText("Host:")
        self.XmlIpLineEdit = QtWidgets.QLineEdit()
        self.XmlIpLineEdit.setText("192.168.99.100")
        self.XmlPortLabel = QtWidgets.QLabel()
        self.XmlPortLabel.setText("Port:")
        self.XmlPortLineEdit = QtWidgets.QLineEdit()
        self.XmlPortLineEdit.setText("4445")
        self.XmlConnect = QtWidgets.QPushButton()
        self.XmlConnect.setText("连接")
        self.XmlConnect.clicked.connect(self._connect_xml)
        self.XmlLayout.addWidget(self.XmlIpLabel)
        self.XmlLayout.addWidget(self.XmlIpLineEdit)
        self.XmlLayout.addWidget(self.XmlPortLabel)
        self.XmlLayout.addWidget(self.XmlPortLineEdit)
        self.XmlLayout.addWidget(self.XmlConnect)


    # ======================== public ==========================================
    def api_loaded(self, api_def):
        # call the parent's api_loaded function
        # dustFrame.dustFrame.api_loaded(self,api_def)
        self.apiDef = api_def
        # display/hide connection forms
        self._show_hide_connection_forms()

    def update_gui_disconnected(self):
        # update the connection fields
        self.guiLock.acquire()
        self.guiLock.release()
        # update the buttons
        self.guiLock.acquire()
        self.guiLock.release()
        # display/hide connection forms
        self._show_hide_connection_forms()

    # ======================== private =========================================
    def _show_hide_connection_forms(self):
        self.guiLock.acquire()
        if (
             isinstance(self.apiDef, IpMoteDefinition.IpMoteDefinition) or
             isinstance(self.apiDef, IpMgrDefinition.IpMgrDefinition) or
             isinstance(self.apiDef, HartMoteDefinition.HartMoteDefinition)
           ):
            self.SerialLayoutWidget.setVisible(True)
            self.XmlLayoutWidget.setVisible(False)
        if (
             isinstance(self.apiDef, IpMgrDefinition.IpMgrDefinition)
           ):
            self.SerialLayoutWidget.setVisible(True)
            self.XmlLayoutWidget.setVisible(True)
        if (
             isinstance(self.apiDef, HartMgrDefinition.HartMgrDefinition)
           ):
            self.SerialLayoutWidget.setVisible(False)
            self.XmlLayoutWidget.setVisible(True)
        self.guiLock.release()

    def _connect_serial(self):
        # initialize the connector
        try:
            if isinstance(self.apiDef, HartMoteDefinition.HartMoteDefinition):
                self.connector = HartMoteConnector.HartMoteConnector()
            else:
                raise SystemError
        except NotImplementedError as err:
            self.guiLock.acquire()
            # self.tipLabel.configure(text=str(err))
            pass
            self.guiLock.release()
            return

        # read connection params from GUI
        self.guiLock.acquire()
        connect_params = {
            'port': self.SerialCOMLabel.text().strip(),
        }
        self.guiLock.release()
        print connect_params
        # connect to the serial port
        try:
            self.connector.connect(connect_params)
        except ConnectionError as err:
            self.guiLock.acquire()
            # self.serialPortText.configure(bg=dustStyle.COLOR_ERROR)
            # self.tipLabel.configure(text=str(err))
            self.guiLock.release()
            return

        # if you get here, the connector could connect, i.e. the COM port is available

        # make sure that the device attached to the serial port is really the mote we expect
        if isinstance(self.apiDef, IpMgrDefinition.IpMgrDefinition):
            # nothing to do, since connecting to a manager includes a handshake
            pass

        elif isinstance(self.apiDef, IpMoteDefinition.IpMoteDefinition):
            try:
                res = self.connector.dn_getParameter_moteInfo()
                self._is_not_used(res)
            except (ConnectionError, CommandError) as err:

                # disconnect the connector
                self.connector.disconnect()

                # print error text
                output = []
                output += ["Could open the COM port, but issuing dn_getParameter_moteInfo() failed."]
                output += ["Exact error received: {0}".format(err)]
                output += ["Please verify that the device connected to {0} is a SmartMesh IP mote.".format(
                    connect_params['port'])]
                output += ["Please verify that the SmartMesh IP mote is configured in slave mode."]
                output = '\n'.join(output)
                self._is_not_used(output)
                self.guiLock.acquire()
                # self.serialPortText.configure(bg=dustStyle.COLOR_WARNING_NOTWORKING)
                # self.tipLabel.configure(text=output)
                self.guiLock.release()
                return

        elif isinstance(self.apiDef, HartMoteDefinition.HartMoteDefinition):

            try:
                res = self.connector.dn_getParameter_moteInfo()
                print res
            except (ConnectionError, CommandError) as err:
                # disconnect the connector
                self.connector.disconnect()

                # print error text
                output = []
                output += ["Could open the COM port, but issuing dn_getParameter_moteInfo() failed."]
                output += ["Exact error received: {0}".format(err)]
                output += [
                    "Please verify that the device connected to {0} is a SmartMesh WirelessHART mote.".
                    format(connect_params['port'])
                ]
                output += ["Please verify that the SmartMesh WirelessHART mote is configured in slave mode."]
                output = '\n'.join(output)
                print output
                # self.guiLock.acquire()
                # self.serialPortText.configure(bg=dustStyle.COLOR_WARNING_NOTWORKING)
                # self.tipLabel.configure(text=output)
                # self.guiLock.release()
                return
        else:
            raise SystemError

        # if you get here, the connection has succeeded
        self.guiLock.acquire()
        self.SerialCOMLabel.setStyleSheet("background:" + PdStyle.COLOR_NOERROR)
        self.guiLock.release()

        # update the button
        self.guiLock.acquire()
        self.SerialConnect.setText("断开")
        self.SerialConnect.clicked.disconnect(self._connect_serial)
        self.SerialConnect.clicked.connect(self._disconnect_serial)
        self.guiLock.release()

        # common connect routing
        self._connect()

    def _connect_serial_mux(self):
        # initialize the connector
        try:
            if isinstance(self.apiDef, IpMgrDefinition.IpMgrDefinition):
                # self.connector = IpMgrConnectorMux.IpMgrConnectorMux()
                print "no IP Mgr Connector"
            else:
                raise SystemError
        except NotImplementedError as err:
            self.guiLock.acquire()
            # self.tipLabel.configure(text=str(err))
            self._is_not_used(err)
            self.guiLock.release()
            return

        # read connection params from GUI
        self.guiLock.acquire()
        connect_params = {
            'host':     self.XmlIpLineEdit.text().strip(),
            'port': int(self.XmlPortLineEdit.text().strip()),
        }
        self.guiLock.release()
        # connect
        try:
            self.connector.connect(connect_params)
        except ConnectionError as err:
            self.guiLock.acquire()
            # self.serialMuxHostText.configure(bg=dustStyle.COLOR_ERROR)
            # self.serialMuxPortText.configure(bg=dustStyle.COLOR_ERROR)
            # self.tipLabel.configure(text=str(err))
            self._is_not_used(err)
            self.guiLock.release()
            return
        else:
            self.guiLock.acquire()
            # self.serialMuxHostText.configure(bg=dustStyle.COLOR_NOERROR)
            # self.serialMuxPortText.configure(bg=dustStyle.COLOR_NOERROR)
            # self.tipLabel.configure(text="Connection successful.")
            self.guiLock.release()
        # hide other connectFrames
        self.guiLock.acquire()
        # self.serialFrame.grid_forget()
        # self.xmlFrame.grid_forget()
        self.guiLock.release()
        # update the button
        self.guiLock.acquire()
        # self.serialMuxButton.configure(text='disconnect', command=self._disconnect_xml)
        self.guiLock.release()
        # common connect routing
        self._connect()

    def _connect_xml(self):
        # initialize the connector
        try:
            if isinstance(self.apiDef, HartMgrDefinition.HartMgrDefinition):
                self.connector = HartMgrConnector.HartMgrConnector()
            else:
                raise SystemError
        except NotImplementedError as err:
            self.guiLock.acquire()
            # self.tipLabel.configure(text=str(err))
            self._is_not_used(err)
            self.guiLock.release()
            return
        print("connector initialized")
        print(self.connector)
        # read connection params from GUI
        self.guiLock.acquire()
        connect_params = {
            'host':     self.XmlIpLineEdit.text().strip(),
            'port': int(self.XmlPortLineEdit.text().strip()),
        }
        self.guiLock.release()
        print("params accepted")
        print(connect_params)
        # connect
        try:
            self.connector.connect(connect_params)
        except ConnectionError as err:
            self.guiLock.acquire()
            print str(err)
            self.XmlIpLineEdit.setStyleSheet("background:" + PdStyle.COLOR_ERROR)
            self.XmlPortLineEdit.setStyleSheet("background:" + PdStyle.COLOR_ERROR)
            self.guiLock.release()
            return
        else:
            self.guiLock.acquire()
            self.XmlIpLineEdit.setStyleSheet("background:" + PdStyle.COLOR_NOERROR)
            self.XmlPortLineEdit.setStyleSheet("background:" + PdStyle.COLOR_NOERROR)
            self.guiLock.release()
        # update the button
        self.guiLock.acquire()
        self.XmlConnect.clicked.disconnect(self._connect_xml)
        self.XmlConnect.clicked.connect(self._disconnect_xml)
        self.XmlConnect.setText("断开")
        self.guiLock.release()
        # common connect routine
        self._connect()

    def _connect(self):
        # connect the connector to the device
        self.connect_cb(self.connector)

    def _disconnect_xml(self):
        # disconnect the connector from  the device
        self.connector.disconnect()
        # update the xml connector frame
        self.guiLock.acquire()
        self.XmlConnect.clicked.connect(self._connect_xml)
        self.XmlConnect.clicked.disconnect(self._disconnect_xml)
        self.XmlConnect.setText("连接")
        self.XmlIpLineEdit.setStyleSheet("background:" + PdStyle.COLOR_BG)
        self.XmlPortLineEdit.setStyleSheet("background:" + PdStyle.COLOR_BG)
        self.guiLock.release()
        self.disconnect_cb()

    def _disconnect_serial(self):
        # disconnect the connector from  the device
        self.connector.disconnect()
        # update the serial connector frame
        self.guiLock.acquire()
        self.SerialConnect.clicked.connect(self._connect_serial)
        self.SerialConnect.clicked.disconnect(self._disconnect_serial)
        self.SerialConnect.setText("连接")
        self.SerialCOMLabel.setStyleSheet("background:" + PdStyle.COLOR_BG)
        self.guiLock.release()
        self.disconnect_cb()

    def _is_not_used(self, argv):
        pass

# ============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application


class ExampleApp(object):
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.mainWindow = QtWidgets.QMainWindow()
        self.mainWindow.setFixedSize(400, 300)
        self.centralWidget = QtWidgets.QWidget(self.mainWindow)
        self.centralWidget.setGeometry(QtCore.QRect(0, 0, 400, 300))
        self.centralLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.guiLock = threading.Lock()
        self.ConnectFrame = WidgetWiHaConnect(self.guiLock, self._connect_cb, self._disconnect_cb)
        self.centralLayout.addWidget(self.ConnectFrame.TopLayoutWidget)

        # test mote connection
        self.api_def = HartMoteDefinition.HartMoteDefinition()

        # test manager connection
        # self.api_def = HartMgrDefinition.HartMgrDefinition()

        self.ConnectFrame.api_loaded(self.api_def)
        self.mainWindow.show()

        sys.exit(self.app.exec_())

    def _close_cb(self):
        self._close_cb()
        print " _closeCb called"

    def _connect_cb(self, params):
        self._is_not_used()
        print " _connectCb called with param="+str(params)

    def _disconnect_cb(self):
        self._is_not_used()
        print "_disconnect called"

    def _is_not_used(self):
        pass


if __name__ == "__main__":
    ExampleApp()
# End of pdConnection
