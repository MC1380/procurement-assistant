
import pytest
from pydantic import ValidationError

from procurement_assistant.rag.evaluation.models import (
    ExpectedEvidence,
    RetrievalEvaluationCase,
    RetrievedChunk,
    ResolvedGroundTruth,
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


def test_resolved_ground_truth_accepts_valid_data():
    ground_truth = ResolvedGroundTruth(
        case_id="motor_voltage_001",
        relevant_chunk_ids={"chunk_001", "chunk_002"},
    )

    assert ground_truth.case_id == "motor_voltage_001"
    assert ground_truth.relevant_chunk_ids == {"chunk_001", "chunk_002"}


def test_resolved_ground_truth_requires_case_id():
    with pytest.raises(ValidationError):
        ResolvedGroundTruth(
            relevant_chunk_ids={"chunk_001"},
        )


def test_resolved_ground_truth_requires_at_least_one_chunk():
    with pytest.raises(ValidationError):
        ResolvedGroundTruth(
            case_id="motor_voltage_001",
            relevant_chunk_ids=set(),
        )


def test_resolved_ground_truth_removes_duplicate_chunk_ids():
    ground_truth = ResolvedGroundTruth(
        case_id="motor_voltage_001",
        relevant_chunk_ids=["chunk_001", "chunk_001", "chunk_002"],
    )

    assert ground_truth.relevant_chunk_ids == {"chunk_001", "chunk_002"}