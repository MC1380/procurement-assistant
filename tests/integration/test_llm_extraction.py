import pytest

from procurement_assistant.domain.conversation_models import (
    MessageIntent,
    RequestDraft,
)
from procurement_assistant.services.llm_extraction_service import (
    extract_request,
)


@pytest.mark.parametrize(
    ("user_message", "expected_intent", "expected_quantity"),
    [
        (
            "I need 5 industrial pumps.",
            MessageIntent.NEW_REQUEST,
            5,
        ),
        (
            "Make it 10.",
            MessageIntent.UPDATE_REQUEST,
            10,
        ),
    ],
)
def test_extract_request_with_context(
    user_message,
    expected_intent,
    expected_quantity,
):
    current_request = (
        None
        if expected_intent == MessageIntent.NEW_REQUEST
        else RequestDraft(
            category_key="industrial_pump",
            item_name="industrial pump",
            quantity=5,
        )
    )

    extraction = extract_request(
        user_message=user_message,
        current_request=current_request,
    )

    assert extraction.intent == expected_intent
    assert extraction.quantity == expected_quantity

def test_extract_new_item_with_existing_request():
    current_request = RequestDraft(
        category_key="industrial_pump",
        item_name="industrial pump",
        quantity=5,
    )

    extraction = extract_request(
        user_message="I also need 3 electric motors.",
        current_request=current_request,
    )

    assert extraction.intent == MessageIntent.NEW_REQUEST
    assert extraction.category_key == "industrial_motor"
    assert extraction.quantity == 3