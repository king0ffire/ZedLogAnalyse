from PyQt6 import QtGui,QtWidgets
from util import helper,enumtypes,filemanger
import logging
import os
from typing import Any

logger=logging.getLogger(__name__)

class ResultHandler:
    def __init__(self, view:QtWidgets.QAbstractItemView):
        self._data:dict[str,Any]={}
        self.model = QtGui.QStandardItemModel(view)
        view.setModel(self.model)
        self.rootItem = self.model.invisibleRootItem()
        
    
    def refresh_data(self) -> None:
        self.model.clear()
        root=self.rootItem
        for filename,value in self._data.items():
            filerow=QtGui.QStandardItem(filename)
            self.refresh_data_recursive(filerow,self._data[filename])
            self.model.appendRow(filerow)
        #logger.debug(f"Added {filename} to result with value {value}")
        
    def refresh_data_recursive(self,current_root:QtGui.QStandardItem,current_dict:dict[str,Any]) ->  None:
        for task_target, tasks in current_dict.items():
            current_item = QtGui.QStandardItem(task_target)
            if tasks is None:
                current_root.appendRow(current_item)
            elif isinstance(tasks,list):
                current_root.appendRow(current_item) #点击怎么实现？
            elif isinstance(tasks,dict):
                self.refresh_data_recursive(current_item,tasks)
                current_root.appendRow(current_item)
            
    def getByKeySequence(self,keys:list[str]) -> Any:
        res=self._data
        for key in keys:
            res=res[key]
        return res