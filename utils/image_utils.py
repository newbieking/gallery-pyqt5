import os
import shutil
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

def save_image_to_disk(source_path, parent_widget):
    path, _ = QFileDialog.getSaveFileName(parent_widget, "保存图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp)")
    if path:
        try:
            shutil.copy2(source_path, path)
            return True
        except Exception as e:
            parent_widget.show_error(f"保存失败: {str(e)}")
            return False

def generate_thumbnail(file_path, size=100):
    pixmap = QPixmap(file_path)
    if not pixmap.isNull():
        return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    return None