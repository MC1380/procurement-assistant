
import pytest

from pydantic import ValidationError

from procurement_assistant.conversation_models import (
    MessageIntent,
    RequestExtraction,
)


def test_extract_new_motor_request():

    extraction = RequestExtraction(
        intent=MessageIntent.NEW_REQUEST,
        category_key="industrial_motor",
        quantity=3,
        attributes={
            "power": "5 kW",
        },
    )

    assert extraction.category_key == "industrial_motor"
    assert extraction.quantity == 3
    assert extraction.attributes["power"] == "5 kW"


def test_quantity_must_be_positive():

    with pytest.raises(ValidationError):
        RequestExtraction(
            intent=MessageIntent.NEW_REQUEST,
            quantity=0,
        )


def test_extraction_supports_partial_updates():

    extraction = RequestExtraction(
        intent=MessageIntent.UPDATE_REQUEST,
        quantity=5,
    )

    updates = extraction.model_dump(exclude_unset=True)

    assert updates["quantity"] == 5
    assert "category_key" not in updates
    assert "attributes" not in updates