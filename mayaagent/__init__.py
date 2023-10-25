from .agent import Agent
from .functions import FunctionSet
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
    
    # エージェントへ問い合わせて更新されたメッセージを受け取る
    messages, agent_message = agent(
        prompt=task,
        model=model, 
        max_call=max_call,
    )

    return messages, agent_message