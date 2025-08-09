import pytest

from aura_core.model.llm.summarizer import summarize_note, load_summarization_model


@pytest.fixture(scope="module")
def loaded_model():
    return load_summarization_model()


def test_summarize_normal_text(loaded_model):
    note = "The patient is a 45-year-old male with a history of hypertension. He presents with chest pain and shortness of breath. An EKG was performed which showed no acute changes."
    summary = summarize_note(note)

    assert summary != note
    assert len(summary) > 0
    assert "patient" in summary.lower()
    assert "hypertension" in summary.lower()


def test_summarize_empty_text(loaded_model):
    summary = summarize_note("")
    assert "No text provided" in summary


def test_summarize_short_text(loaded_model):
    note = "Patient feels fine."
    summary = summarize_note(note, min_length=5)
    assert isinstance(summary, str)
