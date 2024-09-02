from PyQt6 import QtWidgets, QtCore, QtGui
import util.helper as helper
import util.filemanger as filemanger
import logging
import util.enumtypes as enumtypes
from typing import Callable,cast
logger = logging.getLogger(__name__)

class FileUploader(QtCore.QObject):
    def __init__(self, parent: QtWidgets.QWidget|None=None):
        super().__init__(parent)
    
        
    def dropEvent(self, e: QtGui.QDropEvent|None, _open_file: Callable[[str],None]):
        logger.info(f"detect a drop event")
        for url in e.mimeData().urls():
            logger.debug(f"received file: {url.toLocalFile()}")
            if url.isLocalFile():
                path = url.toLocalFile()
                _open_file(path)


    def uploadfile(self,_open_file: Callable[[str],None]):
        logger.info(f"open a dialog to read files")
        file_path_list, selectedFilter = QtWidgets.QFileDialog.getOpenFileNames(
            self.parent(), "Open tgz", "", "All Files (*);;GZip Files (*.gz *.tgz)"
        )
        if file_path_list[0] == "":
            return
        for file_path in file_path_list:    
            _open_file(file_path)


    