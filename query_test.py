from pathlib import Path
import json
from rigagent.openai_utils import (
    get_embedding,
    cosine_similarity
)

def query_test(path:Path, query:str, k:int=4):
    """ 与えられたクエリに基づいて、ベクトルストア内のテキストとの類似度を計算し、類似度が高い上位k個のテキストとそのスコアを表示する。 """

    # ベクトルストアを読み込む。
    with open(path, mode="r", encoding="utf-8") as f:
        vector_store = json.load(f)

    # クエリの埋め込みを取得。
    query_embedding = get_embedding(query)

    # 各テキストとの類似度を計算。
    scores = [(data["content"], cosine_similarity(query_embedding, data["embedding"])) for data in vector_store]

    # スコアを降順にソート。
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

    # 最も類似度が高いテキストとそのスコアを表示。
    for i in range(k):
        print(sorted_scores[i][0])
        print("score:", sorted_scores[i][1])
        print('--'*30)

query_test(Path("./rigdata/rig_manual_mgear_biped.json"), "腕のIKFK切り替え", k=3)