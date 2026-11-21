
import pytest
from pydantic import ValidationError

from procurement_assistant.rag.evaluation.models import (
    ExpectedEvidence,
    RetrievalEvaluationCase,
    RetrievedChunk,
)


def test_valid_evaluation_case():
    case = RetrievalEvaluationCase(
        id="motor_voltage_001",
        query="What is the rated voltage of MOTOR-001?",
        expected_evidence=[
            ExpectedEvidence(
                document_id="DS-MOTOR-001",
                text="Rated Voltage | 400 V",
            )
        ],
    )

    assert case.id == "motor_voltage_001"
    assert len(case.expected_evidence) == 1


def test_evaluation_case_requires_evidence():
    with pytest.raises(ValidationError):
        RetrievalEvaluationCase(
            id="motor_voltage_001",
            query="What is the rated voltage of MOTOR-001?",
            expected_evidence=[],
        )


def test_retrieved_chunk_requires_positive_rank():
    with pytest.raises(ValidationError):
        RetrievedChunk(
            chunk_id="chunk-001",
            document_id="DS-MOTOR-001",
            text="Rated Voltage | 400 V",
            rank=0,
        )


def test_retrieved_chunk_allows_missing_score():
    chunk = RetrievedChunk(
        chunk_id="chunk-001",
        document_id="DS-MOTOR-001",
        text="Rated Voltage | 400 V",
        rank=1,
    )

    assert chunk.score is None
    assert chunk.rank == 1
