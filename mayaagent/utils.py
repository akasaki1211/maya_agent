
import os
from pathlib import Path
from datetime import datetime

class MDLogger():

    def __init__(self, log_dir:Path=None) -> None:
        
        if not log_dir:
            log_dir = Path(os.environ["MAYA_APP_DIR"], "maya_agent_log")
        log_dir.mkdir(parents=True, exist_ok=True)

        file_name = "{}.md".format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        self.log_path = Path(log_dir, file_name).resolve()

    def __call__(self, line:str, codeblock=None):
        
        if not codeblock is None:
            line = "````{}\n{}\n````".format(codeblock, line)
        
        with open(self.log_path, mode="a", encoding="utf-8") as f:
            f.write(line + "\n")