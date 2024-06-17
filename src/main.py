# /visual-to-language-learning-llm
# |-- /src                         # Contains all the source code files
#     |-- __init__.py               # Makes src a Python package
#     |-- main.py                   # Main script to process images and generate Anki decks
#     |-- /ocr                     # Dedicated to optical character recognition functionalities
#         |-- __init__.py          # Makes ocr a Python package
#         |-- image_conversion.py  # Functions for image format conversions
#         |-- text_extraction.py   # OCR functions to extract text from images
#     |-- /llm                     # Interactions with language learning models
#         |-- __init__.py          # Makes llm a Python package
#         |-- llm_interaction.py   # Functions for processing text with language models
#     |-- /deck                    # Anki deck creation and management
#         |-- __init__.py          # Makes deck a Python package
#         |-- deck_building.py     # Functions to build Anki decks
#     |-- /utils                   # Utility functions, common across modules
#         |-- __init__.py          # Makes utils a Python package
#         |-- image_metadata.py    # Functions to retrieve metadata from images
# |-- /tests                       # Unit tests for all modules
       # Tests for OCR functionalities
    # |-- test_image_conversion.py
    # |-- test_text_extraction.py
    # |-- test_llm_interaction.py
    # |-- test_deck_building.py
# |-- /data                        # Data files, e.g., sample images or temporary storage
# |-- /docs                        # Documentation files
# |-- requirements.txt             # Python package dependencies
# |-- README.md                    # Project overview and setup instructions
# |-- .gitignore                   # Specifies intentionally untracked files to ignore

import os
import argparse
import time
import pandas as pd

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.image_utils import *
from src.ocr import *
# from src.image_utils.image_metadata import get_img_metadata
# from src.image_utils.image_conversion import convert_heic_to_jpg
from src.llm import *
from src.deck import *
from src.credentials import *

os.environ['TESSDATA_PREFIX'] = 'tools/'

def parse_arguments():
    parser = argparse.ArgumentParser(description='Process images and generate Anki decks')
    parser.add_argument('--input_directory', type=str, help='Input directory containing images')
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

def main():
    args = parse_arguments()
    input_directory = args.input_directory if args.input_directory else "/Users/azeez/Downloads/language_test_imgs"
    result_directory = os.path.join(input_directory, 'results')
    # add compatable datetime object to the result directory name
    result_directory = os.path.join(result_directory, str(pd.Timestamp.now().replace(microsecond=0)).replace(" ", "_").replace(":", "-"))
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
    4. Convert the extracted German words to lowercase and remove any duplicates.
    5. Use your visual understanding of the image to confirm the extracted German words and their relevance to the scene.
    6. Based on your understanding of the scene and your visual analysis, suggest additional German words and small phrases (nouns, weather conditions, verbs, relationships, adjectives) that are relevant to the image and appropriate for the {language_level} level.
    7. Validate the suggested words and phrases to ensure they are all valid German words.
    8. Assess the quality of the OCR text and assign a quality flag (high, medium, or low) based on the clarity and completeness of the extracted words.
    9. Explain the relevance of the suggested words and phrases to the scene and the language level in one sentence, along with an explanation for the quality rating.
    10. Provide English translations for each extracted and suggested German word and phrase. Ensure that all translations are accurate and complete.
    11. Ensure that only valid German words and phrases are included in the "extracted_words" and "suggested_words" arrays.
    12. Fill in the provided JSON template with the extracted words, suggested words and phrases, their translations, and the quality flag.
    13. **IMPORTANT**: The response must start with the marker "JSON_START:" followed by the JSON object.
    JSON schema:
    'extracted_words':[],'translated_extracted_words':[],'suggested_words':[],'translated_suggested_words':[],
    'image_quality':"", "relevance_explanation":"", "quality_explanation":""
    Please return the filled-in JSON object as the last part of your response, and precede it immediately with the marker "JSON_START:".
    """
    content_responses, model_responses, ocr_texts = batch_ocr_llava_response(prompt, language_level, jpg_files[1:2], wait=3, chat=False)
    responses_df, metadata_df = build_table_from_responses(content_responses, ocr_texts, img_metadata)
    photo_df_metadata_cols = ['photo_id', 'image_datetime', 'latitude_ref', 'latitude', 'longitude_ref', 'longitude', 'altitude_ref', 'altitude', 'timestamp', 'date']
    photo_df_response_cols = ['photo_id', 'json_response', 'ocr_text', 'extracted_words', 'translated_extracted_words', 'suggested_words', 'translated_suggested_words', 'image_quality', 'relevance_explanation', 'quality_explanation']
    photo_df = pd.merge(metadata_df[photo_df_metadata_cols], responses_df[photo_df_response_cols], on='photo_id')
    vocab_df = build_vocab_table(photo_df, quality_cutoff='low')

    vocab_df.to_csv(os.path.join(result_directory, 'vocab_table.csv'), index=False)
    photo_df.to_csv(os.path.join(result_directory, 'photo_table.csv'), index=False)
    build_anki_deck(vocab_df, result_directory)

if __name__ == "__main__":
    main()