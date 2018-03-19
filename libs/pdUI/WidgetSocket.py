# -*- coding: utf-8 -*-
import sys
import socket
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget
from isIP import isIP, isPort
import errno


class WidgetSocket(object):
    def __init__(self):
        # initial socket frame
        self.TopWidget = QWidget()
        self.TopWidget.setFixedSize(380, 200)
        self.SocketLayout = QtWidgets.QVBoxLayout(self.TopWidget)
        self.SocketLabel = QtWidgets.QLabel("Socket",self.TopWidget )
        self.SocketLabel.setGeometry(100, 20, 20, 30)
        # self.SocketLayout.addWidget(self.SocketLabel)

        self.SocketConnect = QtWidgets.QWidget()
        self.SocketLayout.addWidget(self.SocketConnect)
        self.SocketConnectLayout = QtWidgets.QHBoxLayout(self.SocketConnect)
        self.SocketHostLabel = QtWidgets.QLabel("Host:")
        self.SocketHostLineEdit = QtWidgets.QLineEdit("192.168.1.102")
        self.SocketPortLabel = QtWidgets.QLabel("Port:")
        self.SocketPortLineEdit = QtWidgets.QLineEdit("8899")
        self.SocketConnectButton = QtWidgets.QPushButton("连接")
        self.SocketConnectButton.clicked.connect(self.socket_connect)
        self.SocketConnectLayout.addWidget(self.SocketHostLabel)
        self.SocketConnectLayout.addWidget(self.SocketHostLineEdit)
        self.SocketConnectLayout.addWidget(self.SocketPortLabel)
        self.SocketConnectLayout.addWidget(self.SocketPortLineEdit)
        self.SocketConnectLayout.addWidget(self.SocketConnectButton)

        self.SocketText = QtWidgets.QLineEdit("text to send via socket")
        self.SocketText.setFixedSize(360, 80)
        self.SocketSendButton = QtWidgets.QPushButton("发送")
        self.SocketSendButton.clicked.connect(self.socket_send_test)
        self.SocketLayout.addWidget(self.SocketText)
        self.SocketLayout.addWidget(self.SocketSendButton)

        self.socket = None

    def socket_connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = self.SocketHostLineEdit.text()
        port = self.SocketPortLineEdit.text()
        # 建立连接:
        if isIP(host) and isPort(port):
            try:
                self.socket.connect((host, int(port)))
            except socket.error, v:
                errorcode = v[0]
                print errorcode
        else:
            print ('host ip(or port) is invalid')

    def socket_send_test(self):
        for data in ['Michael', 'Tracy', 'Sarah']:
            # 发送数据:
            self.socket.send(data)
            print self.socket.recv(1024)
        self.socket.send('exit')
        self.socket.close()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = QtWidgets.QMainWindow()
    mainWindow.setFixedSize(400, 600)
    centralWidget = QtWidgets.QWidget(mainWindow)
    centralWidget.setFixedSize(380, 600)
    layout = QtWidgets.QHBoxLayout(centralWidget)
    socket_widget = WidgetSocket()
    layout.addWidget(socket_widget.TopWidget)
    mainWindow.show()
    sys.exit(app.exec_())
