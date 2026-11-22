from procurement_assistant.rag.evaluation.normalization import (
    normalize_evidence_text,
)


def test_normalize_evidence_text_lowercases_text():
    result = normalize_evidence_text("Rated Voltage")

    assert result == "rated voltage"


def test_normalize_evidence_text_collapses_whitespace():
    result = normalize_evidence_text("Rated   Voltage   400 V")

    assert result == "rated voltage 400 v"


def test_normalize_evidence_text_normalizes_separators():
    result = normalize_evidence_text("Rated Voltage | 400 V")

    assert result == "rated voltage: 400 v"


def test_normalize_evidence_text_preserves_numeric_values():
    result = normalize_evidence_text("Estimated Current | 7.5 kW")

    assert result == "estimated current: 7.5 kw"