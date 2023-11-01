from maya import OpenMayaUI
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance

TIMEOUT = 10

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

        # add widget
        self.label = QtWidgets.QLabel(message, self)

        self.timeout = TIMEOUT
        self.count_label = QtWidgets.QLabel(str(self.timeout))
        self.count_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.btn_continue = QtWidgets.QPushButton('Continue', self)
        self.btn_continue.clicked.connect(self.on_continue_clicked)

        self.btn_interrupt = QtWidgets.QPushButton('Interrupt', self)
        self.btn_interrupt.clicked.connect(self.on_interrupt_clicked)

        self.textbox = QtWidgets.QLineEdit(self)
        self.textbox.textChanged.connect(self.stop_countdown)

        self.btn_send = QtWidgets.QPushButton('Send', self)
        self.btn_send.clicked.connect(self.on_send_clicked)

        # set timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

        # layout
        h_layout_1 = QtWidgets.QHBoxLayout()
        h_layout_1.addWidget(self.btn_continue)
        h_layout_1.addWidget(self.btn_interrupt)

        h_layout_2 = QtWidgets.QHBoxLayout()
        h_layout_2.addWidget(self.textbox)
        h_layout_2.addWidget(self.btn_send)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.count_label)
        layout.addLayout(h_layout_1)
        layout.addLayout(h_layout_2)

    def update_countdown(self):
        if self.timeout > 0:
            self.count_label.setText(str(self.timeout))
            self.timeout -= 1
        else:
            self.done(1)

    def stop_countdown(self):
        self.timer.stop()
        self.count_label.setText('---')

    def on_continue_clicked(self):
        self.done(1)

    def on_interrupt_clicked(self):
        self.done(0)

    def on_send_clicked(self):
        self.text_content = self.textbox.text()
        self.done(2)