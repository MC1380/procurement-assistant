from procurement_assistant.domain.conversation_models import (
    MessageIntent,
    RequestExtraction,
)
from procurement_assistant.evaluation.models import ExpectedExtraction
from procurement_assistant.evaluation.metrics_service import (
    evaluate_extraction,
)


def test_evaluate_correct_extraction():
    expected = ExpectedExtraction(
        intent=MessageIntent.NEW_REQUEST,
        category_key="industrial_pump",
        quantity=5,
    )

    actual = RequestExtraction(
        intent=MessageIntent.NEW_REQUEST,
        category_key="industrial_pump",
        item_name="industrial pumps",
        quantity=5,
    )

    result = evaluate_extraction(expected, actual)

    assert result["total_fields"] == 3
    assert result["correct_fields"] == 3
    assert result["field_accuracy"] == 1.0


def test_evaluate_incorrect_extraction():
    expected = ExpectedExtraction(
        intent=MessageIntent.NEW_REQUEST,
        quantity=5,
    )

    actual = RequestExtraction(
        intent=MessageIntent.NEW_REQUEST,
        quantity=10,
    )

    result = evaluate_extraction(expected, actual)

    assert result["total_fields"] == 2
    assert result["correct_fields"] == 1
    assert result["field_accuracy"] == 0.5


def test_evaluate_product_attributes():
    expected = ExpectedExtraction(
        intent=MessageIntent.NEW_REQUEST,
        attributes={"voltage": "220V"},
    )

    actual = RequestExtraction(
        intent=MessageIntent.NEW_REQUEST,
        attributes={
            "voltage": "220V",
            "rpm": "1500",
        },
    )

    result = evaluate_extraction(expected, actual)

    assert result["total_fields"] == 2
    assert result["correct_fields"] == 2
    assert result["field_accuracy"] == 1.0