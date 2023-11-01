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
    Class that manages the vector store. 
    Provides the ability to retrieve text embeddings and perform similarity searches.
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
        """ 
        Calculate the similarity to the text in the vector store with the given query and return the top k most similar texts and their scores.
        """
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
        """ 
        Convert text file to vectorstore
        """

        # Open txt file
        with open(text_path, 'r', encoding="utf-8") as f:
            text = f.read()

        # split texts
        texts = [t.strip() for t in text.split(split_char) if t.strip()]
        
        # get embedding of each text
        embeddings = get_embeddings(texts)

        # Prepare vectorstore data
        vector_store = []
        for i, t in enumerate(texts):
            vector_store.append(
                {
                    "content": t,
                    "embedding": embeddings[i],
                }
            )

        # Save the vectorstore as a JSON file
        save_path = text_path.with_suffix('.json')
        with open(save_path, mode="w", encoding="utf-8") as f:
            json.dump(vector_store, f, ensure_ascii=False)

        return cls(
            path=save_path, 
            description=description
        )