import pytest

from procurement_assistant.evaluation.metrics_service import (
    aggregate_evaluation_results,
)


def test_aggregate_evaluation_results():

    case_results = [
        {
            "field_results": {
                "intent": {"correct": True},
                "category_key": {"correct": True},
                "quantity": {"correct": True},
            },
            "total_fields": 3,
            "correct_fields": 3,
        },
        {
            "field_results": {
                "intent": {"correct": True},
                "quantity": {"correct": False},
            },
            "total_fields": 2,
            "correct_fields": 1,
        },
        {
            "field_results": {
                "intent": {"correct": False},
                "category_key": {"correct": False},
            },
            "total_fields": 2,
            "correct_fields": 0,
        },
    ]

    result = aggregate_evaluation_results(case_results)

    assert result["total_cases"] == 3
    assert result["total_fields"] == 7
    assert result["correct_fields"] == 4

    assert result["field_accuracy"] == pytest.approx(4 / 7)
    assert result["intent_accuracy"] == pytest.approx(2 / 3)
    assert result["category_accuracy"] == pytest.approx(1 / 2)
    assert result["category_total"] == 2


def test_aggregate_empty_results_raises_error():

    with pytest.raises(ValueError, match="empty"):
        aggregate_evaluation_results([])