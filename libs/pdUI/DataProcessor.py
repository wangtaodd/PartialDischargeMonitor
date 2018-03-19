# -*- coding: utf-8 -*-
from Sensor import Sensor
import csv
import time
from csvHeaderCheck import checkHeader

class DataProcessor:
    def __init__(self):
        pass

    def save_data_by_sensor(self,  data):
        fileName = data['mac']+"-"+time.strftime('%Y-%m-%d-%H', time.localtime(time.time()))+'.csv'
        checkHeader(fileName, data.keys())
        with open(fileName, 'a') as csvFile:
            fieldnames = data.keys()
            writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
            writer.writerow(data)

    # open file and read Sensor location data
    def read_sensor_location(self):
        with open("sensorData.txt", 'r') as fp:
            sensor_counter = int(fp.readline())
            location = []
            for i in range(sensor_counter):
                location.append(fp.readline().split())
                location[i] = [float(x) for x in location[i]]
        return sensor_counter, location

    def getPdLocation(self, data):
        # this is the place to calculate Partial Discharge Location
        # output format [[x1,y1],[x2,y2],...]
        pdLocation = [[2.5, 1.5]]
        return pdLocation

    def _is_not_used(self):
        pass


dataProcessor = DataProcessor()
data = {'mac':'0xyf','payload':'122365','MoteId':'1'}
dataProcessor.save_data_by_sensor(data)