import openai
# from openai import OpenAI
from PIL import Image
import io
import sys
import base64

from .credentials import openai_key

def query_chatGPT(user_prompt, img_path, system_prompt = None, temperature=1, max_tokens=256, top_p=1, frequency_penalty=0, presence_penalty=0):
    if not openai_key:
        print("Error: No OpenAI API key found. Please set the API key in the credentials file.")
        sys.exit(1)

    client = openai.OpenAI(api_key=openai_key)
    system_prompt = system_prompt if system_prompt else "Please describe the image."

    # Open, resize, and encode the image
    with open(img_path, 'rb') as image_file:
        # Load the image
        img = Image.open(image_file)
        
        # Resize the image, maintaining aspect ratio and ensuring max dimensions of 512x512
        img.thumbnail((128, 128), Image.Resampling.LANCZOS)
        
        # Save the resized image to a bytes buffer to avoid writing back to disk
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        encoded_string = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    
    # Prepare the messages for the API call
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        },
        {
            "role": "user",
            "content": "data:image/jpeg;base64," + encoded_string
        }
    ]
    
    # Call the OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        return response.choices[0].message.content, response
    except Exception as e:
        print(f"Error: An exception occurred while querying ChatGPT: {str(e)}")
        sys.exit(1)