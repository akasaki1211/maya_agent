# Maya Agent
<p align="center">
<img src="./.images/cover.png" alt="Maya Agent" style="width: 80%;"><br>
MayaAgent performs Autodesk Maya operations with natural-language instructions.<br>
<img src="https://img.shields.io/static/v1?message=Maya&color=0696D7&logo=Autodesk&logoColor=white&label=" alt="[Autodesk Maya]"> <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License:MIT"><br>
<a href="./README_ja.md">[日本語README]</a>
<a href="https://twitter.com/akasaki1211/status/1716746810403029290">[🎥Demo movie]</a>
</p>

---

> **Tested with**
> * Windows 10
> * Maya 2024 (Python 3.10.8)
> * openai 1.1.1

## Getting Started
1. Obtain the API Key from [API keys - OpenAI API](https://platform.openai.com/account/api-keys), and set it to the environment variable `OPENAI_API_KEY`.
2. Run [./setup/install_maya2024_win.bat](./setup/install_maya2024_win.bat) to install the package on Maya2024.
3. Do one of the following
    * Copy the `mayagent` folder to `C:/Users/<USERNAMEe>/Documents/maya/<VERSION>/scripts`  
    * Add the parent folder of `mayaagent` to the `PYTHONPATH` environment variable


## Usage

### Run Agent 🤖

Execute the following in Maya ScriptEditor.  

```python
### Normal start ###

import mayaagent
task = "First, please read and understand the manual (motion_export_manual.md) carefully. Please follow the steps described in the manual and export all motions with a Status of 'Fin' to FBX."
mayaagent.run(task)
```

```python
### Normal start (with options) ###

mayaagent.run(
    task, 
    model="gpt-4-1106-preview", # Model. "gpt-4-1106-preview" or "gpt-3.5-turbo-1106"
    max_call=20,                # Maximum number of loops. Forced interruption when this number is reached.
    auto=True                   # If False, a confirmation dialog box will appear before each turn of function execution.
)
```

```python
### Give a function set containing a vectorstore, and start. ###

from pathlib import Path
import mayaagent
from mayaagent.tools import ToolSetWithVectorSearch
from mayaagent.vectorstore import VectorStore

# Prepare vectorstore
manual_vs = VectorStore(
    path=Path("rig_manual_mgear_biped.json"),
    description="Find relevant information in the rig handling manual. The manual outlines the rig controller name, its function, and other auxiliary functions."
)

# Prepare a function set containing a vectorstore
tool_set = ToolSetWithVectorSearch(manual_vs=manual_vs)

# Agent Start
task = "Arms stop extending about 1.5x, can you make them extend indefinitely?"
mayaagent.run(task, toolset=tool_set)
```

For example, you can input the following tasks.  
* "Please read and understand the Motion Export Manual (filepath). Only export completed motions to FBX according to the manual."  
* "Please group the models in scene by category. If you find any strange names, please fix them and report them to me."  
* "Import and build mGear guide into latest character model scene. Please find a guide file. Here is the mGear Script Guide (filepath)."  

Please see the [demo](https://twitter.com/akasaki1211/status/1716746810403029290) for more details.

> **Warning**  
> Make multiple requests to GPT-4 in one `mayagent.run` method call. Please note the tokens used.

### Vector Store 📄

Execute the following in Maya, VSCode, etc.

#### Vector Store Creation
```python
from pathlib import Path
from mayaagent.vectorstore import VectorStore

# create vector store from txt file.
vec_store = VectorStore.from_txt_file(
    text_path=Path("./rigdata/rig_manual_mgear_biped.txt"), 
    split_char="\n\n\n",
    description="Find relevant information in the rig handling manual. The manual outlines the rig controller name, its function, and other auxiliary functions."
)
```

#### Vector Store Loading, and Query Test
```python
from pathlib import Path
from mayaagent.vectorstore import VectorStore

# load vector store
vec_store = VectorStore(Path("./rigdata/rig_manual_mgear_biped.json"))

# query
search_result = vec_store.similarity_search("IKFK switching of arms", k=2)

for sr in search_result:
    print(sr[0]["content"])
    print("score:", sr[1])
    print('--'*30)
```

> **Note**   
> * [`./rigdata/rig_manual_mgear_biped.txt`](./rigdata/rig_manual_mgear_biped.txt) is the manual texts created for the **"Biped Template, Y-up"** in [mGear 4.1.0](https://github.com/mgear-dev/mgear4/releases/tag/4.1.0).  
> * A vector store of this is also located here. ([`./rigdata/rig_manual_mgear_biped.json`](./rigdata/rig_manual_mgear_biped.json))  
> * You can try it immediately by building the Biped rig with mGear 4.1.0.  