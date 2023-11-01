# Maya Agent
<p align="center">
<img src="./.images/cover.png" alt="Maya Agent" style="width: 80%;"><br>
</p>

![Maya](https://img.shields.io/static/v1?message=Maya&color=0696D7&logo=Autodesk&logoColor=white&label=) ![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)  

OpenAI API [Function calling](https://openai.com/blog/function-calling-and-other-api-updates)を利用したMaya上で動くエージェント  

🎥 [Demo movie](https://twitter.com/akasaki1211/status/1716746810403029290)  

> **テスト環境**
> * Windows 10
> * Maya 2024 (Python 3.10.8)
> * openai 0.28.1

## セットアップ
1. [API keys - OpenAI API](https://platform.openai.com/account/api-keys)よりAPI Keyを取得し、環境変数`OPENAI_API_KEY`に設定

2. [./setup/install_maya2024_win.bat](./setup/install_maya2024_win.bat)を実行し、Maya2024にパッケージをインストール

3. 次のいずれかを実施
   * C:/Users/<ユーザー名>/Documents/maya/<バージョン>/scriptsに`mayaagent`フォルダをコピーする
   * 環境変数PYTHONPATHに`mayaagent`の親フォルダを追加する


## 使い方
### Agent起動🤖

以下、MayaのScriptEditorで実行

```python
# 通常起動
import mayaagent
task = "まずはマニュアル（motion_export_manual.md）をよく読んで理解してください。マニュアルに記載された手順を遵守しStatusがFinのモーションをすべてFBX書き出ししてください。"
mayaagent.run(task)
```

```python
# 通常起動（オプション付き）
mayaagent.run(
    task, 
    model="gpt-4-0613", # モデル "gpt-4-0613" または "gpt-3.5-turbo-0613"
    max_call=20,        # 最大ループ数。この数に達すると強制終了。
    auto=True           # Falseにすると毎ターン関数実行の前に確認ダイアログが出る
)
```

```python
# マニュアルのベクトルストアを含む関数セットを渡して起動
from pathlib import Path
import mayaagent
from mayaagent.functions import FunctionSetWithVectorSearch
from mayaagent.vectorstore import VectorStore

# マニュアルのベクトルストア準備
manual_vs = VectorStore(
    path=Path("rig_manual_mgear_biped.json"),
    description="Find relevant information in the rig handling manual. The manual outlines the rig controller name, its function, and other auxiliary functions."
)

# ベクトルストア検索を含む関数セットを準備
function_set = FunctionSetWithVectorSearch(manual_vs=manual_vs)

# エージェント起動
task = "IKで腕を伸ばした時に最大限に伸びるように出来ますか？"
mayaagent.run(task, function_set=function_set)
```


### ベクトルストア📄

以下を、MayaまたはVSCodeなどで実行

#### ベクトルストア作成
```python
from pathlib import Path
from mayaagent.vectorstore import VectorStore

# テキストからベクトルストア作成
vec_store = VectorStore.from_txt_file(
    text_path=Path("./rigdata/rig_manual_mgear_biped.txt"), 
    split_char="\n\n\n",
    description="Find relevant information in the rig handling manual. The manual outlines the rig controller name, its function, and other auxiliary functions."
)
```

#### ベクトルストア読込と検索テスト
```python
from pathlib import Path
from mayaagent.vectorstore import VectorStore

# ベクトルストア読込
vec_store = VectorStore(Path("./rigdata/rig_manual_mgear_biped.json"))

# 検索
search_result = vec_store.similarity_search("腕のIKFK切り替え", k=2)

for sr in search_result:
    print(sr[0]["content"])
    print("score:", sr[1])
    print('--'*30)
```

> **Note**  
> * [`./rigdata/rig_manual_mgear_biped.txt`](./rigdata/rig_manual_mgear_biped.txt)は、[mGear 4.1.0](https://github.com/mgear-dev/mgear4/releases/tag/4.1.0)の「**Biped Template, Y-up**」用に作成したマニュアルテキストです。  
> * これをベクトルストアにしたものも置いてあります。（[`./rigdata/rig_manual_mgear_biped.json`](./rigdata/rig_manual_mgear_biped.json)）  
> * mGear4.1.0でBipedリグをビルドしておくことですぐに試すことができます。  