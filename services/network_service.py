from PyQt5.QtCore import QObject, pyqtSignal, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import os

class NetworkService(QObject):
    download_complete = pyqtSignal(bytes)
    download_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.nam = QNetworkAccessManager()
        self.temp_dir = os.path.join(os.path.expanduser('~'), '.cache', 'pyqt5-app')
        
    def download_image(self, url):
        request = QNetworkRequest(QUrl(url))
        reply = self.nam.get(request)
        reply.finished.connect(lambda: self._handle_response(reply))

    def _handle_response(self, reply):
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll().data()
            try:
                os.makedirs(self.temp_dir, exist_ok=True)
                temp_path = os.path.join(self.temp_dir, 'temp_image')
                with open(temp_path, 'wb') as f:
                    f.write(data)
                self.download_complete.emit(data)
            except Exception as e:
                self.download_failed.emit(f"文件保存失败: {str(e)}")
        else:
            self.download_failed.emit(reply.errorString())