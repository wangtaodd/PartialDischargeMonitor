def isIP(ipInput):
    isIPFlag = True
    ipList = ipInput.split('.')
    if len(ipList) == 4:
        for x in ipList:
            isIPFlag = x.isdigit() and isIPFlag
        if isIPFlag:
            for x in ipList:
                isIPFlag = isIPFlag and (0<=int(x)<=255)
    else:
        isIPFlag = False
    return isIPFlag


def isPort(portInput):
    isPortFlag = False
    if portInput.isdigit():
        if(0<=int(portInput)<=65535):
            isPortFlag = True
    return isPortFlag