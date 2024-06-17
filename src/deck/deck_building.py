import os
import genanki
import pandas as pd

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

def build_anki_deck(df, out_dir):
    model_id = 1234567890
    deck_id = 9876543210

    model = genanki.Model(
        model_id,
        'Simple Model',
        fields=[
            {'name': 'VocabWord'},
            {'name': 'EnglishTranslation'}
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{VocabWord}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{EnglishTranslation}}'
            }
        ]
    )

    deck = genanki.Deck(
        deck_id,
        'German Vocabulary'
    )

    for _, row in df.iterrows():
        note = genanki.Note(
            model=model,
            fields=[row['vocab_word'], row['english_translation']]
        )
        deck.add_note(note)

    genanki.Package(deck).write_to_file(os.path.join(out_dir, "german_vocabulary.apkg"))