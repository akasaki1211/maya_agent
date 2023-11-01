from pathlib import Path
from typing import List, Tuple, Optional
import json

from .openai_utils import (
    get_embedding,
    get_embeddings,
    cosine_similarity
)

class VectorStore:
    """
    ベクトルストアを管理するクラス。テキストの埋め込みを取得し、類似度検索を行う機能を提供。
    """

    def __init__(
        self, 
        path: Optional[Path]=None, 
        description: Optional[str]=""
    ) -> None:
        
        self.vector_store = []
        self.description = description
        if path:
            with open(path, mode="r", encoding="utf-8") as f:
                self.vector_store = json.load(f)

    def similarity_search(
        self, 
        query: str, 
        k: Optional[int]=4
    ) -> List[Tuple]:
        """ 与えられたクエリに基づいて、ベクトルストア内のテキストとの類似度を計算し、上位k件の最も類似度が高いテキストとそのスコアを返す。 """
        query_embedding = get_embedding(query)
        scores = [(data, cosine_similarity(query_embedding, data["embedding"])) for data in self.vector_store]
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        return sorted_scores[:k]

    @classmethod
    def from_txt_file(
        cls, 
        text_path: Path, 
        split_char: Optional[str]="\n\n\n",
        description: Optional[str]=""
    ) -> "VectorStore":
        """ 指定されたテキストファイルをベクトルストアに変換 """

        # テキストファイルを読み取る。
        with open(text_path, 'r', encoding="utf-8") as f:
            text = f.read()

        # テキストを個々のテキストに分割。
        texts = [t.strip() for t in text.split(split_char) if t.strip()]
        
        # 各テキストの埋め込みを取得。
        embeddings = get_embeddings(texts)

        # ベクトルストアデータを準備。
        vector_store = []
        for i, t in enumerate(texts):
            vector_store.append(
                {
                    "content": t,
                    "embedding": embeddings[i],
                }
            )

        # ベクトルストアをJSONファイルとして保存。
        save_path = text_path.with_suffix('.json')
        with open(save_path, mode="w", encoding="utf-8") as f:
            json.dump(vector_store, f, ensure_ascii=False)

        return cls(
            path=save_path, 
            description=description
        )