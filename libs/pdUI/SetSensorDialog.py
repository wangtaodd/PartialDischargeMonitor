# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from StaticFunction import clear_layout


class SetSensorDialog(QtWidgets.QWidget):
    def __init__(self, manager):
        super(SetSensorDialog, self).__init__()
        self.num = 0
        self.SensorNr = [0 for i in range(20)]
        self.SensorLocationWidget = [[0 for i in range(22)] for j in range(20)]

        self.label = QtWidgets.QLabel("传感器数量")

        self.HLayout = QtWidgets.QVBoxLayout(self)
        self.TopWidget = QtWidgets.QWidget()
        self.TopWidget.setFixedHeight(40)
        self.DownWidget = QtWidgets.QWidget()
        self.HLayout.addWidget(self.TopWidget)
        self.HLayout.addWidget(self.DownWidget)

        self.layout = QtWidgets.QGridLayout(self.TopWidget)
        self.layout1 = QtWidgets.QGridLayout(self.DownWidget)
        self.layout.addWidget(self.label, 0, 0, 1, 1)
        self.numLine = QtWidgets.QLineEdit("")
        self.layout.addWidget(self.numLine, 0, 1, 1, 1)
        self.numButton = QtWidgets.QPushButton("添加")
        self.numButton.clicked.connect(self.addGrid)
        self.layout.addWidget(self.numButton, 0, 2, 1, 1)
        '''
        self.removeButton = QtWidgets.QPushButton("清空")
        self.removeButton.clicked.connect(self.clearGrid)
        self.layout.addWidget(self.removeButton, 0, 3, 1, 1)
        '''
        self.setWindowTitle("输入传感器坐标")
        self.parent = manager
        sensor_count_recorded, sensor_location = self.parent.dataProcessor.read_sensor_location()
        self.numLine.setText(str(sensor_count_recorded))

    def addGrid(self):
        """
        for i in reversed(range(self.layout1.count())):
            item = self.layout1.itemAt(i)
            item.widget().setParent(None)
            """
        clear_layout(self.layout1)
        self.num = int(self.numLine.text())
        self.NrLabel = QtWidgets.QLabel("编号")
        self.XLabel = QtWidgets.QLabel("x坐标")
        self.YLabel = QtWidgets.QLabel("y坐标")
        self.layout1.addWidget(self.NrLabel, 0, 0, 1, 1)
        self.layout1.addWidget(self.XLabel, 0, 1, 1, 1)
        self.layout1.addWidget(self.YLabel, 0, 2, 1, 1)
        sensor_count_recorded, sensor_location = self.parent.dataProcessor.read_sensor_location()

        for i in range(self.num):
            self.SensorNr[i] = QtWidgets.QLabel(str(i+1))
            self.SensorLocationWidget[i][0] = QtWidgets.QLineEdit()
            self.SensorLocationWidget[i][1] = QtWidgets.QLineEdit()
            self.layout1.addWidget(self.SensorNr[i], i+2, 0, 1, 1)
            self.layout1.addWidget(self.SensorLocationWidget[i][0], i + 2, 1, 1, 1)
            self.layout1.addWidget(self.SensorLocationWidget[i][1], i + 2, 2, 1, 1)

            if i < sensor_count_recorded:
                self.SensorLocationWidget[i][0].setText(str(sensor_location[i][0]))
                self.SensorLocationWidget[i][1].setText(str(sensor_location[i][1]))
        self.saveButton = QtWidgets.QPushButton("确认")
        self.saveButton.clicked.connect(self.save_location)
        self.layout1.addWidget(self.saveButton, self.num+2, 1, 1, 1)
        self.DownWidget.setFixedHeight((self.num+2)*30)
        self.setFixedHeight(60+(self.num+2)*30)

    def save_location(self):
        with open("sensorData.txt", "w") as file:
            file.write(str(self.num)+'\n')
            for i in range(self.num):
                file.write(self.SensorLocationWidget[i][0].text() + ' ' + self.SensorLocationWidget[i][1].text() + '\n')
        self.parent.sensor_counter = self.num
        self.parent.init_sensor_map()
        self.parent.update_table()
