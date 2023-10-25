import sys
import json

from .functions import FunctionSet
from .utils import MDLogger
from .openai_utils import (
    chat_completion, 
    DEFAULT_CHAT_MODEL
)

from maya import cmds

MAX_MESSAGE_LENGTH = 8

SYSTEM_PROMPT = """You are a professional who works with **Autodesk Maya** with python code.
When you run the code, it will run on Maya. Maya is already up and running.
Do not try packages that are not installed as standard with Autodesk Maya.
Execution results and other important information should be stored in variables so that you can be referenced at any time. Variables and functions are preserved between each code block. Since you have extreme memory loss, important information stored in variables must be displayed each time.
If the user has given you an external document, pay particular attention to its content. Find out what you don't know. Don't just answer with your existing knowledge.
In general, try to **make plans** with as few steps as possible. 
When repeating similar tasks multiple times, prepare and use functions that can execute the tasks. Writing the same code over and over again is very inefficient. Consider updating the function if necessary.
If there is clearly insufficient data given to perform a task, please report this to the user at the **end of the task**. In such a case, please do not interrupt the task in progress, complete only the tasks that are possible, and report both completed and uncompleted tasks. Please save the report as a text file to desktop.
Never delegate tasks to users. You can access all of Maya's features through Python code. You are capable of **any** task."""

class Agent:

    def __init__(self, functions:FunctionSet):
        self.functions = functions
        self.mdlogger = None
        
    def _log(self, line:str, codeblock=None):
        if not self.mdlogger:
            return
        self.mdlogger(line, codeblock)

    def __call__(
            self, 
            prompt:str, 
            model:str=DEFAULT_CHAT_MODEL, 
            max_call:int=20, 
            mdlogger:MDLogger=None
        ):

        # ロガー準備
        self.mdlogger = mdlogger

        # プロンプトの最後に追加する文
        prompt += "\n\n現在は{maya_version}が起動中。Python Versionは{python_version}です。\nそれでは仕事を始めましょう。".format(
            maya_version=cmds.about(installedVersion=True), 
            python_version='{}.{}.{}'.format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro),
        )        

        self._log(SYSTEM_PROMPT, codeblock="")
        self._log(prompt, codeblock="")
        
        # メッセージ配列準備
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.append({"role": "user", "content": prompt})

        # メイン処理（max_callに達っしたら強制終了）
        for i in range(max_call):

            cmds.refresh()

            # メッセージ長調整（トークン制限対策）
            while True:
                if len(messages) > MAX_MESSAGE_LENGTH:
                    messages.pop(2)
                else:
                    break

            self._log("\n\n# Step:{} ({})".format(i, model))
            print("\n\n" + "//"*30)
            print("Step:{} ({})".format(i, model))
            
            # APIリクエスト
            options = {
                "temperature": 0,
                "top_p": 1,
                "functions": self.functions.functions,
                "function_call": "auto",
            }
            finish_reason, message = chat_completion(messages, model, **options)
            agent_message = message["content"].strip() if message["content"] else ""
            
            self._log("Finish Reason: `{}`  ".format(finish_reason))
            self._log("Agent: {}  ".format(agent_message))
            print(agent_message)

            # 返答をメッセージ配列へ追加
            messages.append(message)

            # GPTが関数を呼び出したいかどうか判定
            if finish_reason == "function_call":
                # 関数名と引数取得
                func_name = message["function_call"]["name"]
                arguments = json.loads(message["function_call"]["arguments"])
                
                self._log("Call : `{}`  ".format(func_name))
                self._log("Arguments : {}  ".format(json.dumps(arguments, indent=4, ensure_ascii=False)))
                print("Call : `{}`  ".format(func_name))

                # 関数実行
                func_returns = getattr(self.functions, func_name)(**arguments)

                if func_name == "exec_code":
                    self._log("### " + arguments["headline"] + " ###\n\n" + arguments["python_code"], codeblock="python")
                self._log("Result :  ")
                self._log(func_returns, codeblock="")
                print(func_returns)

                # 関数の実行結果をメッセージに追加
                messages.append({"role": "function", "name": func_name, "content": func_returns})
            else:
                # 関数を呼び出さない場合は終了
                break
        
        return messages, agent_message