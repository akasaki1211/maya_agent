from pathlib import Path
#import json

from maya import cmds, OpenMayaUI
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance

from .vectorstore import VectorStore
from .functions import FunctionSet
from .agent import Agent
from .openai_utils import CHAT_MODELS, DEFAULT_CHAT_MODEL

def maya_main_window():
    main_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)

class UI(QtWidgets.QMainWindow):
    
    def __init__(self, vectorstore_path:Path, parent=None):
        super(UI, self).__init__(parent)

        # VectorStore読み込み
        manual_vs = VectorStore(vectorstore_path)

        # 関数セットのインスタンスを作成
        self.function_set = FunctionSet(manual_vs=manual_vs)

        # エージェントのインスタンスを作成
        self.agent = Agent(function_set=self.function_set)

        # 初期の空メッセージリスト
        self.messages = []

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(u'Rig Support Agent')
        self.setGeometry(400, 400, 400, 500)
        self.statusBar().showMessage("Ready.")

        # Model
        self.chat_model_cbx = QtWidgets.QComboBox()
        self.chat_model_cbx.addItems(CHAT_MODELS)
        self.chat_model_cbx.setCurrentText(DEFAULT_CHAT_MODEL)

        # Max Call
        maxcall_label = QtWidgets.QLabel("Max Call:")
        maxcall_label.setAlignment(QtCore.Qt.AlignRight)
        self.maxcall_spinbox = QtWidgets.QSpinBox()
        self.maxcall_spinbox.setMinimum(1)
        self.maxcall_spinbox.setValue(20)

        # temperature
        temperature_label = QtWidgets.QLabel("temperature:")
        temperature_label.setAlignment(QtCore.Qt.AlignRight)
        self.temperature_spinbox = QtWidgets.QDoubleSpinBox()
        self.temperature_spinbox.setRange(0.0, 2.0)
        self.temperature_spinbox.setValue(0.0)
        self.temperature_spinbox.setSingleStep(0.1)

        # top_p
        top_p_label = QtWidgets.QLabel("top_p:")
        top_p_label.setAlignment(QtCore.Qt.AlignRight)
        self.top_p_spinbox = QtWidgets.QDoubleSpinBox()
        self.top_p_spinbox.setRange(0.0, 2.0)
        self.top_p_spinbox.setValue(1.0)
        self.top_p_spinbox.setSingleStep(0.1)

        # Agentの回答を表示するテキストエリアの設定
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("QTextEdit {font-size: 15px; background-color: #333333;}")

        # ユーザー入力欄の設定
        self.user_input = QtWidgets.QPlainTextEdit()
        self.user_input.setPlaceholderText("Enter text...")
        self.user_input.setMaximumHeight(100)
        self.user_input.setStyleSheet("QPlainTextEdit {font-size: 15px; background-color: #262626;}")

        self.ask_button = QtWidgets.QPushButton('Send')
        self.ask_button.clicked.connect(self.ask)

        # レイアウト
        options_layout_01 = QtWidgets.QHBoxLayout()
        options_layout_01.addWidget(self.chat_model_cbx)

        options_layout_02 = QtWidgets.QHBoxLayout()
        options_layout_02.addWidget(maxcall_label)
        options_layout_02.addWidget(self.maxcall_spinbox)
        options_layout_02.addWidget(temperature_label)
        options_layout_02.addWidget(self.temperature_spinbox)
        options_layout_02.addWidget(top_p_label)
        options_layout_02.addWidget(self.top_p_spinbox)
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(options_layout_01)
        main_layout.addLayout(options_layout_02)
        main_layout.addWidget(self.text_edit)
        main_layout.addWidget(self.user_input)
        main_layout.addWidget(self.ask_button)
        
        widget = QtWidgets.QWidget(self)
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def ask(self):
        query = self.user_input.toPlainText()

        if not query.strip():
            return
        
        options = {
            "temperature": self.temperature_spinbox.value(),
            "top_p": self.top_p_spinbox.value(),
            "functions": self.function_set.functions,
            "function_call": "auto",
        }

        self.statusBar().showMessage("Ask the agent...")
        cmds.refresh()

        # エージェントへ問い合わせて更新されたメッセージを受け取る
        self.messages, assistant_message = self.agent(
            query=query, 
            messages=self.messages, 
            model=self.chat_model_cbx.currentText(), 
            max_call=self.maxcall_spinbox.value(),
            **options
        )

        self.text_edit.setText(assistant_message)
        self.statusBar().showMessage("Fin.")
        cmds.refresh()

def show_ui(vectorstore_path:Path):
    ui = UI(vectorstore_path, parent=maya_main_window())
    ui.show()