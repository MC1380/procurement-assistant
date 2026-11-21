
import json
from pathlib import Path

from procurement_assistant.rag.evaluation.models import (
    RetrievalEvaluationCase,
)


def load_retrieval_evaluation_dataset(
    dataset_path: Path,
) -> list[RetrievalEvaluationCase]:
    """Load and validate a RAG retrieval evaluation dataset."""

    cases = []

    with dataset_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                data = json.loads(line)
                case = RetrievalEvaluationCase.model_validate(data)

            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid retrieval evaluation data "
                    f"at line {line_number}: {exc}"
                ) from exc

            cases.append(case)

    if not cases:
        raise ValueError("Retrieval evaluation dataset is empty.")

    return cases
