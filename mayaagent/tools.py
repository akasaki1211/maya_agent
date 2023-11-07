import sys
import traceback
from io import StringIO

from .openai_utils import ChatCompletionToolParam
from .vectorstore import VectorStore

MAYA_OUTPUT = sys.stdout

class ToolSet:

    def __init__(self):
        self.tools = [
            ChatCompletionToolParam(
                type="function",
                function={
                    "name": "exec_code",
                    "description": "Executes python code on **Autodesk Maya** and returns output.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "python_code": {
                                "type": "string",
                                "description": "The python code to execute (required). Be sure to insert a print() that outputs the result of the execution on the line where the main process is executed.",
                            },
                        },
                        "required": ["python_code"],
                    },
                },
            )
        ]
    
    def exec_code(self, python_code:str):
        """
            Function to execute python code in Maya.
            Returns stdout if successfully executed. If an error occurs, an error statement is returned.
        """

        try:
            buffer = StringIO()
            sys.stdout = buffer

            exec(python_code, globals())

            sys.stdout = MAYA_OUTPUT
            captured_output = str(buffer.getvalue()).strip()

            if len(captured_output) > 2000:
                output_result = captured_output[:500]
                output_result += "\n\n...\n\nThe outputs is too long. Please extract only the information you need."
            elif not captured_output:
                output_result = "**There is no output!!!** Insert a print() that outputs the result of the execution on the line where the main process is executed."
            else:
                output_result = captured_output

            return "## OUTPUT ##\n" + output_result
        
        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            trace = traceback.format_exception(exc_type, exc_value, exc_traceback)
            err = "{}: {}: {}".format(exc_type.__name__, trace[-2].strip(), exc_value)
            
            sys.stdout = MAYA_OUTPUT
            
            return "## ERROR ##\n" + err



class ToolSetWithVectorSearch(ToolSet):

    def __init__(self, manual_vs:VectorStore):
        super(ToolSetWithVectorSearch, self).__init__()

        self.manual_vs = manual_vs        
        self.tools.append(
            ChatCompletionToolParam(
                type="function",
                function={
                    "name": "search_manual",
                    "description": self.manual_vs.description,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search terms for what content you want to retrieve related documents from the manual.",
                            },
                        },
                        "required": ["query"],
                    },
                }
            )
        )

    def search_manual(self, query:str):
        """ Retrieve the items corresponding to the search term (query) from the manual. """
        search_result = self.manual_vs.similarity_search(query, k=2)
        return "\n".join([sr[0]["content"] for sr in search_result])