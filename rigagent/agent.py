from typing import List
import json

from .functions import FunctionSet
from .openai_utils import chat_completion, DEFAULT_CHAT_MODEL

class Agent:

    def __init__(self, function_set:FunctionSet):
        self.func_set = function_set   
        self.system_prompt = """あなたはある特定のキャラクターリグの取り扱いをサポートする優秀なAIです。
質問に対し、必ずマニュアル内を検索し該当する記述があるかを確認してから返答してください。ユーザーにマニュアルの確認を促すことはしないでください。
一般的な既存の知識だけで返答することがないよう徹底してください。
不足している情報があれば無理に回答せず、ユーザーへ質問を返してください。"""

    def __call__(self, query:str, messages:List=[], model:str=DEFAULT_CHAT_MODEL, max_call:int=10, **kwargs):

        print("-------------")
        print("user: ", query)
        
        if len(messages) == 0:
            # メッセージが空だった場合（会話の最初だった場合）はmessagesにシステムプロンプト追加
            messages.append({"role": "system", "content": self.system_prompt})
        
        # ユーザーの問い合わせをmessagesに追加
        messages.append({"role": "user", "content": query})

        for i in range(max_call):

            # ターン数表示
            print("---- [{}] ----".format(i))

            # APIリクエスト
            finish_reason, message = chat_completion(messages, model, **kwargs)

            if finish_reason == "function_call":
                ### function 使う場合 ###

                # 関数名と引数取得
                func_name = message["function_call"]["name"]
                arguments = json.loads(message["function_call"]["arguments"])
                print("call <{}> args={}".format(func_name, arguments))

                # 関数セットから関数を取得し、引数を渡して実行
                func_returns = getattr(self.func_set, func_name)(**arguments)
                print(func_returns)

                # messagesに返答と関数の実行結果を追加
                messages.append(message)
                messages.append({"role": "function", "name": func_name, "content": func_returns})
            else:
                ### function 使わない場合 ###

                # messagesに返答を追加して終了
                messages.append(message)
                print("agent: ", message["content"].strip())

                break

        return messages, message["content"].strip()