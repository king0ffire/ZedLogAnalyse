import tarfile
from PyQt6 import QtWidgets, QtCore, QtGui
from core.analyzer import Analyzer
from core.viewmodel import ResultHandler
import logging
from util import helper, enumtypes
from core.uploader import FileUploader
import os
from typing import Any

logger = logging.getLogger(__name__)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow: QtWidgets.QMainWindow):
        self.MainWindow = MainWindow
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(4)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.plainTextEdit.sizePolicy().hasHeightForWidth()
        )
        self.plainTextEdit.setSizePolicy(sizePolicy)
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout.addWidget(self.plainTextEdit, 0, 1, 1, 1)
        self.treeView = QtWidgets.QTreeView(parent=self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeView.sizePolicy().hasHeightForWidth())
        self.treeView.setSizePolicy(sizePolicy)
        self.treeView.setObjectName("treeView")
        self.gridLayout.addWidget(self.treeView, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(parent=self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionImport = QtGui.QAction(parent=MainWindow)
        self.actionImport.setObjectName("actionImport")
        self.menu.addAction(self.actionImport)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # self.treeView.setAcceptDrops(True)
        self.MainWindow.setAcceptDrops(True)
        # self.plainTextEdit.setAcceptDrops(True)
        # self.plainTextEdit.dropEvent=self.dropEvent
        # self.plainTextEdit.dragEnterEvent=self.dragEnterEvent
        # self.treeView.dropEvent=self.dropEvent
        # self.treeView.dragEnterEvent=self.dragEnterEvent
        self.MainWindow.dropEvent = self.dropEvent
        self.MainWindow.dragEnterEvent = self.dragEnterEvent

        self._file_uploader = FileUploader(self.MainWindow)
        self._file_analyzer = Analyzer()
        self._file_customable_location_in_gz = (
            ("log/snapshot/reboot.log", enumtypes.AnalyzerType.Analyze),
            (
                "logs/keylog.tgz",
                (
                    (
                        "keylog/keylog.txt", enumtypes.AnalyzerType.Analyze
                    ),
                ),
            ),
            # (["log/.tar.bz2"],enumtypes.AnalyzerType.DisplayOnly),
            (
                "log/*.tar.bz2",
                (
                    (
                        "*var_*",
                        (

                            ("var/log/syslog", enumtypes.AnalyzerType.Analyze),
                            ("var/log/trace/dbglog", enumtypes.AnalyzerType.Analyze),
                        ),
                    ),
                    (
                        "*core-*", enumtypes.AnalyzerType.DisplayOnly
                    ),
                ),
            ),
        )
        self._view_model = ResultHandler(self.treeView)
        self.actionImport.triggered.connect(self.import_file)
        self.treeView.clicked.connect(self.tree_clicked)
        self.plainTextEdit.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)

    def tree_clicked(self, index: QtCore.QModelIndex):
        data = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
        logger.debug(f"clicked on {data}")
        parent_list=self.parent_list(index)
        parent_list.reverse()
        logger.debug(f"parent_list: {parent_list+[data]}")
        filedata=self._view_model.getByKeySequence(parent_list+[data])
        if isinstance(filedata,list):
            self.plainTextEdit.setPlainText("\n".join(filedata))

    def parent_list(self, index: QtCore.QModelIndex) -> list[str]:
        parent_list = []
        parent=index.parent()
        while parent.isValid():
            parent_list.append(parent.data(QtCore.Qt.ItemDataRole.DisplayRole))
            parent=parent.parent()
        return parent_list
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(
            _translate("MainWindow", "ZedLog Analyzer  V0.2.1 (100 lines)")
        )
        self.menu.setTitle(_translate("MainWindow", "文件"))
        self.actionImport.setText(_translate("MainWindow", "Import"))

    def import_file(self, _):
        self._file_uploader.uploadfile(self.open_file)

    def dragEnterEvent(self, a0: QtGui.QDragEnterEvent | None):
        if a0.mimeData().hasUrls():
            a0.acceptProposedAction()
        else:
            a0.ignore()

    def dropEvent(self, a0: QtGui.QDropEvent | None):
        # self.MainWindow.dropEvent(a0)
        logger.info("drop event")
        self._file_uploader.dropEvent(a0, self.open_file)

    def open_file(self, fullpath: str):
        root, ext = helper.split_filename(fullpath)
        self._file_original_full_path = fullpath
        if ext.endswith("gz"):
            roottar = tarfile.open(fullpath, "r:gz")
        elif ext.endswith("bz2"):
            roottar = tarfile.open(fullpath, "r:bz2")
        else:
            logger.error("The file is not gzipped")
            return
        try:
            self._view_model._data[fullpath] = {}
            self._file_analyzer.recursive_analyze(
                roottar,
                self._file_customable_location_in_gz,
                self._view_model._data[fullpath],
            )
            logger.debug(f"current data: {self._view_model._data}")
        except AttributeError as e:
            logger.error(
                f"The file is considered as a gz file, but we failed to read it.\nThe exception message is: {e}"
            )
            critical_box = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Warning,
                "warning",
                f"The file is considered as a gz file, but we failed to read it.\nThe exception message is: {e}",
            )
            critical_box.exec()
            return
        except Exception as e:
            logger.error(
                f"The file is considered as a gz file, but we failed to load it.\nThe exception message is: {e}"
            )
            critical_box = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Warning,
                "warning",
                f"The file is considered as a gz file, but we failed to load it.\nThe exception message is: {e}",
            )
            critical_box.exec()
            raise e
        finally:
            roottar.close()

        self._view_model.refresh_data()
        logger.info(f"file is open")
