from transformers import pipeline

SUMMARIZATION_MODEL_NAME = "sshleifer/distilbart-cnn-12-6"

summarizer = None


def load_summarization_model():
    global summarizer
    if summarizer is None:
        print(f"Loading summarization model: {SUMMARIZATION_MODEL_NAME}...")
        summarizer = pipeline("summarization", model=SUMMARIZATION_MODEL_NAME)
        print("Summarization model loaded.")
    return summarizer


def summarize_note(text: str, max_length: int = 150, min_length: int = 30) -> str:
    if summarizer is None:
        load_summarization_model()

    if not text.strip():
        return "No text provided to summarize."

    try:
        summary_result = summarizer(
            text, max_length=max_length, min_length=min_length, do_sample=False
        )
        return summary_result[0]["summary_text"]
    except Exception as e:
        print(f"Error during summarization: {e}")
        return f"Error summarizing note: {e}"
