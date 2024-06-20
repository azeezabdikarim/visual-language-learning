# Visuals-to-Language Learning LLM

As a new German learner, I found myself constantly surrounded by unfamiliar words in my daily life. However, stopping to translate and note down every new word was impractical and disruptive. I needed a way to passively capture the German language I encountered and study it later.

This project automates that process. It turns everyday photos into personalized language learning materials:

1. I snap photos of German text throughout my day.
2. This program processes my photo collection.
3. AI extracts the text, understands the context, and generates curated vocabulary lists with translations.
4. It creates Anki flashcard decks for efficient studying.

Using OCR and advanced language models (LLaVA or GPT-4), this tool works with iPhone's HEIC photo format, seamlessly turning passive observations into active learning opportunities. It's like having a patient German tutor who prepares personalized lessons from everything I see.

Whether you're a beginner or advanced learner, this tool can transform your daily experiences into efficient language learning resources.

## Features

- Converts HEIC images to JPG format
- Extracts text from images using OCR
- Uses LLaVA or GPT-4 to analyze image content and generate relevant vocabulary
- Creates Anki flashcard decks for language learning
- Supports customizable language levels (e.g., A1, A2, B1, etc.)

## Requirements

- Python 3.7+
- Tesseract OCR
- Other dependencies listed in `requirements.txt`

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/azeezabdikarim/visual-language-learning.git
   cd visual-to-language-learning-llm
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Install Tesseract OCR and ensure it's in your system PATH.

4. Set up your API keys for OpenAI (if using GPT-4) and other necessary services.

## Usage

The main script expects a directory containing HEIC photos (the standard format for iPhone photos). To run the program:

```
python src/main.py --input_directory /path/to/your/photos
```

### Flags

- `--input_directory`: Specifies the directory containing input images
- `--use_openai`: Use OpenAI's GPT instead of LLaVA (default is False)

## Output

The program generates:

1. A CSV file with extracted and suggested vocabulary
2. A CSV file with detailed information about each processed photo
3. An Anki deck file (.apkg) for flashcard study

Output files are saved in a subdirectory within the input directory, named with the model used and current timestamp.

## How it works

1. Converts HEIC images to JPG format
2. Extracts text from images using OCR
3. Sends the extracted text and image to an AI model (LLaVA or GPT-4)
4. The AI model analyzes the content and generates:
   - Cleaned-up extracted German words
   - Suggested additional relevant German words and phrases
   - English translations for all words and phrases
   - Quality assessment of the OCR output
   - Relevance explanation for the suggested vocabulary
5. Processes the AI output to create vocabulary lists and Anki flashcards

## Customization

You can modify the prompt in `main.py` to adjust the language level, target language, or specific instructions for the AI model.

Here's the updated README with the additions you requested:

[Your existing README content]

## Sample Output

You can view sample outputs under the `sample_pics/result` directory. These samples demonstrate the kind of vocabulary lists and Anki decks the program generates from input images.

## Setup for OpenAI Integration

If you plan to use GPT-4, you need to set up your OpenAI credentials:

1. Create a file named `credentials.py` in the `src/llm/` directory.
2. In this file, define your OpenAI API key as follows:
   ```python
   openai_key = "your_openai_api_key_here"
   ```
3. Make sure to add `credentials.py` to your `.gitignore` file to avoid accidentally sharing your API key.

## Next Steps

Future developments for this project include:

1. Implementing quantitative tests to compare performance with other multimodal models, enabling objective evaluation of the tool's effectiveness.

2. Creating visualizations or network graphs to explore lexical themes between images. This could reveal interesting patterns in vocabulary acquisition across different contexts.

These enhancements aim to improve the tool's performance and provide deeper insights into the language learning process.

[Rest of your existing README content]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
