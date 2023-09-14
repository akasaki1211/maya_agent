import sys
import traceback
from typing import List

from maya import cmds

from .vectorstore import VectorStore

class FunctionSet:

    def __init__(self, manual_vs:VectorStore):
        self.manual_vs = manual_vs

        self.functions = [
            {
                "name": "search_manual",
                "description": "リグの取り扱いマニュアルから関連する情報を検索します。マニュアルにはリグコントローラ名とその機能、その他の補助機能の概要が書いてあります。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "マニュアルからどのような内容の関連文書を取得したいかの検索語句",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "select_ctls",
                "description": "指定した名前のリグコントローラを選択する。複数可。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ctl_list": {
                            "type": "array",
                            "description": "リグコントローラ名の配列",
                            "items": {
                                "type": "string",
                            },
                        },
                    },
                    "required": ["ctl_list"],
                },
            },
            {
                "name": "set_attribute",
                "description": "指定した名前のリグコントローラの、指定したアトリビュートを、指定した値に設定する。複数可。コントローラを選択している必要はない。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "attribute_data_list":{
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {
                                    "ctl_name":{
                                        "type": "string",
                                        "description": "リグコントローラ名",
                                    },
                                    "attribute_name":{
                                        "type": "string",
                                        "description": "アトリビュート名",
                                    },
                                    "value":{
                                        "type": "string",
                                        "description": "設定値",
                                    },
                                },
                                "minItems": 3,
                                "maxItems": 3
                            },
                        },
                    },
                    "required": ["attribute_data_list"],
                },
            },
            {
                "name": "get_attribute_value",
                "description": "指定した名前のリグコントローラの、指定したアトリビュートの値を取得する。複数可。コントローラを選択している必要はない。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "attribute_data_list":{
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {
                                    "ctl_name":{
                                        "type": "string",
                                        "description": "リグコントローラ名",
                                    },
                                    "attribute_name":{
                                        "type": "string",
                                        "description": "アトリビュート名",
                                    },
                                },
                                "minItems": 2,
                                "maxItems": 2
                            },
                        },
                    },
                    "required": ["attribute_data_list"],
                },
            },
            {
                "name": "exec_code",
                "description": "pythonスクリプトを実行します。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "pythonコード",
                        },
                    },
                    "required": ["code"],
                },
            },
        ]


    # 既存の知識に無い部分を補う
    def search_manual(self, query:str):
        """ マニュアルから検索語句(query)に該当する箇所を取得する """
        search_result = self.manual_vs.similarity_search(query)
        return "\n".join([sr[0]["content"] for sr in search_result])

    # Mayaから情報を得る／操作する
    def select_ctls(self, ctl_list:List[str]):
        """ 指定したノードを選択する """
        msg = []
        for ctl in ctl_list:
            if not cmds.objExists(ctl):
                msg.append("{}というコントローラは無い。".format(ctl))
        if msg:
            msg.append("マニュアルを確認し正しいコントローラ名を得る必要がある。")
            return "\n".join(msg)
    
        cmds.select(ctl_list)
        return "{}を選択した。".format(",".join(ctl_list))

    def set_attribute(self, attribute_data_list:List[List]):
        """ 指定したノードの指定したアトリビュートを指定値にセットする """        
        msg = []
        for ctl, attr, value in attribute_data_list:
            full_attr = ctl + "." + attr
            if not cmds.objExists(ctl):
                msg.append("{}というコントローラは無い。マニュアルを確認し正しいコントローラ名を得る必要がある。".format(ctl))
            elif not cmds.objExists(full_attr):
                msg.append("{}に{}というアトリビュートはない。マニュアルを確認し正しいアトリビュート名を得る必要がある。".format(ctl, attr))
            else:
                if type(value) == str:
                    value = self._convert_str(value)
                if type(value) == str:
                    cmds.setAttr(full_attr, value, type="string")
                else:
                    cmds.setAttr(full_attr, value)
                msg.append("{}を{}に設定した。".format(full_attr, value))

        return "\n".join(msg)

    def get_attribute_value(self, attribute_data_list:List[List]):
        """ 指定したノードの指定したアトリビュートの現在値を取得する """
        msg = []
        for ctl, attr in attribute_data_list:
            full_attr = ctl + "." + attr
            if not cmds.objExists(ctl):
                msg.append("{}というコントローラは無い。マニュアルを確認し正しいコントローラ名を得る必要がある。".format(ctl))
            elif not cmds.objExists(full_attr):
                msg.append("{}に{}というアトリビュートはない。マニュアルを確認し正しいアトリビュート名を得る必要がある。".format(ctl, attr))
            else:
                value = cmds.getAttr(full_attr)
                msg.append("{}の現在の値は{}。".format(full_attr, value))

        return "\n".join(msg)

    def exec_code(self, code:str):
        """ pythonコードを実行する関数 エラーが発生したらエラー文を返す """
        try:
            exec(code, {'__name__': '__main__'}, None)
            return 'pythonコード実行完了'
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
            return "{}: {}: {}".format(exc_type.__name__, trace[-2].strip(), exc_value)

    def _convert_str(self, s:str):
        """ 文字列の内容に基づいて適切な型(bool, int, float, str)に変換する """
        if s.lower() == "true":
            return True
        elif s.lower() == "false":
            return False
    
        try:
            return int(s)
        except ValueError:
            pass
    
        try:
            return float(s)
        except ValueError:
            pass
    
        return s