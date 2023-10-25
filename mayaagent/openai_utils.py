from typing import List, Tuple

import openai

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

@retry_decorator
def chat_completion(messages:List, model:str=DEFAULT_CHAT_MODEL, **kwargs) -> Tuple:
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        **kwargs
    )
    finish_reason = response.choices[0]["finish_reason"]
    message = response.choices[0]["message"]

    return finish_reason, message