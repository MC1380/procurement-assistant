from pydantic import BaseModel, ConfigDict, Field


class ExpectedEvidence(BaseModel):
    """Evidence expected to be retrieved for an evaluation query."""

    model_config = ConfigDict(extra="forbid")

    document_id: str
    text: str = Field(min_length=1)


class RetrievalEvaluationCase(BaseModel):
    """A single query and its expected relevant evidence."""

    model_config = ConfigDict(extra="forbid")

    id: str
    query: str = Field(min_length=1)
    expected_evidence: list[ExpectedEvidence] = Field(min_length=1)


class RetrievedChunk(BaseModel):
    """A chunk returned by the retrieval system."""

    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    document_id: str
    text: str = Field(min_length=1)
    score: float | None = None
    rank: int = Field(gt=0)


class ResolvedGroundTruth(BaseModel):
    """Represents resolved relevant chunks for an evaluation case."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    relevant_chunk_ids: set[str] = Field(min_length=1)
