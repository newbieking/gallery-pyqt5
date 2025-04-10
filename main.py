import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFileDialog, QScrollArea, QListWidget, QListWidgetItem, QSplitter, QMenu
from PyQt5.QtCore import Qt, QTimer, QUrl, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply


class MainWindow(QMainWindow):
    class ImageLabel(QLabel):
        def __init__(self, main_window):
            super().__init__()
            self.main_window = main_window

        def contextMenuEvent(self, event):
            menu = QMenu(self)
            save_action = menu.addAction("另存为")
            save_action.triggered.connect(self.main_window.save_image)
            menu.exec_(event.globalPos())

    def save_image(self):
        source_path = getattr(self, 'current_image_path', None) or getattr(self, 'temp_image_path', None)
        if source_path:
            path, _ = QFileDialog.getSaveFileName(self, "保存图片", "", "图片文件 (*.png *.jpg *.jpeg *.bmp)")
            if path:
                try:
                    import shutil
                    shutil.copy2(source_path, path)
                except Exception as e:
                    self.show_error(f"保存失败: {str(e)}")
        else:
            self.show_error("当前没有可保存的图片")

    def __init__(self):
        super().__init__()
        self.nam = QNetworkAccessManager()
        self.initUI()
        self.current_images = []
        self.current_index = 0

    def initUI(self):
        self.setWindowTitle('图片浏览器')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('app_icon.png'))

        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # 操作区域
        control_layout = QHBoxLayout()
        
        self.btn_open_file = QPushButton('打开文件')
        self.btn_open_dir = QPushButton('打开文件夹')
        self.uri_input = QLineEdit()
        self.btn_submit = QPushButton('加载URL')
        
        control_layout.addWidget(self.btn_open_file)
        control_layout.addWidget(self.btn_open_dir)
        control_layout.addWidget(self.uri_input)
        control_layout.addWidget(self.btn_submit)
        
        # 图片展示区域
        self.scroll_area = QScrollArea()
        self.image_label = self.ImageLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)

        main_layout.addLayout(control_layout)
        # 使用水平分割布局
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧图片展示区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addWidget(self.scroll_area)
        
        # 右侧缩略图列表
        self.thumbnail_list = QListWidget()
        self.thumbnail_list.setViewMode(QListWidget.ListMode)
        self.thumbnail_list.setFlow(QListWidget.TopToBottom)
        self.thumbnail_list.setSpacing(10)
        self.thumbnail_list.setIconSize(QSize(100, 100))
        self.thumbnail_list.setFixedWidth(120)  # 设置固定宽度匹配侧边栏
        self.thumbnail_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.thumbnail_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.thumbnail_list.setUniformItemSizes(True)
        self.thumbnail_list.setWrapping(False)
        self.thumbnail_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.thumbnail_list.setResizeMode(QListWidget.Adjust)
        self.thumbnail_list.itemClicked.connect(self.on_thumbnail_clicked)
        
        splitter.addWidget(self.thumbnail_list)
        splitter.addWidget(left_widget)
        # splitter.setSizes([1, 10])  # 调整为1:4的比例分配初始空间
        splitter.splitterMoved.connect(self.handle_splitter_moved)
        splitter.setStretchFactor(0, 1)  # 设置分割器区域伸缩比例为1:4
        splitter.setStretchFactor(1, 8)  # 设置分割器区域伸缩比例为1:4
        
        main_layout.addWidget(splitter)
        main_layout.setStretch(1, 4)  # 设置分割器区域伸缩比例为1:4

        # 样式设置
        self.apply_styles()
        
        # 事件绑定
        self.btn_open_file.clicked.connect(self.open_file)
        self.btn_open_dir.clicked.connect(self.open_directory)
        self.btn_submit.clicked.connect(self.load_from_url)

        # 导航控件
        self.nav_widget = QWidget()
        nav_layout = QHBoxLayout(self.nav_widget)
        self.btn_prev = QPushButton('◀')
        self.btn_next = QPushButton('▶')
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.btn_next)
        main_layout.addWidget(self.nav_widget)

        # 错误提示框
        self.error_label = QLabel()
        self.error_label.setFixedHeight(30)
        self.error_label.hide()
        main_layout.addWidget(self.error_label)
        
        # 导航按钮事件绑定
        self.btn_prev.clicked.connect(self.show_previous_image)
        self.btn_next.clicked.connect(self.show_next_image)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #ADD8E6;
                color: white;
                border-radius: 5px;
                padding: 8px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #007BFF;
            }
            QLineEdit {
                border: 1px solid #D3D3D3;
                border-radius: 3px;
                padding: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #007BFF;
            }
            QListWidget::item {
                margin: 5px 0;
                padding: 2px;
                width: 100%;
            }
            QListWidget {
                background: white;
                border-right: 1px solid #D3D3D3;
            }
            QScrollBar:vertical {
                width: 12px;
            }
            """
        )

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "图片文件 (*.png *.jpg *.jpeg *.gif *.bmp)")
        if file_path:
            dir_path = os.path.dirname(file_path)
            self.current_dir = dir_path
            self.current_images = [f for f in os.listdir(dir_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            self.current_index = self.current_images.index(os.path.basename(file_path))
            self.thumbnail_list.clear()
            
            for idx, filename in enumerate(self.current_images):
                full_path = os.path.join(dir_path, filename)
                pixmap = QPixmap(full_path)
                if not pixmap.isNull():
                    thumbnail = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    item = QListWidgetItem(QIcon(thumbnail), '')
                    item.setData(Qt.UserRole, idx)
                    self.thumbnail_list.addItem(item)
            self.show_image(file_path)

    def open_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择图片文件夹")
        if dir_path:
            self.current_dir = dir_path
            self.current_images = [f for f in os.listdir(dir_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            self.current_index = 0
            self.thumbnail_list.clear()
            
            # 生成缩略图
            for idx, filename in enumerate(self.current_images):
                full_path = os.path.join(dir_path, filename)
                pixmap = QPixmap(full_path)
                if not pixmap.isNull():
                    thumbnail = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    item = QListWidgetItem(QIcon(thumbnail), '')
                    item.setData(Qt.UserRole, idx)  # 存储索引
                    self.thumbnail_list.addItem(item)
            
            if self.current_images:
                self.show_image(os.path.join(dir_path, self.current_images[0]))

    def on_thumbnail_clicked(self, item):
        clicked_index = item.data(Qt.UserRole)
        self.current_index = clicked_index
        self.show_image(os.path.join(self.current_dir, self.current_images[self.current_index]))

    def show_previous_image(self):
        if hasattr(self, 'current_dir') and self.current_index > 0:
            self.current_index -= 1
            self.show_image(os.path.join(self.current_dir, self.current_images[self.current_index]))

    def show_next_image(self):
        if hasattr(self, 'current_dir') and self.current_index < len(self.current_images) - 1:
            self.current_index += 1
            self.show_image(os.path.join(self.current_dir, self.current_images[self.current_index]))

    def handle_splitter_moved(self):
        self.update_image_scale()

    def show_image(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self.current_image_path = path
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            # 同步选中状态
            self.thumbnail_list.setCurrentRow(self.current_index)
        else:
            self.show_error("无法加载图片")
        self.update_image_scale()

    def update_image_scale(self):
        if hasattr(self, 'current_image_path'):
            pixmap = QPixmap(self.current_image_path)
            if pixmap.isNull():
                self.show_error("无法加载图片文件")
                return
            self.image_label.setPixmap(pixmap.scaled(self.scroll_area.size(),
                                                   Qt.KeepAspectRatio,
                                                   Qt.SmoothTransformation))
        else:
            self.show_error("当前没有可显示的图片")

    def show_image_from_data(self, data):
        pixmap = QPixmap()
        if pixmap.loadFromData(data):
            self.current_image_path = None
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.update_image_scale()
        else:
            self.show_error("无法解析图片数据")

    def show_error(self, message):
        self.error_label.setText(f"<span style='color:red;'>{message}</span>")
        self.error_label.show()
        QTimer.singleShot(3000, self.error_label.hide)

    def wheelEvent(self, event):
        if self.image_label.pixmap():
            delta = event.angleDelta().y()
            self.image_label.resize(self.image_label.width() + delta, self.image_label.height() + delta)

    def resizeEvent(self, event):
        self.update_image_scale()
        super().resizeEvent(event)

    def load_from_url(self):
        url = self.uri_input.text()
        if url:
            self.thumbnail_list.clear()
            self.current_images = [url]
            self.current_index = 0
            
            # 创建临时文件保存路径
            temp_dir = os.path.join(os.path.expanduser('~'), '.cache', 'pyqt5-app')
            os.makedirs(temp_dir, exist_ok=True)
            self.temp_image_path = os.path.join(temp_dir, 'temp_image')
            
            # 发起网络请求
            reply = self.nam.get(QNetworkRequest(QUrl(url)))
            reply.finished.connect(lambda: self.handle_url_reply(reply))
            
    def handle_url_reply(self, reply):
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            # 保存到临时文件
            try:
                with open(self.temp_image_path, 'wb') as f:
                    f.write(data.data())
            except Exception as e:
                self.show_error(f"临时文件保存失败: {str(e)}")
                return
            
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            if not pixmap.isNull():
                # 生成并添加缩略图
                thumbnail = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                item = QListWidgetItem(QIcon(thumbnail), '')
                item.setData(Qt.UserRole, 0)
                self.thumbnail_list.addItem(item)
                self.show_image_from_data(data)
        else:
            self.show_error(f"加载失败: {reply.errorString()}")

# 删除类定义后的错误事件绑定代码
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())