# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
def clear_layout(layout):
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)
        if isinstance(item, QtWidgets.QSpacerItem):
            layout.removeItem(item)
        if isinstance(item, QtWidgets.QWidgetItem):
            item.widget().setParent(None)

