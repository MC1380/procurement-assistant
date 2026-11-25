import pytest

from procurement_assistant.rag.evaluation.ground_truth_resolver import (
    GroundTruthResolver,
)
from procurement_assistant.rag.evaluation.models import (
    RetrievalEvaluationCase,
    ExpectedEvidence,
)
from procurement_assistant.rag.ingestion.models import (
    DocumentChunk,
    DocumentMetadata,
)


def test_resolve_returns_matching_chunk_id():
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

    metadata = DocumentMetadata(
        document_id="DS-MOTOR-001",
        document_version="1.0",
        document_type="datasheet",
        knowledge_type="product_specific",
        category_key="industrial_motor",
        source_type="synthetic",
        verification_status="unverified",
        language="en",
        sku="MOTOR-001",
        product_model="SIM-IM-7K5-4P",
    )

    chunks = [
        DocumentChunk(
            content="Rated Voltage: 400 V",
            metadata=metadata,
            chunk_index=0,
        )
    ]

    resolver = GroundTruthResolver()

    result = resolver.resolve(case, chunks)

    assert result.case_id == "motor_voltage_001"
    assert result.relevant_chunk_ids == {
        chunks[0].chunk_id
    }


def test_resolve_returns_all_chunks_containing_same_evidence():
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

    metadata = DocumentMetadata(
        document_id="DS-MOTOR-001",
        document_version="1.0",
        document_type="datasheet",
        knowledge_type="product_specific",
        category_key="industrial_motor",
        source_type="synthetic",
        verification_status="unverified",
        language="en",
    )

    chunks = [
        DocumentChunk(
            content="Motor specifications. Rated Voltage: 400 V",
            metadata=metadata,
            chunk_index=0,
        ),
        DocumentChunk(
            content="Rated Voltage: 400 V. Frequency: 50 Hz",
            metadata=metadata,
            chunk_index=1,
        ),
    ]

    resolver = GroundTruthResolver()

    result = resolver.resolve(case, chunks)

    assert result.relevant_chunk_ids == {
    chunk.chunk_id for chunk in chunks
    }


def test_resolve_combines_chunks_for_multiple_evidence():
    case = RetrievalEvaluationCase(
        id="motor_specs_001",
        query="What are the voltage and frequency of MOTOR-001?",
        expected_evidence=[
            ExpectedEvidence(
                document_id="DS-MOTOR-001",
                text="Rated Voltage | 400 V",
            ),
            ExpectedEvidence(
                document_id="DS-MOTOR-001",
                text="Frequency | 50 Hz",
            ),
        ],
    )

    metadata = DocumentMetadata(
        document_id="DS-MOTOR-001",
        document_version="1.0",
        document_type="datasheet",
        knowledge_type="product_specific",
        category_key="industrial_motor",
        source_type="synthetic",
        verification_status="unverified",
        language="en",
    )

    chunks = [
        DocumentChunk(
            content="Rated Voltage: 400 V",
            metadata=metadata,
            chunk_index=0,
        ),
        DocumentChunk(
            content="Frequency: 50 Hz",
            metadata=metadata,
            chunk_index=1,
        ),
    ]

    resolver = GroundTruthResolver()

    result = resolver.resolve(case, chunks)

    assert result.relevant_chunk_ids == {
        chunk.chunk_id for chunk in chunks
    }


def test_resolve_deduplicates_chunk_ids_for_multiple_evidence():
    case = RetrievalEvaluationCase(
        id="motor_specs_001",
        query="What are the voltage and frequency of MOTOR-001?",
        expected_evidence=[
            ExpectedEvidence(
                document_id="DS-MOTOR-001",
                text="Rated Voltage | 400 V",
            ),
            ExpectedEvidence(
                document_id="DS-MOTOR-001",
                text="Frequency | 50 Hz",
            ),
        ],
    )

    metadata = DocumentMetadata(
        document_id="DS-MOTOR-001",
        document_version="1.0",
        document_type="datasheet",
        knowledge_type="product_specific",
        category_key="industrial_motor",
        source_type="synthetic",
        verification_status="unverified",
        language="en",
    )

    chunks = [
        DocumentChunk(
            content=(
                "Rated Voltage: 400 V. "
                "Frequency: 50 Hz"
            ),
            metadata=metadata,
            chunk_index=0,
        )
    ]

    resolver = GroundTruthResolver()

    result = resolver.resolve(case, chunks)

    assert result.relevant_chunk_ids == {
        chunks[0].chunk_id
    }


def test_resolve_does_not_match_evidence_from_wrong_document():
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

    wrong_metadata = DocumentMetadata(
        document_id="DS-MOTOR-002",
        document_version="1.0",
        document_type="datasheet",
        knowledge_type="product_specific",
        category_key="industrial_motor",
        source_type="synthetic",
        verification_status="unverified",
        language="en",
    )

    chunks = [
        DocumentChunk(
            content="Rated Voltage: 400 V",
            metadata=wrong_metadata,
            chunk_index=0,
        )
    ]

    resolver = GroundTruthResolver()

    with pytest.raises(ValueError, match="Expected evidence not found"):
        resolver.resolve(case, chunks)


def test_resolve_raises_error_when_one_evidence_is_missing():
    case = RetrievalEvaluationCase(
        id="motor_specs_001",
        query="What are the voltage and frequency of MOTOR-001?",
        expected_evidence=[
            ExpectedEvidence(
                document_id="DS-MOTOR-001",
                text="Rated Voltage | 400 V",
            ),
            ExpectedEvidence(
                document_id="DS-MOTOR-001",
                text="Frequency | 50 Hz",
            ),
        ],
    )

    metadata = DocumentMetadata(
        document_id="DS-MOTOR-001",
        document_version="1.0",
        document_type="datasheet",
        knowledge_type="product_specific",
        category_key="industrial_motor",
        source_type="synthetic",
        verification_status="unverified",
        language="en",
    )

    chunks = [
        DocumentChunk(
            content="Rated Voltage: 400 V",
            metadata=metadata,
            chunk_index=0,
        )
    ]

    resolver = GroundTruthResolver()

    with pytest.raises(
        ValueError,
        match="Expected evidence not found",
    ):
        resolver.resolve(case, chunks)