from procurement_assistant.rag.evaluation.models import (
    ResolvedGroundTruth,
    RetrievalEvaluationCase,
)
from procurement_assistant.rag.evaluation.normalization import (
    normalize_evidence_text,
)
from procurement_assistant.rag.ingestion.models import DocumentChunk


class GroundTruthResolver:
    """Resolves expected evidence into actual relevant chunk IDs."""

    def resolve(
        self,
        case: RetrievalEvaluationCase,
        chunks: list[DocumentChunk],
    ) -> ResolvedGroundTruth:
        relevant_chunk_ids: set[str] = set()

        for evidence in case.expected_evidence:
            normalized_evidence = normalize_evidence_text(
                evidence.text
            )

            matching_chunks = [
                chunk
                for chunk in chunks
                if chunk.metadata.document_id == evidence.document_id
                and normalized_evidence
                in normalize_evidence_text(chunk.content)
            ]

            if not matching_chunks:
                raise ValueError(
                    f"Expected evidence not found for case "
                    f"'{case.id}' in document "
                    f"'{evidence.document_id}': {evidence.text}"
                )

            relevant_chunk_ids.update(
                f"{chunk.metadata.document_id}:{chunk.chunk_index}"
                for chunk in matching_chunks
            )

        return ResolvedGroundTruth(
            case_id=case.id,
            relevant_chunk_ids=relevant_chunk_ids,
        )
