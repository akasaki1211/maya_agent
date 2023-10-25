from maya import OpenMayaUI
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

def maya_main_window():
    main_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)

def information(parent, title, message):
    QtWidgets.QMessageBox.information(parent, title, message)

def confirm(parent, title, message):
    dialog = CofirmDialog(parent, title, message)
    result = dialog.exec_()

    if result == 1:
        return 1, None
    elif result == 0:
        return 0, None
    elif result == 2:
        return 2, dialog.text_content

class CofirmDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, title="", message=""):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.resize(400, 100)

        self.label = QtWidgets.QLabel(message, self)

        self.btn_continue = QtWidgets.QPushButton('Continue', self)
        self.btn_continue.clicked.connect(self.on_continue_clicked)

        self.btn_interrupt = QtWidgets.QPushButton('Interrupt', self)
        self.btn_interrupt.clicked.connect(self.on_interrupt_clicked)

        self.textbox = QtWidgets.QLineEdit(self)

        self.btn_send = QtWidgets.QPushButton('Send', self)
        self.btn_send.clicked.connect(self.on_send_clicked)

        h_layout_1 = QtWidgets.QHBoxLayout()
        h_layout_1.addWidget(self.btn_continue)
        h_layout_1.addWidget(self.btn_interrupt)

        h_layout_2 = QtWidgets.QHBoxLayout()
        h_layout_2.addWidget(self.textbox)
        h_layout_2.addWidget(self.btn_send)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addLayout(h_layout_1)
        layout.addLayout(h_layout_2)

    def on_continue_clicked(self):
        self.done(1)

    def on_interrupt_clicked(self):
        self.done(0)

    def on_send_clicked(self):
        self.text_content = self.textbox.text()
        self.done(2)