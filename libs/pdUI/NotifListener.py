# -*- coding: utf-8 -*-
import threading
from SmartMeshSDK.ApiException import CommandError, \
                                      ConnectionError, \
                                      APIError,\
                                      QueueError


class NotifListener(threading.Thread):
    def __init__(self, connector, notif_cb, disconnected_cb):

        # record variables
        self.connector = connector
        self.notifCb = notif_cb
        self.disconnectedCb = disconnected_cb

        # init the parent
        threading.Thread.__init__(self)
        self.name = "NotifListener"
        self.daemon = True

    # ======================== public ==========================================
    def run(self):
        keep_listening = True
        while keep_listening:
            try:
                input = self.connector.getNotificationInternal(-1)
            except (ConnectionError, QueueError) as err:
                print(err)
                keep_listening = False
            else:
                if input:
                    self.notifCb(input)
                else:
                    keep_listening = False
        self.disconnectedCb()
