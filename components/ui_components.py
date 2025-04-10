from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QLabel, QMenu
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap

class ThumbnailList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setViewMode(QListWidget.ListMode)
        self.setFlow(QListWidget.TopToBottom)
        self.setSpacing(10)
        self.setIconSize(QSize(100, 100))
        self.setFixedWidth(120)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

class ImageLabel(QLabel):
    def __init__(self, save_handler):
        super().__init__()
        self.save_handler = save_handler

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        save_action = menu.addAction("另存为")
        save_action.triggered.connect(self.save_handler)
        menu.exec_(event.globalPos())