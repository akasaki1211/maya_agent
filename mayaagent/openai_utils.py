from typing import List, Tuple
import json

import openai
from openai.datalib.numpy_helper import numpy as np

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

def retry_decorator(func):
    return retry(
        stop=stop_after_attempt(6),
        wait=wait_random_exponential(min=1, max=20)
    )(func)

DEFAULT_CHAT_MODEL = "gpt-4-0613"
DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

@retry_decorator
def chat_completion(messages:List, model:str=DEFAULT_CHAT_MODEL, **kwargs) -> Tuple:
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        **kwargs
    )
    finish_reason = response.choices[0]["finish_reason"]
    message = response.choices[0]["message"]
    
    if finish_reason == "function_call":
        json.loads(message["function_call"]["arguments"])

    return finish_reason, message

@retry_decorator
def get_embedding(text: str, engine=DEFAULT_EMBEDDING_MODEL, **kwargs) -> List[float]:
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], engine=engine, **kwargs)["data"][0]["embedding"]

@retry_decorator
def get_embeddings(list_of_text: List[str], engine=DEFAULT_EMBEDDING_MODEL, **kwargs) -> List[List[float]]:
    assert len(list_of_text) <= 2048, "The batch size should not be larger than 2048."

    # replace newlines, which can negatively affect performance.
    list_of_text = [text.replace("\n", " ") for text in list_of_text]

    data = openai.Embedding.create(input=list_of_text, engine=engine, **kwargs).data
    return [d["embedding"] for d in data]