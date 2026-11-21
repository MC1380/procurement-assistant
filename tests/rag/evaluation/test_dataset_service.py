import json

import pytest

from procurement_assistant.rag.evaluation.dataset_service import (
    load_retrieval_evaluation_dataset,
)


def test_load_valid_dataset(tmp_path):
    dataset_path = tmp_path / "dataset.jsonl"

    case = {
        "id": "motor_voltage_001",
        "query": "What is the rated voltage of MOTOR-001?",
        "expected_evidence": [
            {
                "document_id": "DS-MOTOR-001",
                "text": "Rated Voltage | 400 V",
            }
        ],
    }

    dataset_path.write_text(
        json.dumps(case),
        encoding="utf-8",
    )

    cases = load_retrieval_evaluation_dataset(dataset_path)

    assert len(cases) == 1
    assert cases[0].id == "motor_voltage_001"
    assert cases[0].expected_evidence[0].document_id == "DS-MOTOR-001"


def test_skip_empty_lines(tmp_path):
    dataset_path = tmp_path / "dataset.jsonl"

    case = {
        "id": "motor_voltage_001",
        "query": "What is the rated voltage of MOTOR-001?",
        "expected_evidence": [
            {
                "document_id": "DS-MOTOR-001",
                "text": "Rated Voltage | 400 V",
            }
        ],
    }

    dataset_path.write_text(
        "\n" + json.dumps(case) + "\n\n",
        encoding="utf-8",
    )

    cases = load_retrieval_evaluation_dataset(dataset_path)

    assert len(cases) == 1


def test_invalid_json_reports_line_number(tmp_path):
    dataset_path = tmp_path / "dataset.jsonl"

    valid_case = {
        "id": "motor_voltage_001",
        "query": "What is the rated voltage of MOTOR-001?",
        "expected_evidence": [
            {
                "document_id": "DS-MOTOR-001",
                "text": "Rated Voltage | 400 V",
            }
        ],
    }

    dataset_path.write_text(
        json.dumps(valid_case) + "\n"
        '{"id": invalid json}\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="line 2"):
        load_retrieval_evaluation_dataset(dataset_path)


def test_invalid_case_reports_line_number(tmp_path):
    dataset_path = tmp_path / "dataset.jsonl"

    invalid_case = {
        "id": "motor_voltage_001",
        "query": "What is the rated voltage?",
        "expected_evidence": [],
    }

    dataset_path.write_text(
        json.dumps(invalid_case),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="line 1"):
        load_retrieval_evaluation_dataset(dataset_path)


def test_empty_dataset_raises_error(tmp_path):
    dataset_path = tmp_path / "dataset.jsonl"
    dataset_path.write_text("\n  \n", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="Retrieval evaluation dataset is empty",
    ):
        load_retrieval_evaluation_dataset(dataset_path)