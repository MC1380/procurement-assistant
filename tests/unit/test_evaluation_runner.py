import json

from procurement_assistant.conversation_models import (
    MessageIntent,
    RequestExtraction,
)
from procurement_assistant.services.evaluation_runner import run_evaluation


def test_run_evaluation(monkeypatch, tmp_path):
    dataset_path = tmp_path / "dataset.jsonl"

    case = {
        "id": "case_001",
        "user_message": "I need 5 industrial pumps.",
        "current_request": None,
        "expected": {
            "intent": "new_request",
            "category_key": "industrial_pump",
            "quantity": 5,
        },
    }

    dataset_path.write_text(
        json.dumps(case) + "\n",
        encoding="utf-8",
    )

    def fake_extract_request(
        user_message,
        current_request=None,
        model=None,
    ):
        return RequestExtraction(
            intent=MessageIntent.NEW_REQUEST,
            category_key="industrial_pump",
            quantity=5,
        )

    monkeypatch.setattr(
        "procurement_assistant.services.evaluation_runner.extract_request",
        fake_extract_request,
    )

    summary, case_results = run_evaluation(dataset_path)

    assert summary["total_cases"] == 1
    assert summary["field_accuracy"] == 1.0
    assert summary["intent_accuracy"] == 1.0

    assert case_results[0]["case_id"] == "case_001"
    assert case_results[0]["correct_fields"] == 3

def test_run_evaluation_continues_after_extraction_failure(
    monkeypatch,
    tmp_path,
):
    dataset_path = tmp_path / "dataset.jsonl"

    cases = [
        {
            "id": "case_001",
            "user_message": "I need 5 industrial pumps.",
            "current_request": None,
            "expected": {
                "intent": "new_request",
                "category_key": "industrial_pump",
                "quantity": 5,
            },
        },
        {
            "id": "case_002",
            "user_message": "I need 3 industrial motors.",
            "current_request": None,
            "expected": {
                "intent": "new_request",
                "category_key": "industrial_motor",
                "quantity": 3,
            },
        },
    ]

    dataset_path.write_text(
        "\n".join(json.dumps(case) for case in cases) + "\n",
        encoding="utf-8",
    )

    def fake_extract_request(
        user_message,
        current_request=None,
        model=None,
    ):
        if "motors" in user_message:
            raise RuntimeError("Simulated API failure")

        return RequestExtraction(
            intent=MessageIntent.NEW_REQUEST,
            category_key="industrial_pump",
            quantity=5,
        )

    monkeypatch.setattr(
        "procurement_assistant.services.evaluation_runner.extract_request",
        fake_extract_request,
    )

    summary, case_results = run_evaluation(dataset_path)

    assert summary["total_cases"] == 2
    assert summary["successful_extractions"] == 1
    assert summary["failed_extractions"] == 1
    assert summary["structured_output_success_rate"] == 0.5

    assert case_results[0]["structured_output_success"] is True
    assert case_results[1]["structured_output_success"] is False
    assert case_results[1]["error_type"] == "RuntimeError"

def test_run_evaluation_when_all_extractions_fail(
    monkeypatch,
    tmp_path,
):
    dataset_path = tmp_path / "dataset.jsonl"

    case = {
        "id": "case_001",
        "user_message": "I need 5 industrial pumps.",
        "current_request": None,
        "expected": {
            "intent": "new_request",
            "category_key": "industrial_pump",
            "quantity": 5,
        },
    }

    dataset_path.write_text(
        json.dumps(case) + "\n",
        encoding="utf-8",
    )

    def fake_extract_request(
        user_message,
        current_request=None,
        model=None,
    ):
        raise RuntimeError("Simulated API failure")

    monkeypatch.setattr(
        "procurement_assistant.services.evaluation_runner.extract_request",
        fake_extract_request,
    )

    summary, case_results = run_evaluation(dataset_path)

    assert summary["total_cases"] == 1
    assert summary["successful_extractions"] == 0
    assert summary["failed_extractions"] == 1
    assert summary["structured_output_success_rate"] == 0.0

    assert summary["field_accuracy"] is None
    assert summary["intent_accuracy"] is None
    assert summary["category_accuracy"] is None

    assert len(case_results) == 1
    assert case_results[0]["structured_output_success"] is False