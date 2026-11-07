import pytest

from pydantic import ValidationError

from procurement_assistant.domain.conversation_models import (
    ConversationMessage,
    ConversationStatus,
    RequestDraft,
)


def test_request_draft_can_be_incomplete():
    draft = RequestDraft(
        category_key="industrial_motor",
        quantity=3,
    )

    assert draft.quantity == 3
    assert draft.sku is None
    assert draft.attributes == {}


def test_request_draft_rejects_invalid_quantity():
    with pytest.raises(ValidationError):
        RequestDraft(quantity=0)


def test_conversation_message_has_timestamp():
    message = ConversationMessage(
        role="user",
        content="I need three motors.",
    )

    assert message.role == "user"
    assert message.content == "I need three motors."
    assert message.created_at is not None


def test_conversation_status():
    assert (
        ConversationStatus.COLLECTING_INFORMATION.value
        == "collecting_information"
    )