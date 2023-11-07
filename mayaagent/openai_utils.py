from typing import List
import numpy as np

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessage,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
)

client = OpenAI()

DEFAULT_CHAT_MODEL = "gpt-4-1106-preview"
DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def chat_completion(messages:List, model:str=DEFAULT_CHAT_MODEL, **kwargs) -> ChatCompletionMessage:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs
    )
    return response.choices[0].message

def get_embedding(text:str, **kwargs):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=DEFAULT_EMBEDDING_MODEL, **kwargs).data[0].embedding

def get_embeddings(texts:List[str], **kwargs):
    assert len(texts) <= 2048
    texts = [text.replace("\n", " ") for text in texts]
    data = client.embeddings.create(input=texts, model=DEFAULT_EMBEDDING_MODEL, **kwargs).data
    return [d.embedding for d in data]