import pandas as pd
import json

def parse_json_response_llava(response, start="JSON_START:"):
    start_loc = response.find(start)
    json_response = response[start_loc + len(start):] if start_loc != -1 else response
    try:
        return json.loads(json_response)
    except json.JSONDecodeError:
        return {
            "extracted_words": [],
            "translated_extracted_words": [],
            "suggested_words": [],
            "translated_suggested_words": [],
            "image_quality": "unknown",
            "relevance_explanation": "Parsing error",
            "quality_explanation": "Parsing error",
            "json_response": response
        }

def build_table_from_responses(llm_response, ocr_text, metadata):
    responses_json = [parse_json_response_llava(res) for res in llm_response]
    metadata_df = pd.DataFrame(metadata).rename(columns={
        "Image DateTime": "image_datetime", 
        " GPS GPSLatitudeRef": "latitude_ref", 
        "GPS GPSLatitude": "latitude", 
        "GPS GPSLongitudeRef": "longitude_ref", 
        "GPS GPSLongitude": "longitude", 
        "GPS GPSAltitudeRef": "altitude_ref", 
        "GPS GPSAltitude": "altitude", 
        "GPS GPSTimeStamp": "timestamp", 
        "GPS GPSSpeedRef": "speed_ref", 
        "GPS GPSSpeed": "speed", 
        "GPS GPSDate": "date"
    })
    metadata_df['photo_id'] = range(len(metadata_df))
    responses_df = pd.DataFrame(responses_json)
    responses_df['photo_id'] = range(len(responses_df))
    responses_df['ocr_text'] = ocr_text
    responses_df['json_response'] = llm_response

    return responses_df, metadata_df

def build_vocab_table(photo_df, quality_cutoff='medium'):
    qualities_allowed = ['medium', 'high'] if quality_cutoff == 'medium' else ['high'] if quality_cutoff == 'high' else ['low', 'medium', 'high']

    extracted_words, translated_words, ex_words_photo_ids = [], [], []
    suggested_words, translated_suggested_words, sug_words_photo_ids = [], [], []

    for _, row in photo_df.iterrows():
        if row['image_quality'] in qualities_allowed:
            p_id = row['photo_id']
            e_words = row['extracted_words'] if isinstance(row['extracted_words'], list) else []
            te_words = row['translated_extracted_words'] if isinstance(row['translated_extracted_words'], list) else []
            s_words = row['suggested_words'] if isinstance(row['suggested_words'], list) else []
            ts_words = row['translated_suggested_words'] if isinstance(row['translated_suggested_words'], list) else []

            extracted_words.extend(e_words)
            translated_words.extend(te_words)
            ex_words_photo_ids.extend([p_id] * len(e_words))
            suggested_words.extend(s_words)
            translated_suggested_words.extend(ts_words)
            sug_words_photo_ids.extend([p_id] * len(s_words))
    n_e_terms = min(len(extracted_words), len(translated_words))
    n_s_terms = min(len(suggested_words), len(translated_suggested_words))
    ex_df = pd.DataFrame({
        'photo_id': ex_words_photo_ids[:n_e_terms], 
        'vocab_word': extracted_words[:n_e_terms], 
        'english_translation': translated_words[:n_e_terms], 
        'source': 'extracted'
    })
    sug_df = pd.DataFrame({
        'photo_id': sug_words_photo_ids[:n_s_terms], 
        'vocab_word': suggested_words[:n_s_terms], 
        'english_translation': translated_suggested_words[:n_s_terms], 
        'source': 'suggested'
    })
    vocab_df = pd.concat([ex_df, sug_df])
    return vocab_df