import sys
import json
import time
import keyboard
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

from .tools import ToolSet
from .utils import MDLogger
from .openai_utils import (
    chat_completion, 
    DEFAULT_CHAT_MODEL,
    ChatCompletionMessage,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionToolMessageParam,
)
from .dialog import (
    maya_main_window,
    information,
    confirm,
)

from maya import cmds

MAX_MESSAGE_LENGTH = 20

TEMPERATURE = 0
TOP_P = 1

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

    def __init__(self, toolset:ToolSet):
        self.toolset = toolset
        self.mdlogger = None
        
    def _log(self, line:str, codeblock=None):
        if not self.mdlogger:
            return
        self.mdlogger(line, codeblock)
    
    def _monitor_keys(self):
        """ Key input acceptance thread (for interruption)"""
        while not self.exit_flag:
            time.sleep(0.2)
            if keyboard.is_pressed('esc'):
                self.exit_flag = 1
                break

    def _adjust_message_length(self, messages:List):
        while True:
            if len(messages) > 8:
                deleted_message = messages.pop(2)

                if type(deleted_message) == ChatCompletionMessage:
                    tool_calls = deleted_message.tool_calls
                elif type(deleted_message) == dict:
                    tool_calls = deleted_message.get("tool_calls")
                
                if tool_calls:
                    for i in range(len(tool_calls)):
                        if len(messages) > 3:
                            messages.pop(2)
            else:
                break
        
        return messages

    def __call__(
            self, 
            prompt:str, 
            model:str=DEFAULT_CHAT_MODEL, 
            max_call:int=20, 
            auto:bool=True,
            mdlogger:MDLogger=None
        ):

        # Turn off exit flag
        self.exit_flag = 0

        # Create key input acceptance thread
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(self._monitor_keys)

        # Prepare markdown logger
        self.mdlogger = mdlogger

        # Added version information to system prompts
        system_prompt = SYSTEM_PROMPT + "\n\nCurrently {maya_version} is running. python Version is {python_version}.".format(
            maya_version=cmds.about(installedVersion=True), 
            python_version='{}.{}.{}'.format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro),
        )        

        self._log(system_prompt, codeblock="")
        self._log(prompt, codeblock="")
        
        # Prepare message list
        messages = [
            ChatCompletionSystemMessageParam(role="system", content=system_prompt),
            ChatCompletionUserMessageParam(role="user", content=prompt)
        ]

        # Main (Force interruption when max_call is reached)
        for i in range(max_call):

            if self.exit_flag:
                self._log("\n\npressed esc. interrupt.")
                break

            cmds.refresh()

            self._adjust_message_length(messages)

            self._log("\n\n# Step:{} ({})".format(i, model))
            print("\n\n" + "//"*30)
            print("Step:{} ({})".format(i, model))
            
            # API request
            options = {
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
                "tools": self.toolset.tools,
                "tool_choice": "auto",
            }
            message = chat_completion(messages, model, **options)
            tool_calls = message.tool_calls
            agent_message = message.content.strip() if message.content else ""
            
            #self._log("Finish Reason: `{}`  ".format(finish_reason))
            self._log("Agent: {}  ".format(agent_message))
            print(agent_message)

            # Append reply to message list
            messages.append(message)

            if self.exit_flag:
                self._log("\n\npressed esc. interrupt.")
                break

            # Ask user every time, if not in auto mode.
            if not auto:
                confirm_result, instruct_text = confirm(maya_main_window(), "Step:{} ({})".format(i, model), agent_message)
                if confirm_result == 1:
                    pass
                elif confirm_result == 0:
                    break
                elif confirm_result == 2 and instruct_text:
                    # If the user gives additional instructions, the function is not executed and continue.
                    messages.append(ChatCompletionUserMessageParam(role="user", content=instruct_text))
                    self._log("User Instruct :  ")
                    self._log(instruct_text, codeblock="")
                    print(instruct_text)
                    continue
                else:
                    pass

            # Check if GPT wants to call a function
            if tool_calls:
                for tool_call in tool_calls:
                    # Get function name and arguments
                    func_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    self._log("Call : `{}`  ".format(func_name))
                    self._log("Arguments : {}  ".format(json.dumps(arguments, indent=4, ensure_ascii=False)))
                    print("Call : `{}`  ".format(func_name))

                    # Execute function
                    func_returns = getattr(self.toolset, func_name)(**arguments)

                    if func_name == "exec_code":
                        self._log(arguments["python_code"], codeblock="python")
                    self._log("Result :  ")
                    self._log(func_returns, codeblock="")
                    print(func_returns)

                    # Append the result of function to message list
                    messages.append(
                        ChatCompletionToolMessageParam(
                            tool_call_id=tool_call.id,
                            role="tool",
                            name=func_name,
                            content=func_returns
                        )
                    )
            else:
                # Break if the function is not called
                break
        
        # Shutdown key acceptance thread
        self.exit_flag = 1
        executor.shutdown(wait=True)

        # Display completion message
        if auto:
            information(maya_main_window(), "Done!", agent_message)

        return messages, agent_message