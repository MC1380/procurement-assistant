import json
from pathlib import Path

from procurement_assistant.evaluation_models import EvaluationCase


def load_evaluation_dataset(
    dataset_path: Path,
) -> list[EvaluationCase]:
    """Load and validate evaluation cases from a JSONL file."""

    cases = []

    with dataset_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            try:
                data = json.loads(line)
                case = EvaluationCase.model_validate(data)
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(
                    f"Invalid evaluation data at line {line_number}: {exc}"
                ) from exc

            cases.append(case)

    if not cases:
        raise ValueError("Evaluation dataset is empty.")

    return cases