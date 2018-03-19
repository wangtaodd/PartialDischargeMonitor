import csv


def checkHeader(fileName, Header):
    with open(fileName,'a') as csvFile:
        pass
    with open(fileName,'r') as csvFile:
        firstLine = csvFile.readline().rstrip('\r\n').split(',')
    if firstLine != Header:
        with open(fileName,'w') as csvFile:
            writer = csv.DictWriter(csvFile, fieldnames=Header)
            writer.writeheader()

