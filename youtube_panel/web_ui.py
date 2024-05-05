from PySide2 import QtWidgets, QtWebEngineWidgets
from .conf import Const


class WebUI(QtWidgets.QWidget):
    YOUTUBE_URL = Const.YOUTUBE_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setGeometry(500, 300, 250, 110)
        self.setWindowTitle('Web Demo')
        hbox = QtWidgets.QHBoxLayout()
        self.webview = QtWebEngineWidgets.QWebEngineView()
        self.webview.setUrl(self.YOUTUBE_URL)
        hbox.addWidget(self.webview)
        self.setLayout(hbox)

    def get_url(self) -> str:
        '''
        webviewのURLを取得する

        Returns:
            str: URL
        '''
        return self.webview.url().toString()
