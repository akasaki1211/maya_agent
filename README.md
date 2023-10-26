# Maya Agent
[Function calling](https://openai.com/blog/function-calling-and-other-api-updates)とRAG(Retrieval-Augmented Generation)を使用した、Maya上で動くサポートエージェント  

**テスト環境**
* Windows 10
* Maya 2024 (Python 3.10.8)
* openai 0.28.1

## セットアップ
1. [API keys - OpenAI API](https://platform.openai.com/account/api-keys)よりAPI Keyを取得し、環境変数`OPENAI_API_KEY`に設定

2. [install.bat](./install.bat)を実行し、Maya2024にパッケージをインストール

3. 次のいずれかを実施
   * C:/Users/<ユーザー名>/Documents/maya/<バージョン>/scriptsに`mayaagent`フォルダをコピーする
   * 環境変数PYTHONPATHに`mayaagent`の親フォルダを追加する


## Agent起動

以下、MayaのScriptEditorで実行

```python
# 通常起動
import mayaagent
task = "シーンにあるポリゴン板の頂点を上下にランダム移動してボコボコにしてほしい。"
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
# 検索用ベクトルストアを含む関数セットを渡して起動
from pathlib import Path
import mayaagent
from mayaagent import FunctionSetWithVectorSearch, VectorStore

function_set = FunctionSetWithVectorSearch(
    manual_vs=VectorStore(Path("~/rig_manual_mgear_biped.json")),
    manual_description="Find relevant information in the rig handling manual. The manual outlines the rig controller name, its function, and other auxiliary functions.",
)

task = "両腕両足をFKに切り替えて"
mayaagent.run(task, function_set=function_set)
```


## ベクトルストア作成

[vectorstore_test.py](./vectorstore_test.py)を参照

```python
from pathlib import Path
from mayaagent.vectorstore import VectorStore

# ベクトルストア作成
vec_store = VectorStore()
vec_store.txt_to_vectorstore(Path("./rigdata/rig_manual_mgear_biped.txt"))
```

```python
from pathlib import Path
from mayaagent.vectorstore import VectorStore

# ベクトルストア読込 → 検索
vec_store = VectorStore(Path("./rigdata/rig_manual_mgear_biped.json"))
search_result = vec_store.similarity_search("腕のIKFK切り替え")
for sr in search_result:
    print(sr[0]["content"])
    print("score:", sr[1])
    print('--'*30)
```

> **Note**  
> * [`./rigdata/rig_manual_mgear_biped.txt`](./rigdata/rig_manual_mgear_biped.txt)は、[mGear 4.1.0](https://github.com/mgear-dev/mgear4/releases/tag/4.1.0)の「**Biped Template, Y-up**」用に作成したマニュアルテキストです。  
> * これをベクトルストアにしたものも置いてあります。（[`./rigdata/rig_manual_mgear_biped.json`](./rigdata/rig_manual_mgear_biped.json)）  
> * mGear4.1.0でBipedリグをビルドしておくことですぐに試すことができます。  