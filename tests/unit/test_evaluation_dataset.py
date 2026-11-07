import json

import pytest

from procurement_assistant.evaluation.dataset_service import (
    load_evaluation_dataset,
)


def test_load_valid_evaluation_dataset(tmp_path):
    dataset_path = tmp_path / "dataset.jsonl"

    case = {
        "id": "case_001",
        "user_message": "I need 5 industrial pumps.",
        "current_request": None,
        "expected": {
            "intent": "new_request",
            "category_key": "industrial_pump",
            "item_name": "industrial pumps",
            "quantity": 5,
        },
    }

    dataset_path.write_text(
        json.dumps(case) + "\n",
        encoding="utf-8",
    )

    cases = load_evaluation_dataset(dataset_path)

    assert len(cases) == 1
    assert cases[0].id == "case_001"
    assert cases[0].expected.quantity == 5


def test_load_invalid_jsonl_raises_error(tmp_path):
    dataset_path = tmp_path / "dataset.jsonl"
    dataset_path.write_text(
        '{"id": "case_001", invalid json}\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="line 1"):
        load_evaluation_dataset(dataset_path)


def test_load_empty_dataset_raises_error(tmp_path):
    dataset_path = tmp_path / "dataset.jsonl"
    dataset_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        load_evaluation_dataset(dataset_path)