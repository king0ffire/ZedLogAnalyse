from PyQt6 import QtGui,QtWidgets
from util import helper,enumtypes,filemanger
import logging
import os

logger=logging.getLogger(__name__)

class ResultHandler:
    def __init__(self, view:QtWidgets.QAbstractItemView):
        self._data:dict[str,dict[str,list[str]]]={}
        self.model = QtGui.QStandardItemModel(view)
        view.setModel(self.model)
        self.rootItem = self.model.invisibleRootItem()
        
    
    def refresh_data(self) -> None:
        self.model.clear()
        for key,value in self._data.items():
            filerow=QtGui.QStandardItem(key)
            for k,v in value.items():
                filerow.appendRow(QtGui.QStandardItem(f"{k}"))
            self.model.appendRow(filerow)
            logger.debug(f"Added {key} to result with value {value}")
        