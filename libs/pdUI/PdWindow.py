#!/usr/bin/python

# ============================ adjust path =====================================
import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from SmartMeshSDK import sdk_version
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))
# ============================ body ============================================


class PdWindow(QtWidgets.QMainWindow):
    # possible locations of icon
    PDICON = [
        '../../pdUI/pd.ico',  # if running from src/
        'pdUI/pd.ico',        # if running from win/
        'pd.ico',               # if running from dustUI/
    ]

    def __init__(self, app_name, close_cb, size):
        # init parent
        super(PdWindow, self).__init__()
        # record variables
        self.closeCb = close_cb

        # icon displayed in the upper-left
        for icon in self.PDICON:
            try:
                self.iconbitmap(default=icon)
            except Exception as err:
                pass  # works on Windows only
            else:
                break
        
        # name of the window. unichr(169) is the copyright sign
        self.setWindowTitle(app_name+' '+unichr(169)+'GEIRI_CPS')
        
        # the window cannot be resized
        self.setFixedSize(size[0], size[1])
        
        # status bar with version
        version_string = '.'.join([str(i) for i in sdk_version.VERSION])
        self.StatusBar = QtWidgets.QStatusBar()
        self.setStatusBar(self.StatusBar)
        self.versionLabel = QtWidgets.QLabel(self.StatusBar)
        self.versionLabel.setText(version_string)
    # ======================== public ==========================================
    
    # ======================== private =========================================
    
    def _release_and_quit(self):
        pass

# ============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application


class ExampleApp(object):
    def __init__(self):
            self.app = QtWidgets.QApplication(sys.argv)
            size = [600, 300]
            window = PdWindow("Partial Discharge Monitor System", self._close_cb, size)
            window.show()
            sys.exit(self.app.exec_())
    
    def _close_cb(self):
        self._is_not_used()
        print ("_closeCb called")

    def _is_not_used(self):
        pass


if __name__ == '__main__':
    ExampleApp()
