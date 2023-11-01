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
        # Create instance of default FunctionSet
        function_set = FunctionSet()

    # Create instance of Agent
    agent = Agent(function_set)

    # Prepare logger
    mdlogger = MDLogger()
    
    # Call
    messages, agent_message = agent(
        prompt=task,
        model=model, 
        max_call=max_call,
        auto=auto,
        mdlogger=mdlogger
    )

    return messages, agent_message