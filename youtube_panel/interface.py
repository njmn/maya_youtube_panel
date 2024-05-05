from importlib import reload
from PySide2 import QtWidgets
from maya import cmds
from . import function
from . import web_ui

reload(web_ui)
reload(function)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=function.get_maya_main_window()):
        super().__init__(parent)
        self.setMinimumSize(800, 800)
        self.setWindowTitle('Main Window')
        v_box = QtWidgets.QVBoxLayout()
        h_box = QtWidgets.QHBoxLayout()

        self.web_ui = web_ui.WebUI()

        self.input_label = QtWidgets.QLabel('URL:')
        self.input_text = QtWidgets.QLineEdit()

        # buttons
        get_url_button = QtWidgets.QPushButton('Get URL')
        download_button = QtWidgets.QPushButton('Download')
        image_plane_button = QtWidgets.QPushButton('Create Image Plane')
        delete_button = QtWidgets.QPushButton('Delete')

        # connection
        get_url_button.clicked.connect(
            lambda: self.input_text.setText(self.web_ui.get_url())
        )
        download_button.clicked.connect(
            lambda: [
                function.download(self.input_text.text()),
                cmds.confirmDialog(
                    title='Download', message='Download Complete', button=['OK']
                ),
            ]
        )
        image_plane_button.clicked.connect(lambda: function.create_image_plane())
        delete_button.clicked.connect(
            lambda: [
                function.delete_folder(),
                cmds.confirmDialog(
                    title='Delete', message='Delete Complete', button=['OK']
                ),
            ]
        )

        # hbox
        h_box.addWidget(self.input_label)
        h_box.addWidget(self.input_text)
        h_box.addWidget(get_url_button)

        # vbox
        v_box.addWidget(self.web_ui)
        v_box.addLayout(h_box)
        v_box.addWidget(download_button)
        v_box.addWidget(image_plane_button)
        v_box.addWidget(delete_button)

        # central widgetの設定
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(v_box)
        self.setCentralWidget(central_widget)
        self.show()
        self.activateWindow()


def main():
    MainWindow()
