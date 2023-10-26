try:
    from .agent import Agent
except ImportError as e:
    print(e)

from .functions import FunctionSet
from .utils import MDLogger
from .openai_utils import DEFAULT_CHAT_MODEL

def run(
        task:str, 
        model:str=DEFAULT_CHAT_MODEL, 
        max_call:int=20, 
        auto:bool=True,
        function_set:FunctionSet=None
    ):

    if not function_set:
        # デフォルトの関数セットのインスタンスを作成
        function_set = FunctionSet()

    # エージェントのインスタンスを作成
    agent = Agent(function_set)

    # ロガー準備
    mdlogger = MDLogger()
    
    # エージェントへ問い合わせて更新されたメッセージを受け取る
    messages, agent_message = agent(
        prompt=task,
        model=model, 
        max_call=max_call,
        auto=auto,
        mdlogger=mdlogger
    )

    return messages, agent_message