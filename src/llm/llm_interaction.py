import json
import logging
import time
import ollama
import httpx
import pandas as pd
# from src.ocr.text_extraction import extract_ocr_text

class ResponseError(Exception):
    pass

def chat_debug(model, messages, stream=False, max_retries=10, wait_time=1):
    retries = 0
    while retries < max_retries:
        try:
            response = ollama.chat(
                model=model,
                messages=messages,
                stream=stream,
                keep_alive="1s"
            )
            return response
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTPStatusError: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 429:
                logging.info("Rate limit exceeded. Retrying...")
                time.sleep(wait_time)
                retries += 1
                wait_time *= 2  # Exponential backoff
            else:
                raise ResponseError(e.response.text, e.response.status_code) from None
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise

    raise ResponseError("No slots available after maximum retries")

def ocr_llava(prompt, path, model='llava-llama3', temperature=0.2):
    with open(path, "rb") as image_file:
        image_bytes = image_file.read()
        result = ollama.generate(
            model=model,
            prompt=prompt,
            images=[image_bytes],
            stream=False,
            options={"temperature": temperature},
            keep_alive="1s",
            context="",
        )['response']
        return result

def chat(model, messages, stream=False):
    response = ollama.chat(
        model=model,
        messages=messages,
        stream=stream
    )
    return response

def ocr_llava_chat(prompt, path, model='llava-llama3', temperature=0.2):
    with open(path, "rb") as image_file:
        image_bytes = image_file.read()
    
    messages = [
        {
            'role': 'user',
            'images': [image_bytes],
            'content': ' '
        },
        {
            'role': 'user',
            'images': [],
            'content': prompt
        }
    ]
    
    result = chat(model, messages, stream=False)
    return result['message']['content'], result