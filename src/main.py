import os
import argparse
import time
import pandas as pd

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.image_utils import *
from src.ocr import *
from src.llm import *
from src.deck import *

os.environ['TESSDATA_PREFIX'] = 'tools/'

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process images and generate Anki decks')
    parser.add_argument('--input_directory', type=str, help='Input directory containing images')
    parser.add_argument('--use_openai', action='store_true', default=False, help='Use OpenAI GPT instead of LLaVA')
    return parser.parse_args()

def batch_ocr_llava_response(prompt, language_level, img_paths, temperature=0.2, chat=True, wait=1):
    content_responses = []
    model_responses = []
    ocr_text_list = []
    for i, img_path in enumerate(img_paths):
        print(f"Processing image: {i+1} of {len(img_paths)} - {img_path}")
        ocr_text = extract_ocr_text(img_path)
        ocr_text_list.append(ocr_text)
        ocr_prompt = prompt.format(ocr_output=ocr_text, language_level=language_level)
        if chat:
            c_response, m_response = ocr_llava_chat(ocr_prompt, img_path, temperature=temperature)
            print(json.dumps(m_response, indent=4))
            model_responses.append(m_response)
        else:
            c_response = ocr_llava(ocr_prompt, img_path, temperature=temperature)
        time.sleep(wait)
        content_responses.append(c_response)

    return content_responses, model_responses, ocr_text_list

def batch_openai_chatGPT_response(user_prompt, language_level, img_paths, system_prompt = None, max_tokens=4096, presence_penalty=0):
    content_responses = []
    ocr_text_list = []
    model_responses = []
    system_prompt = system_prompt if system_prompt else "Please describe the image."
    for i, img_path in enumerate(img_paths):
        print(f"Processing image: {i+1} of {len(img_paths)} - {img_path}")
        ocr_text = extract_ocr_text(img_path)
        ocr_text_list.append(ocr_text)
        ocr_prompt = user_prompt.format(ocr_output=ocr_text, language_level=language_level)
        c_response, m_response = query_chatGPT(ocr_prompt, img_path, system_prompt=system_prompt, max_tokens=max_tokens, presence_penalty=presence_penalty)
        content_responses.append(c_response)
        model_responses.append(m_response)

    return content_responses, model_responses, ocr_text_list


def main():
    args = parse_arguments()
    input_directory = args.input_directory if args.input_directory else "/Users/azeez/Downloads/language_test_imgs"
    llm_model = "gpt-4o" if args.use_openai else "llava-llama3"
    result_directory = os.path.join(input_directory, 'results')
    result_directory = os.path.join(result_directory, llm_model + "_" + str(pd.Timestamp.now().replace(microsecond=0)).replace(" ", "_").replace(":", "-"))
    os.makedirs(result_directory, exist_ok=True)

    heic_files, jpg_files = convert_heic_to_jpg(input_directory)
    img_metadata = [get_img_metadata(img_path) for img_path in heic_files]

    language_level = "A1"
    prompt = """
    Please help me clean up and extract German words from the following OCR output to build a study guide for German vocabulary at the {language_level} level.
    OCR output:
    {ocr_output}
    Steps:
    1. Clean the OCR output by removing any non-alphabetic characters, punctuation, numbers, non-unicode, and any text that clearly does not represent valid words in any language (e.g., "ae", "ee", "f").
    2. Identify and extract all valid German words from the cleaned-up text. Ensure that these words are found in the German dictionary.
    3. Exclude any English words or phrases and ensure only valid German words are included.
    4. Convert the extracted German words to lowercase, remove any duplicates, and add the proper articles to all nouns (der, die, das).
    5. Use your visual understanding of the image to confirm the extracted German words and their relevance to the scene.
    6. Based on your understanding of the scene and your visual analysis, suggest additional German words and small phrases (nouns, weather conditions, verbs, relationships, adjectives) that are relevant to the image and appropriate for the {language_level} level.
    7. Validate the suggested words and phrases to ensure they are all valid German words.
    8. Assess the quality of the OCR text and assign a quality flag (high, medium, or low) based on the clarity and completeness of the extracted words.
    9. Explain the relevance of the suggested words and phrases to the scene and the language level in one sentence, along with an explanation for the quality rating.
    10. Provide English translations for each extracted and suggested German word and phrase. Ensure that all translations are accurate and complete.
    11. Ensure that only valid German words and phrases are included in the "extracted_words" and "suggested_words" arrays.
    12. Ensure that if a word is a noun, it includes the proper article infront of it (der, die, das).
    13. Fill in the provided JSON template with the extracted words, suggested words and phrases, their translations, and the quality flag.
    14. **IMPORTANT**: The response must start with the marker "JSON_START:" followed by the JSON object.
    Please return the filled-in JSON object as the last part of your response, and precede it immediately with the marker "JSON_START:" Then immediatly return the json

    JSON schema:
    'extracted_words':[],'translated_extracted_words':[],'suggested_words':[],'translated_suggested_words':[],
    'image_quality':"", "relevance_explanation":"", "quality_explanation":""
    
    End of response. Please do not add any text or characters after the JSON object to ensure it can be parsed correctly.
    """

    if args.use_openai:
        system_prompt = "Please help me clean up and extract German words from the following OCR output to build a study guide for German vocabulary at the {language_level} level. OCR output: {ocr_output}"
        content_responses, model_responses, ocr_texts = batch_openai_chatGPT_response(prompt, language_level, jpg_files, system_prompt=system_prompt, max_tokens=4096, presence_penalty=0)
    else:
        content_responses, model_responses, ocr_texts = batch_ocr_llava_response(prompt, language_level, jpg_files, wait=3, chat=True)

    responses_df, metadata_df = build_table_from_responses(content_responses, ocr_texts, img_metadata, jpg_files)
    photo_df_metadata_cols = ['photo_id', 'image_datetime', 'latitude_ref', 'latitude', 'longitude_ref', 'longitude', 'altitude_ref', 'altitude', 'timestamp', 'date', 'jpg_path']
    photo_df_response_cols = ['photo_id', 'json_response', 'ocr_text', 'extracted_words', 'translated_extracted_words', 'suggested_words', 'translated_suggested_words', 'image_quality', 'relevance_explanation', 'quality_explanation']
    photo_df = pd.merge(metadata_df[photo_df_metadata_cols], responses_df[photo_df_response_cols], on='photo_id')
    vocab_df = build_vocab_table(photo_df, quality_cutoff='low')

    vocab_df.to_csv(os.path.join(result_directory, 'vocab_table.csv'), index=False)
    photo_df.to_csv(os.path.join(result_directory, 'photo_table.csv'), index=False)
    build_anki_deck(vocab_df, result_directory)

if __name__ == "__main__":
    main()